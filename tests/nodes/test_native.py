"""Exercise conversion and synchronization through actual isolated bpy workers."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.nodes import cli
from tools.nodes.runtimes import runtime_environment
from tools.nodes.sources import source_digest


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
    config = cli.configuration()
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
    cli.write_json(source / "collection.json", {"files": {
        "Probe.blend": {"source": "geometry"}, "ProbeImage.blend": {"source": "shader"}}})
    image = source / "shader/resources/0.png"
    native(config, directory,
           "import bpy\ni=bpy.data.images.new('Pixel',width=1,height=1)\n"
           "i.pixels[:]=(0.2,0.3,0.4,1.0)\ni.file_format='PNG'\n"
           f"i.filepath_raw={str(image)!r}\ni.save()\n")
    cli.write_json(image.parent / "images.json", [{"name": "Pixel", "file": "0.png", "colorspace": "sRGB", "alpha_mode": "STRAIGHT"}])
    workspace = directory / "workspace"
    cli.build_staged(config, [source], workspace, directory / "build")
    return config, directory, source, workspace


def case(prepared, tmp_path):
    config, _, source, workspace = prepared
    candidate = tmp_path / "sources/Probe"
    shutil.copytree(source, candidate)
    copied = tmp_path / "workspace"
    shutil.copytree(workspace, copied)
    return config, candidate, copied


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
    report = cli.run_worker(config, tmp_path, "inspect", version="b45", input=str(file))
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
    original = source_digest(source)
    output = tmp_path / "Published"
    cli.run_worker(config, tmp_path, "publish", version="b45", input=str(source), output=str(output))
    assert "Not freed memory blocks" not in capsys.readouterr().out
    assert source_digest(source) == original
    assert sorted(file.name for file in output.glob("*.blend")) == ["a_compositor.blend", "z_geometry.blend"]


def test_native_layout_and_no_change_sync_preserve_every_source_byte(prepared, tmp_path, monkeypatch, capsys):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "for n in bpy.data.node_groups['Probe'].nodes: n.location.x += 170\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    before = source_digest(source)
    cli.sync(source, workspace)
    assert source_digest(source) == before
    output = capsys.readouterr().out
    assert "Done: no logical changes" in output
    assert "Committing:" not in output


def test_native_b45_edit_survives_backend_dump_and_deduplicates_matching_b52(prepared, tmp_path, monkeypatch, capsys):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    for version in ("b45", "b52"):
        edit_value(config, tmp_path, workspace / version / "Probe/Probe.blend", 3.0, version)
    cli.sync(source, workspace)
    output = capsys.readouterr().out
    assert output.index("exporting") < output.index("merging versions") < output.index("Validating:") < output.index("Committing:") < output.index("Done: sources synchronized")
    assert source.as_posix() in output
    assert "3.0" in (source / "geometry/geometry/probe.py").read_text()
    assert not list(source.rglob("*.b52.py"))
    before = source_digest(source)
    cli.sync(source, workspace)
    assert source_digest(source) == before


def test_native_metadata_edit_and_new_asset_are_saved(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "g=bpy.data.node_groups['Probe']\ng.asset_data.author='Editor'\n"
           "g.asset_data.description='Changed'\ng.asset_data.tags.new('new')\n"
           "new=g.copy()\nnew.name='New Probe'\nnew.asset_mark()\nnew.use_fake_user=True\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    cli.sync(source, workspace)
    report = cli.run_worker(config, tmp_path, "inspect", version="b52", input=str(file))
    assert report["graphs"]["Probe"]["asset_metadata"]["author"] == "Editor"
    assert "New Probe" in report["graphs"]
    assert any("Editor" in p.read_text() for p in source.rglob("*.b52.py"))


def test_native_failure_preserves_source_and_baseline(prepared, tmp_path, monkeypatch, capsys):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    edit_value(config, tmp_path, file, 4.0, "b52")
    before = source_digest(source)
    baseline = (file.parent / ".nodes.json").read_bytes()
    def fail(*args, **kwargs):
        raise ValueError("Rejected candidate")
    monkeypatch.setattr(cli, "build_staged", fail)
    with pytest.raises(ValueError, match="Rejected candidate"):
        cli.sync(source, workspace)
    assert source_digest(source) == before
    assert (file.parent / ".nodes.json").read_bytes() == baseline
    output = capsys.readouterr().out
    assert "Validating:" in output
    assert "Done: sources synchronized" not in output


def test_native_resource_change_is_detected_and_shared_conflict_is_rejected(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/ProbeImage.blend"
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "bpy.data.images['Pixel'].colorspace_settings.name='Non-Color'\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    before = source_digest(source)
    with pytest.raises(ValueError, match="Shared resource conflict"):
        cli.sync(source, workspace)
    assert source_digest(source) == before



@pytest.mark.parametrize("actor", ["source", "workspace"])
def test_native_concurrent_changes_are_preserved_before_commit(prepared, tmp_path, monkeypatch, actor):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    edit_value(config, tmp_path, file, 7.0, "b52")
    original_source = (source / "geometry/geometry/probe.py").read_text()
    original_build = cli.build_staged
    marker = source / "geometry/geometry/probe.py" if actor == "source" else file.parent / "human-note.txt"
    def concurrent_change(*args, **kwargs):
        original_build(*args, **kwargs)
        marker.write_text(original_source + "\n# concurrent human change\n" if actor == "source" else "human change")
    monkeypatch.setattr(cli, "build_staged", concurrent_change)
    baseline = (file.parent / ".nodes.json").read_bytes()
    with pytest.raises(ValueError, match="changed during synchronization"):
        cli.sync(source, workspace)
    assert "human change" in marker.read_text()
    assert (file.parent / ".nodes.json").read_bytes() == baseline


def test_native_removal_and_stale_source_reject_without_rewriting_baseline(prepared, tmp_path, monkeypatch):
    config, source, workspace = case(prepared, tmp_path)
    monkeypatch.setattr(cli, "configuration", lambda *args, **kwargs: config)
    file = workspace / "b52/Probe/Probe.blend"
    baseline = (file.parent / ".nodes.json").read_bytes()
    native(config, tmp_path, f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(file)!r},load_ui=False)\n"
           "bpy.context.preferences.filepaths.save_version=0\n"
           "bpy.data.node_groups.remove(bpy.data.node_groups['Probe'])\n"
           f"bpy.ops.wm.save_as_mainfile(filepath={str(file)!r},check_existing=False)\n", "b52")
    before = source_digest(source)
    with pytest.raises(ValueError, match="Missing assets"):
        cli.sync(source, workspace)
    assert source_digest(source) == before
    assert (file.parent / ".nodes.json").read_bytes() == baseline
    with (source / "geometry/geometry/probe.py").open("a") as stream:
        stream.write("\n# changed source\n")
    with pytest.raises(ValueError, match="Source changed since workspace build"):
        cli.sync(source, workspace)
