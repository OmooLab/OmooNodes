"""Exercise conversion and synchronization through actual isolated bpy workers."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.nodes import importing, libraries
from tools.nodes.files import write_json
from tools.nodes.runtimes import configuration, run_worker
from tools.nodes.runtimes import runtime_environment


def source_files(source):
    return {path.relative_to(source): path.read_bytes() for path in source.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts}


def native(config, directory, code, version="builder"):
    script = directory / "edit.py"
    script.write_text(code, encoding="utf8")
    env = runtime_environment()
    for name in ("RESOURCES", "CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
        user = directory / "user" / name.lower()
        user.mkdir(parents=True, exist_ok=True)
        env["BLENDER_USER_" + name] = str(user)
    subprocess.run([config[version], str(script)], env=env, check=True, capture_output=True, text=True)


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    directory = tmp_path_factory.mktemp("native")
    config = configuration()
    source = directory / "sources" / "Probe"
    (source / "geometry/geometry").mkdir(parents=True)
    (source / "shader/resources").mkdir(parents=True)
    (source / "__init__.py").write_text("")
    for category in ("geometry", "shader"):
        (source / category / "__init__.py").write_text("")
        (source / category / category).mkdir(exist_ok=True)
        (source / category / category / "__init__.py").write_text("")
    (source / "geometry/geometry/probe.py").write_text(
        "from nodebpy import geometry as g\nfrom nodebpy.builder import CustomGeometryGroup\n"
        "class Probe(CustomGeometryGroup):\n    _name = 'Probe'\n    _tree_properties = {'is_modifier': True}\n"
        "    def _build_group(self, tree):\n        value = tree.inputs.float('Value', 1.0)\n"
        "        result = tree.outputs.float('Result')\n        value * 2.0 >> result\n"
        "ASSET = Probe\nASSET_METADATA = {'author': 'Tester', 'description': 'Original', 'tags': ['test']}\n")
    (source / "shader/shader/probe_image.py").write_text(
        "import bpy\nfrom nodebpy import shader as s\nfrom nodebpy.builder import CustomShaderGroup\n"
        "class ProbeImage(CustomShaderGroup):\n    _name = 'Probe Image'\n"
        "    def _build_group(self, tree):\n        color = tree.outputs.color('Color')\n"
        "        image = s.ImageTexture()\n        image.node.image = bpy.data.images['Pixel']\n        image.o.color >> color\nASSET = ProbeImage\nDATABLOCK_DEPENDENCIES = {'images': ('Pixel',)}\n")
    write_json(source / "collection.json", {"files": {
        "Probe.blend": {"source": "geometry"}, "ProbeImage.blend": {"source": "shader"}}})
    image = source / "shader/resources/0.png"
    native(config, directory,
           "import bpy\ni=bpy.data.images.new('Pixel',width=1,height=1)\n"
           "i.pixels[:]=(0.2,0.3,0.4,1.0)\ni.file_format='PNG'\n"
           f"i.filepath_raw={str(image)!r}\ni.save()\n")
    write_json(image.parent / "images.json", [{"name": "Pixel", "file": "0.png", "colorspace": "sRGB", "alpha_mode": "STRAIGHT"}])
    workspace = directory / "workspace"
    libraries.build_staged(config, [source], workspace, directory / "build")
    return config, directory, source, workspace


def case(prepared, tmp_path):
    config, _, source, workspace = prepared
    candidate = tmp_path / "sources/Probe"
    shutil.copytree(source, candidate)
    copied = tmp_path / "workspace"
    shutil.copytree(workspace, copied)
    return config, candidate, copied


def test_native_initial_import_preserves_assets_and_packed_resources(prepared, tmp_path, monkeypatch):
    config, _, _, workspace = prepared
    monkeypatch.setattr(importing, "configuration", lambda **kwargs: config)
    source = workspace / "b52/Probe"
    before = source_files(source)
    destination = tmp_path / "Imported"
    importing.dump_sources(source, destination)
    manifest = importing.module_classes(destination)
    assert {"Probe", "Probe Image"} <= manifest.keys()
    assert list(destination.rglob("resources/images.json"))
    assert not list(destination.rglob("*.b52.py"))
    assert source_files(source) == before


@pytest.mark.parametrize("remote", [False, True])
def test_native_publication_preserves_assets_in_standalone_libraries(prepared, tmp_path, remote):
    config, _, _, workspace = prepared
    source = workspace / "b52/Probe"
    output = tmp_path / "Published"
    before = source_files(source)
    run_worker(config, tmp_path, "publish", version="b52", input=str(source), output=str(output),
               self_contained=True, remote=remote)
    assert not (output / ".nodes.json").exists()
    assert (output / "_asset-library-meta.json").exists() == remote
    for path in source.glob("*.blend"):
        expected = run_worker(config, tmp_path, "inspect", version="b52", input=str(path))
        actual = run_worker(config, tmp_path, "inspect", version="b52", input=str(output / path.name))
        assert actual["graphs"] == expected["graphs"]
    assert source_files(source) == before


def edit_value(config, directory, file, value, version):
    native(config, directory,
           f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           f"bpy.data.node_groups['Probe'].interface.items_tree['Value'].default_value={value!r}\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", version)


def test_native_b45_compositor_inspection_releases_legacy_storage_without_rewriting_input(prepared, tmp_path, capsys):
    config, _, _, _ = prepared
    file = tmp_path / "compositor.blend"
    native(config, tmp_path,
           "import bpy\ntree=bpy.data.node_groups.new('Legacy Storage','CompositorNodeTree')\n"
           "tree.nodes.new('CompositorNodeAntiAliasing')\n"
           "tree.nodes.new('CompositorNodeAlphaOver')\ntree.asset_mark()\n"
           f"bpy.data.libraries.write({str(file)!r},{{tree}},fake_user=True)\n", "b45")
    original = file.read_bytes()
    report = run_worker(config, tmp_path, "inspect", version="b45", input=str(file))
    assert report["file_version"][:2] == [4, 5]
    assert "Legacy Storage" in report["graphs"]
    assert file.read_bytes() == original
    assert "Not freed memory blocks" not in capsys.readouterr().out
    assert not list(tmp_path.glob("*.cleanup.blend"))


def test_native_b45_publication_releases_compositor_storage_between_files(prepared, tmp_path, capsys):
    config, _, _, workspace = prepared
    source = tmp_path / "Source"
    source.mkdir()
    compositor = source / "a_compositor.blend"
    native(config, tmp_path,
           "import bpy\ntree=bpy.data.node_groups.new('Legacy Storage','CompositorNodeTree')\n"
           "tree.nodes.new('CompositorNodeAntiAliasing')\n"
           "tree.nodes.new('CompositorNodeAlphaOver')\ntree.asset_mark()\n"
           f"bpy.data.libraries.write({str(compositor)!r},{{tree}},fake_user=True)\n", "b45")
    shutil.copy2(workspace / "b45/Probe/Probe.blend", source / "z_geometry.blend")
    original = source_files(source)
    output = tmp_path / "Published"
    run_worker(config, tmp_path, "publish", version="b45", input=str(source), output=str(output))
    assert "Not freed memory blocks" not in capsys.readouterr().out
    assert source_files(source) == original
    assert sorted(file.name for file in output.glob("*.blend")) == ["a_compositor.blend", "z_geometry.blend"]


def test_native_hide_in_modifier_edit_is_shared_without_a_version_branch(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    shutil.rmtree(workspace / "b52")
    file = workspace / "b45/Probe/Probe.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "bpy.data.node_groups['Probe'].interface.items_tree['Value'].hide_in_modifier=True\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b45")
    libraries.sync(source, workspace)
    assert not list(source.rglob("*.b52.py"))
    assert "hide_in_modifier=True" in (source / "geometry/geometry/probe.py").read_text()


def test_native_metadata_edit_and_new_asset_are_saved(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "g=bpy.data.node_groups['Probe']\ng.asset_data.author='Editor'\n"
           "g.asset_data.description='Changed'\ng.asset_data.tags.new('new')\n"
           "new=g.copy()\nnew.name='New Probe'\nnew.asset_mark()\nnew.use_fake_user=True\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    libraries.sync(source, workspace, target="b52")
    report = run_worker(config, tmp_path, "inspect", version="b52", input=str(file))
    assert report["graphs"]["Probe"]["asset_metadata"]["author"] == "Editor"
    assert "New Probe" in report["graphs"]
    assert any("Editor" in p.read_text() for p in source.rglob("*.py"))
    assert not list(source.rglob("*.b52.py"))


def test_native_resource_change_overwrites_shared_resources(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/ProbeImage.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "bpy.data.images['Pixel'].colorspace_settings.name='Non-Color'\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    libraries.sync(source, workspace, target="b52")
    assert "Non-Color" in (source / "shader/resources/images.json").read_text()


def test_native_dev_overwrites_edited_blend_after_source_changes(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    config = {**config, "versions": {"b45": config["versions"]["b45"]}}
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b45/Probe/Probe.blend"
    edit_value(config, tmp_path, file, 9.0, "b45")
    script = source / "geometry/geometry/probe.py"
    script.write_text(script.read_text().replace("'Value', 1.0", "'Value', 3.0"))
    libraries.dev(source, workspace)
    report = run_worker(config, tmp_path, "inspect", version="b45", input=str(file))
    socket = next(item for item in report["graphs"]["Probe"]["interface"] if item["name"] == "Value")
    assert socket["default_value"] == 3.0
    assert not (file.parent / ".nodes.json").exists()


def test_native_sync_overwrites_source_without_a_baseline_and_rebuilds_both_targets(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b45/Probe/Probe.blend"
    edit_value(config, tmp_path, file, 7.0, "b45")
    script = source / "geometry/geometry/probe.py"
    script.write_text("This source was edited independently")
    stale = source / "geometry/geometry/stale.py"
    stale.write_text("Old generated asset")
    libraries.sync(source, workspace, target="b45")
    assert "7.0" in script.read_text()
    assert not stale.exists()
    assert not list(workspace.rglob(".nodes.json"))
    rebuilt = tmp_path / "rebuilt"
    libraries.build_staged(config, [source], rebuilt, tmp_path / "validation")
    for version in config["versions"]:
        report = run_worker(config, tmp_path, "inspect", version=version, input=str(rebuilt / version / "Probe/Probe.blend"))
        socket = next(item for item in report["graphs"]["Probe"]["interface"] if item["name"] == "Value")
        assert socket["default_value"] == 7.0


def test_native_sync_removes_sources_of_deleted_assets(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "bpy.data.node_groups.remove(bpy.data.node_groups['Probe'])\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    libraries.sync(source, workspace, target="b52")
    assert not list((source / "geometry").rglob("*.py"))
    assert (source / "shader/shader/probe_image.py").exists()
