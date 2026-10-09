import ast
import json
import subprocess
from pathlib import Path

import pytest

from tools.nodes.cli import replace_directories, rewrite_foreign_modules
from tools.nodes import cli


def test_foreign_shared_class_is_imported_from_owner_without_forwarding_file(tmp_path):
    root = tmp_path / "sources"
    shared = root / "geometry/_shared"
    shared.mkdir(parents=True)
    (shared / "helper.py").write_text("class Helper:\n    _name = 'Public Helper'\n", encoding="utf8")
    asset = root / "geometry/asset.py"
    asset.write_text("from ._shared.helper import Helper\nclass Asset:\n    _name = 'Asset'\n", encoding="utf8")
    rewrite_foreign_modules(root, {"Public Helper": {"module": "nodes.Owner.geometry.helper", "class": "Helper"}})
    assert not (shared / "helper.py").exists()
    statements = ast.parse(asset.read_text()).body
    assert isinstance(statements[0], ast.ImportFrom)
    assert statements[0].module == "nodes.Owner.geometry.helper"
    assert statements[0].names[0].asname == "Helper"
    assert statements[1].name == "Asset"


def test_directory_transaction_restores_both_libraries_on_failure(tmp_path, monkeypatch):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    target = tmp_path / "libraries/A"
    target.mkdir(parents=True)
    (target / "original").write_text("keep")
    (prepared / "replacement").write_text("new")
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        replace_directories([(prepared, target), (missing, tmp_path / "libraries/B")])
    assert (target / "original").read_text() == "keep"
    assert not (target / "replacement").exists()
    assert not target.with_name("A.nodes-backup").exists()


@pytest.mark.parametrize(("sdk", "builder"), [("520.34.1", "5.2.2"), ("530.0.0", "5.3.0")])
def test_configuration_keeps_targets_independent_of_builder(tmp_path, monkeypatch, sdk, builder):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        f'[tool.nodes.backend]\npython = "3.13"\nnodebpy = "{sdk}"\nbpy = "{builder}"\n'
        '[tool.nodes.targets]\nb45 = "4.5.14"\nb52 = "5.2.2"\n')

    prepared = []

    def prepare(cache, target, settings):
        prepared.append((target, settings))
        return "python-" + target

    monkeypatch.setattr(cli, "ensure_runtime", prepare)
    config = cli.configuration()
    assert config["builder_version"] == builder
    assert config["b45"] == "python-b45"
    assert config["b52"] == "python-b52"
    assert [target for target, _ in prepared] == ["backend", "b45", "b52"]
    assert prepared[0][1]["nodebpy"] == sdk


@pytest.mark.parametrize("overrides", [{}, {"nodebpy": "530.0.0", "bpy": "5.3.0"}, {"nodebpy": "520.34.2"}])
def test_backend_defaults_can_be_omitted_or_partially_overridden(tmp_path, monkeypatch, overrides):
    monkeypatch.chdir(tmp_path)
    backend = "[tool.nodes.backend]\n" + "".join(f'{key} = "{value}"\n' for key, value in overrides.items()) if overrides else ""
    (tmp_path / "pyproject.toml").write_text(backend + '[tool.nodes.targets]\nb45 = "4.5.14"\n')
    prepared = {}

    def prepare(cache, name, settings):
        prepared[name] = settings
        return "python-" + name

    monkeypatch.setattr(cli, "ensure_runtime", prepare)
    config = cli.configuration()
    assert prepared["backend"] == {"python": "3.13", "nodebpy": "520.34.1", "bpy": "5.2.2", **overrides}
    assert config["builder_version"] == prepared["backend"]["bpy"]
    assert config["versions"] == {"b45": "4.5.14"}
    assert set(prepared) == {"backend", "b45"}


@pytest.mark.parametrize("targets", ["", "[tool.nodes.targets]\n"])
def test_targets_must_be_explicit_and_nonempty(tmp_path, monkeypatch, targets):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[tool.nodes]\nsource = "nodes"\n' + targets)
    monkeypatch.setattr(cli, "ensure_runtime", lambda *args: pytest.fail("Invalid configuration prepared a runtime"))
    with pytest.raises(ValueError, match="Declare at least one target"):
        cli.configuration()


