import json
import subprocess
from pathlib import Path

import pytest

from omoonodes import runtimes


@pytest.mark.parametrize(("target", "version", "python"), [("b45", "4.5.14", "3.11"), ("b52", "5.2.2", "3.13")])
def test_target_version_selects_matching_python(target, version, python):
    assert runtimes.target_settings(target, version) == {"python": python, "bpy": version}


@pytest.mark.parametrize(("target", "version"), [
    ("b45", "5.2.2"), ("b52", "5.2"), ("b53", "5.3.0"),
    ("b45", {"python": "3.11", "bpy": "4.5.14"}),
])
def test_invalid_target_configuration_is_rejected(target, version):
    with pytest.raises(ValueError):
        runtimes.target_settings(target, version)


def test_missing_bpy_is_installed_and_matching_runtime_is_reused(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONHOME", "foreign-runtime")
    monkeypatch.setenv("PYTHONPATH", "foreign-packages")
    monkeypatch.setattr(runtimes.shutil, "which", lambda name: "uv")
    settings = {"python": "3.11", "bpy": "4.5.14"}
    calls = []

    def execute(command, check, env):
        assert "PYTHONHOME" not in env and "PYTHONPATH" not in env
        calls.append(command)
        if command[1] == "venv":
            directory = Path(command[-1]) / ("Scripts" if runtimes.os.name == "nt" else "bin")
            directory.mkdir(parents=True)
            (directory / ("python.exe" if runtimes.os.name == "nt" else "python")).touch()

    monkeypatch.setattr(runtimes.subprocess, "run", execute)
    info = {"python": "3.11", "bpy": None}
    monkeypatch.setattr(runtimes.subprocess, "check_output", lambda *a, **kw: json.dumps(info))
    python = runtimes.ensure_runtime(tmp_path, "b45", settings)
    assert calls[0][1:5] == ["venv", "--no-project", "--python", "3.11"]
    assert calls[1] == ["uv", "pip", "install", "--python", python, "bpy==4.5.14"]
    calls.clear()
    info["bpy"] = "4.5.14"
    assert runtimes.ensure_runtime(tmp_path, "b45", settings) == python
    assert not calls


def test_wrong_python_is_rejected_before_package_install(tmp_path, monkeypatch):
    monkeypatch.setattr(runtimes.shutil, "which", lambda name: "uv")
    settings = {"python": "3.13", "bpy": "5.2.2"}
    python = tmp_path / "runtimes/b52/5.2.2-py3.13" / (
        "Scripts/python.exe" if runtimes.os.name == "nt" else "bin/python")
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(runtimes.subprocess, "check_output", lambda *a, **kw: '{"python": "3.11", "bpy": "5.2.2"}')
    with pytest.raises(ValueError, match="Wrong Python"):
        runtimes.ensure_runtime(tmp_path, "b52", settings)


def test_runtime_keeps_virtual_environment_python_symlink(tmp_path, monkeypatch):
    settings = {"python": "3.11", "bpy": "4.5.14"}
    base = tmp_path / "base-python"
    base.touch()
    python = tmp_path / "runtimes/b45/4.5.14-py3.11" / (
        "Scripts/python.exe" if runtimes.os.name == "nt" else "bin/python")
    python.parent.mkdir(parents=True)
    try:
        python.symlink_to(base)
    except OSError:
        if runtimes.os.name == "nt":
            pytest.skip("Windows requires permission to create symbolic links")
        raise
    monkeypatch.setattr(runtimes.shutil, "which", lambda name: "uv")
    monkeypatch.setattr(runtimes.subprocess, "check_output", lambda *a, **kw: json.dumps(settings))
    assert runtimes.ensure_runtime(tmp_path, "b45", settings) == str(python)


@pytest.mark.parametrize("targets", ["", "targets = []\n"])
def test_targets_must_be_explicit_and_nonempty(tmp_path, monkeypatch, targets):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[tool.omoonodes]\nsource = "nodes"\n' + targets)
    monkeypatch.setattr(runtimes, "ensure_runtime", lambda *args: pytest.fail("Invalid configuration prepared a runtime"))
    with pytest.raises(ValueError, match="nonempty list"):
        runtimes.configuration()


def test_dev_defaults_to_lowest_target_and_versions_only_override_declared_targets(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "pyproject.toml"
    path.write_text('[tool.omoonodes]\ntargets = ["b52", "b45"]\n[tool.omoonodes.versions]\nb45 = "4.5.13"\n')
    prepared = {}
    monkeypatch.setattr(runtimes, "ensure_runtime", lambda cache, name, settings: prepared.setdefault(name, settings))
    config = runtimes.configuration(development=True)
    assert config["versions"] == {"b45": "4.5.13"}
    assert set(prepared) == {"b45"}
    assert set(runtimes.configuration()["versions"]) == {"b45", "b52"}
    path.write_text('[tool.omoonodes]\ntargets = ["b45"]\n[tool.omoonodes.versions]\nb52 = "5.2.2"\n')
    with pytest.raises(ValueError, match="only override declared"):
        runtimes.configuration()


@pytest.mark.parametrize("action", ["build", "dump", "inspect", "publish"])
def test_worker_uses_requested_runtime_and_reports_failure(tmp_path, monkeypatch, capsys, action):
    config = {"b52": "python-b52", "versions": {"b52": "5.2.2"}, "targets": {"b52": "5.2.2"}}
    calls = []

    def execute(command, env, **options):
        assert Path(env["BLENDER_USER_CONFIG"]).is_relative_to(tmp_path)
        assert env["PYTHONNOUSERSITE"] == "1"
        job = json.loads(Path(command[-1]).read_text())
        calls.append((command[0], job["expected_version"]))
        assert "backend" not in job
        Path(job["report"]).write_text('{"graphs": {}}')
        return subprocess.CompletedProcess(command, int(failed), stdout=(
            'Read blend: "D:/Projects/OmooNodes/.cache/nodes/example.blend"\n'
            '00:01.000  blend            | Read blend: "example.blend"\n'
            "Warning: File written by newer Blender binary (502.45), expect loss of data!\n"
            "Warning: Library file, loading empty scene\n"
            "warning: Another warning\n"
            "Info: Read library: 'example.blend'\n"
            "info: Saved file\n"
            "Worker diagnostic\n" + error))

    failed = False
    error = ""
    monkeypatch.setattr(runtimes.subprocess, "run", execute)
    runtimes.run_worker(config, tmp_path, action)
    runtimes.run_worker(config, tmp_path, "inspect", version="b52")
    assert calls == [("python-b52", "5.2.2"), ("python-b52", "5.2.2")]
    assert capsys.readouterr().out == "Worker diagnostic\n" * 2
    failed = True
    with pytest.raises(subprocess.CalledProcessError):
        runtimes.run_worker(config, tmp_path, action)
    assert capsys.readouterr().out == "Worker diagnostic\n"
    failed = False
    error = "Error: Cannot load library\n"
    with pytest.raises(RuntimeError, match="Cannot load library"):
        runtimes.run_worker(config, tmp_path, action)
    assert capsys.readouterr().out == "Worker diagnostic\n" + error
    error = "Error: Not freed memory blocks: 1, total unfreed memory 0.000008 MB\n"
    assert runtimes.run_worker(config, tmp_path, action) == {"graphs": {}}
    assert capsys.readouterr().out == "Worker diagnostic\n"
    failed = True
    with pytest.raises(subprocess.CalledProcessError):
        runtimes.run_worker(config, tmp_path, action)
    assert capsys.readouterr().out == "Worker diagnostic\n" + error
