import json
from pathlib import Path

import pytest

from tools.nodes import runtimes


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