def test_worker_receives_expected_version_before_processing_assets(tmp_path, monkeypatch):
    config = {"builder": "python-builder", "builder_version": "5.3.0",
              "b52": "python-b52", "versions": {"b52": "5.2.2"}}
    calls = []

    def execute(command, env, **options):
        assert Path(env["BLENDER_USER_CONFIG"]).is_relative_to(tmp_path)
        assert env["PYTHONNOUSERSITE"] == "1"
        job = json.loads(Path(command[-1]).read_text())
        calls.append((command[0], job["expected_version"]))
        assert "backend" not in job
        Path(job["report"]).write_text('{"graphs": {}}')
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(cli.subprocess, "run", execute)
    cli.run_worker(config, tmp_path, "build")
    cli.run_worker(config, tmp_path, "inspect", version="b52")
    assert calls == [("python-builder", "5.3.0"), ("python-b52", "5.2.2")]


@pytest.mark.parametrize("returncode", [0, 1])
def test_worker_filters_only_normal_library_messages_and_keeps_failure_diagnostics(tmp_path, monkeypatch, capsys, returncode):
    output = ('Warning: Library file, loading empty scene\n'
              '00:00.359  blend            | Read blend: "library.blend"\n'
              "Info: Read library: 'Owner.blend'\n"
              'Read blend: "library.blend"\n'
              'Error: Not freed memory blocks: 2, total unfreed memory 0.000019 MB\n'
              'Warning: File written by newer Blender binary (502.45), expect loss of data!\n'
              'Warning: Missing external library\n')

    def execute(command, **options):
        job = json.loads(Path(command[-1]).read_text())
        Path(job["report"]).write_text('{}')
        return subprocess.CompletedProcess(command, returncode, stdout=output)

    monkeypatch.setattr(cli.subprocess, "run", execute)
    config = {"builder": "python", "builder_version": "5.2.2"}
    if returncode:
        with pytest.raises(subprocess.CalledProcessError):
            cli.run_worker(config, tmp_path, "build")
    else:
        cli.run_worker(config, tmp_path, "build")
    displayed = capsys.readouterr().out
    assert "Warning: Missing external library" in displayed
    assert "Not freed memory blocks" in displayed
    assert "expect loss of data" in displayed
    assert ("loading empty scene" in displayed) == bool(returncode)
    assert ("Read blend:" in displayed) == bool(returncode)
    assert ("Read library:" in displayed) == bool(returncode)


@pytest.mark.parametrize(("save", "file_version", "returncode", "visible"), [
    (True, "502.45", 0, False),
    (False, "502.45", 0, True),
    (True, "503.1", 0, True),
    (True, "502.45", 1, True),
])
def test_only_expected_backend_conversion_warning_is_hidden(tmp_path, monkeypatch, capsys, save, file_version, returncode, visible):
    def execute(command, **options):
        job = cli.read_json(command[-1])
        cli.write_json(job["report"], {})
        return subprocess.CompletedProcess(command, returncode, stdout=
            f"Warning: File written by newer Blender binary ({file_version}), expect loss of data!\n")

    monkeypatch.setattr(cli.subprocess, "run", execute)
    config = {"builder_version": "5.2.2", "b45": "python", "versions": {"b45": "4.5.14"}}
    if returncode:
        with pytest.raises(subprocess.CalledProcessError):
            cli.run_worker(config, tmp_path, "inspect", version="b45", save=save)
    else:
        cli.run_worker(config, tmp_path, "inspect", version="b45", save=save)
    assert ("expect loss of data" in capsys.readouterr().out) == visible


@pytest.mark.parametrize("fail", [False, True])
def test_dev_reports_final_dependency_paths_only_after_success(tmp_path, monkeypatch, capsys, fail):
    sources = [tmp_path / "nodes" / name for name in ("Owner", "Extra")]
    config = {"cache": tmp_path / "cache", "versions": {"b52": "5.2.2"}}
    monkeypatch.setattr(cli, "configuration", lambda target: config)
    monkeypatch.setattr(cli, "libraries", lambda source: sources)
    monkeypatch.setattr(cli, "verify_workspace", lambda *args: None)

    def stage(config, closure, destination, temporary):
        if fail:
            raise ValueError("Invalid nodes")
        for source in closure:
            (destination / "b52" / source.name).mkdir(parents=True)

    monkeypatch.setattr(cli, "build_staged", stage)
    workspace = tmp_path / "workspaces"
    if fail:
        with pytest.raises(ValueError, match="Invalid nodes"):
            cli.dev(sources[-1], workspace)
    else:
        cli.dev(sources[-1], workspace)
    displayed = capsys.readouterr().out
    assert "Owner -> Extra" in displayed
    assert ("Done: development libraries exported" in displayed) == (not fail)
    for source in sources:
        assert ((workspace / "b52" / source.name).as_posix() in displayed) == (not fail)


