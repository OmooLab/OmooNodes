"""Prepare isolated bpy environments for the configured asset targets."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

TARGET_PYTHON = {"b45": "3.11", "b52": "3.13"}


def target_settings(target, version):
    """Resolve the Python ABI for a supported Blender release series."""
    if target not in TARGET_PYTHON:
        raise ValueError(f"Unsupported target: {target}")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Set tool.nodes.versions.{target} to an exact bpy version string")
    major, minor, _ = version.split(".")
    if target != f"b{major}{minor}":
        raise ValueError(f"Target {target} does not match bpy {version}")
    return {"python": TARGET_PYTHON[target], "bpy": version}

PROBE = (
    "import importlib.metadata as m,json,sys; "
    "packages={d.metadata['Name'].lower():d.version for d in m.distributions()}; "
    "print(json.dumps({'python':'.'.join(map(str,sys.version_info[:2])),"
    "'bpy':packages.get('bpy'),'nodebpy':packages.get('nodebpy')}))"
)


def runtime_environment():
    environment = os.environ.copy()
    for name in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
        environment.pop(name, None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def ensure_runtime(cache: Path, target: str, settings: dict[str, str]) -> str:
    """Install the exact bpy release once; a failed installation is retried."""
    environment_variables = runtime_environment()
    uv = shutil.which("uv")
    if uv is None:
        raise ValueError("Install uv before running nodes")
    environment = cache / "runtimes" / target / f"{settings['bpy']}-py{settings['python']}"
    if settings.get("nodebpy"):
        environment = environment.with_name(environment.name + "-nodebpy" + settings["nodebpy"])
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        environment.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([uv, "venv", "--no-project", "--python", settings["python"], str(environment)], check=True, env=environment_variables)
    info = json.loads(subprocess.check_output([str(python), "-c", PROBE], text=True, env=environment_variables))
    if info["python"] != settings["python"]:
        raise ValueError(f"Wrong Python in target runtime: {python}")
    if info["bpy"] != settings["bpy"] or info.get("nodebpy") != settings.get("nodebpy"):
        print(f"Preparing {target}: Python {settings['python']}, bpy {settings['bpy']}", flush=True)
        packages = [f"bpy=={settings['bpy']}"]
        if settings.get("nodebpy"):
            packages.append(f"nodebpy=={settings['nodebpy']}")
        subprocess.run([uv, "pip", "install", "--python", str(python), *packages], check=True, env=environment_variables)
    return str(python.resolve())
