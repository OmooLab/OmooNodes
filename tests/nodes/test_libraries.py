import json
from pathlib import Path

import pytest

from tools.nodes import libraries


@pytest.mark.parametrize(("markers", "target", "message"), [
    ([], None, "No development libraries found"),
    (["b45"], "b52", "No development libraries found"),
    (["b45", "b52"], None, "multiple versions exist"),
])
def test_sync_distinguishes_missing_workspaces_from_multiple_targets(tmp_path, monkeypatch, markers, target, message):
    source = tmp_path / "nodes/Library"
    source.mkdir(parents=True)
    workspace = tmp_path / "workspaces"
    workspace.mkdir()
    for version in markers:
        directory = workspace / version / "Library"
        directory.mkdir(parents=True)
        (directory / "Library.blend").write_bytes(b"blend")
    config = {"versions": {"b45": "4.5.14", "b52": "5.2.2"}}
    monkeypatch.setattr(libraries, "configuration", lambda *args, **kwargs: config)
    monkeypatch.setattr(libraries, "libraries", lambda path: [source])
    monkeypatch.setattr(libraries, "run_worker", lambda *args, **kwargs: pytest.fail("Invalid workspace ran a worker"))
    with pytest.raises(ValueError, match=message):
        libraries.sync(source, workspace, target)


def test_formal_build_publishes_dependency_closure_and_preserves_old_outputs_on_failure(tmp_path, monkeypatch):
    for name, dependencies in (("Owner", []), ("Extra", ["Owner"])):
        directory = tmp_path / "nodes" / name
        directory.mkdir(parents=True)
        (directory / "collection.json").write_text(json.dumps({"dependencies": dependencies}))
    config = {"cache": tmp_path / "cache", "versions": {"b52": "5.2.2"}, "settings": {}}
    monkeypatch.setattr(libraries, "configuration", lambda target, **kwargs: config)
    monkeypatch.setattr(libraries, "build_staged", lambda *args: None)
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

    monkeypatch.setattr(libraries, "run_worker", publish)
    output = tmp_path / "dist"
    libraries.build(tmp_path / "nodes/Extra", output, remote=True)
    assert calls == [("b52", "Owner", True, False), ("b52", "Extra", True, False)]
    (output / "b52/Extra/original").write_text("keep")
    fail = True
    with pytest.raises(ValueError, match="Bad remote listing"):
        libraries.build(tmp_path / "nodes/Extra", output, remote=True)
    assert (output / "b52/Extra/original").read_text() == "keep"