def test_build_saves_and_reloads_both_targets_in_their_own_runtime(tmp_path, monkeypatch, capsys):
    source = tmp_path / "Source"
    source.mkdir()
    (source / "asset.py").write_text("ASSET = None")
    (source / "collection.json").write_text(json.dumps({"files": {"assets.blend": {"source": "."}}}))
    calls = []

    def run(config, temporary, action, version=None, **options):
        calls.append((action, version, options.get("save", False)))
        return {"graphs": {}, "file_version": [4, 5, 0] if version == "b45" else [5, 2, 0]}

    monkeypatch.setattr(cli, "run_worker", run)
    cli.build_staged({"versions": {"b45": "4.5.14", "b52": "5.2.2"}}, [source], tmp_path / "workspaces", tmp_path / "temporary")
    assert calls == [("build", None, False), ("inspect", "b45", True), ("inspect", "b45", False),
                     ("build", None, False), ("inspect", "b52", True), ("inspect", "b52", False)]
    displayed = capsys.readouterr().out
    assert displayed.count("assets.blend: build -> save -> check") == 2
    assert "Building nodes and arranging layout" not in displayed


def test_build_rejects_a_file_that_remains_at_backend_version(tmp_path, monkeypatch):
    source = tmp_path / "Source"
    source.mkdir()
    (source / "asset.py").write_text("ASSET = None")
    cli.write_json(source / "collection.json", {"files": {"assets.blend": {"source": "."}}})
    monkeypatch.setattr(cli, "run_worker", lambda *args, **kwargs: {"graphs": {}, "file_version": [5, 2, 45]})
    with pytest.raises(ValueError, match="Unexpected saved file version"):
        cli.build_staged({"versions": {"b45": "4.5.14"}}, [source], tmp_path / "out", tmp_path / "temporary")



def test_commands_are_three_and_build_modes_are_simple():
    parser = cli.parser()
    local = parser.parse_args(["build"])
    assert not local.remote and not local.self_contained
    independent = parser.parse_args(["build", "--self-contained"])
    assert independent.self_contained and not independent.remote
    combined = parser.parse_args(["build", "--remote", "--self-contained"])
    assert combined.remote and combined.self_contained
    imported = parser.parse_args(["dump", "library.blend", "-o", "nodes/Library"])
    assert not hasattr(imported, "target")
    for command in (["sync"], ["build", "--zip"], ["dump", "a.blend", "-o", "nodes/A", "--target", "b52"]):
        with pytest.raises(SystemExit):
            parser.parse_args(command)


def test_formal_build_publishes_dependency_closure_and_preserves_old_outputs_on_failure(tmp_path, monkeypatch):
    for name, dependencies in (("Owner", []), ("Extra", ["Owner"])):
        directory = tmp_path / "nodes" / name
        directory.mkdir(parents=True)
        (directory / "collection.json").write_text(json.dumps({"dependencies": dependencies}))
    config = {"cache": tmp_path / "cache", "versions": {"b52": "5.2.2"}, "settings": {}}
    monkeypatch.setattr(cli, "configuration", lambda target: config)
    monkeypatch.setattr(cli, "build_staged", lambda *args: None)
    calls = []
    fail = False

    def publish(config, temporary, action, version=None, **options):
        nonlocal fail
        calls.append((version, Path(options["input"]).name, options["remote"], options["self_contained"]))
        destination = Path(options["output"])
        destination.mkdir(parents=True)
        (destination / "new").write_text("new")
        if fail:
            raise ValueError("Bad remote listing")

    monkeypatch.setattr(cli, "run_worker", publish)
    output = tmp_path / "dist"
    cli.build(tmp_path / "nodes/Extra", output, remote=True)
    assert calls == [("b52", "Owner", True, False), ("b52", "Extra", True, False)]
    (output / "b52/Extra/original").write_text("keep")
    fail = True
    with pytest.raises(ValueError, match="Bad remote listing"):
        cli.build(tmp_path / "nodes/Extra", output, remote=True)
    assert (output / "b52/Extra/original").read_text() == "keep"



def test_foreign_rewrite_keeps_untouched_comments_and_format(tmp_path):
    source = tmp_path / "asset.py"
    original = "# Authored comment\nclass Asset:\n    _name = \"Asset\"\n"
    source.write_text(original)
    rewrite_foreign_modules(tmp_path, {})
    assert source.read_text() == original
