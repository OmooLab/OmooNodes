"""Verify documentation commands and deployment boundaries."""

import subprocess
import tomllib
from pathlib import Path

import pytest

from tools import docs


@pytest.mark.parametrize("command", ["build", "dev", "deploy"])
def test_documentation_commands(monkeypatch, command):
    calls = []
    monkeypatch.setattr(
        subprocess, "run", lambda args, **kwargs: calls.append((args, kwargs))
    )

    docs.main([command])

    args, options = calls[0]
    assert options == {"cwd": docs.PROJECT_ROOT, "check": True}
    if command == "dev":
        assert args == ("mkdocs", "serve")
        return
    version = tomllib.loads(
        (docs.PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    assert args[:3] == ("mike", "deploy", "--update-aliases")
    assert args[-2:] == (".".join(version.split(".")[:2]) + ".x", "latest")
    assert ("--push" in args) == (command == "deploy")
    if command == "deploy":
        assert "--allow-empty" in args
        assert args[args.index("--remote") + 1] == "github"


@pytest.mark.parametrize("failed", [False, True])
def test_documentation_check_cleans_output_and_propagates_failure(monkeypatch, failed):
    outputs = []

    def run(args, **kwargs):
        assert args[:4] == ("mkdocs", "build", "--strict", "--site-dir")
        output = Path(args[4])
        assert output.is_dir()
        (output / "index.html").write_text("test", encoding="utf-8")
        outputs.append(output)
        if failed:
            raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(subprocess, "run", run)
    if failed:
        with pytest.raises(subprocess.CalledProcessError):
            docs.main(["test"])
    else:
        docs.main(["test"])

    assert len(outputs) == 1
    assert not outputs[0].exists()
