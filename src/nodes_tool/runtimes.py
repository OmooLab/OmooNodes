"""Prepare isolated bpy environments for the configured asset targets."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

from .files import read_json, write_json

WORKER = Path(__file__).with_name("worker.py")
TARGETS = {
    "b45": {"python": "3.11", "bpy": "4.5.14"},
    "b52": {"python": "3.13", "bpy": "5.2.2"},
}


def target_settings(target, version):
    """Resolve the Python ABI for a supported Blender release series."""
    if target not in TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Set tool.nodes.versions.{target} to an exact bpy version string")
    major, minor, _ = version.split(".")
    if target != f"b{major}{minor}":
        raise ValueError(f"Target {target} does not match bpy {version}")
    return {"python": TARGETS[target]["python"], "bpy": version}

PROBE = (
    "import importlib.metadata as m,json,sys; "
    "packages={d.metadata['Name'].lower():d.version for d in m.distributions()}; "
    "print(json.dumps({'python':'.'.join(map(str,sys.version_info[:2])),"
    "'bpy':packages.get('bpy')}))"
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
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        environment.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([uv, "venv", "--no-project", "--python", settings["python"], str(environment)], check=True, env=environment_variables)
    info = json.loads(subprocess.check_output([str(python), "-c", PROBE], text=True, env=environment_variables))
    if info["python"] != settings["python"]:
        raise ValueError(f"Wrong Python in target runtime: {python}")
    if info["bpy"] != settings["bpy"]:
        print(f"Installing {target} ...", flush=True)
        packages = [f"bpy=={settings['bpy']}"]
        subprocess.run([uv, "pip", "install", "--python", str(python), *packages], check=True, env=environment_variables)
    return str(python.resolve())


def project_root():
    for directory in (Path.cwd(), *Path.cwd().parents):
        path = directory / "pyproject.toml"
        if path.is_file() and tomllib.loads(path.read_text(encoding="utf8")).get("tool", {}).get("nodes"):
            return directory
    raise ValueError("No [tool.nodes] project configuration found")


def configuration(target=None, prepare_targets=True, development=False):
    root = project_root()
    settings = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf8"))["tool"]["nodes"]
    declared = settings.get("targets")
    if (not isinstance(declared, list) or not declared
            or any(not isinstance(label, str) or label not in TARGETS for label in declared)
            or len(set(declared)) != len(declared)):
        raise ValueError('Set tool.nodes.targets to a nonempty list of supported targets: ["b45", "b52"]')
    overrides = settings.get("versions", {})
    if not isinstance(overrides, dict) or set(overrides) - set(declared):
        raise ValueError("tool.nodes.versions may only override declared targets")
    targets = {label: target_settings(label, overrides.get(label, TARGETS[label]["bpy"])) for label in declared}
    base_target = min(targets, key=lambda label: tuple(map(int, targets[label]["bpy"].split("."))))
    if target and target not in targets:
        raise ValueError(f"Unknown target: {target}")
    chosen = [target or base_target] if target or development else list(targets)
    cache = root / ".cache/nodes"
    data = {"cache": cache, "settings": settings,
            "targets": {label: data["bpy"] for label, data in targets.items()},
            "versions": {label: targets[label]["bpy"] for label in chosen}}
    for label in chosen if prepare_targets else ():
        data[label] = ensure_runtime(cache, label, targets[label])
    return data


def run_worker(config, temporary, action, version=None, **options):
    version = version or next(iter(config["versions"]))
    runtime = version
    if runtime not in config:
        config[runtime] = ensure_runtime(config["cache"], runtime, target_settings(runtime, config["targets"][runtime]))
    temporary.mkdir(parents=True, exist_ok=True)
    job = temporary / f"{action}-{runtime}.json"
    report = job.with_suffix(".report.json")
    expected = config["targets"][version]
    write_json(job, {"action": action, "report": str(report),
                     "expected_version": expected, **options})
    environment = runtime_environment()
    user = temporary / "blender-user"
    for suffix in ("RESOURCES", "CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
        path = user / suffix.lower()
        path.mkdir(parents=True, exist_ok=True)
        environment["BLENDER_USER_" + suffix] = str(path)
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([config[runtime], str(WORKER), "--", str(job)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding="utf8", errors="replace", env=environment)
    errors = []
    for line in (result.stdout or "").splitlines():
        message = re.sub(r"^\d+:\d+\.\d+\s+[\w.]+\s+\|\s*", "", line.lstrip()).lower()
        if message.startswith(("info:", "warning:", "info ", "warning ", "warn (", 'read blend: "')):
            continue
        # Blender can report leaked legacy storage even after a successful job.
        if result.returncode == 0 and re.fullmatch(
                r"error: not freed memory blocks: \d+, total unfreed memory [\d.]+ mb", message):
            continue
        print(line, flush=True)
        if message.startswith(("error:", "error ")):
            errors.append(line)
    result.check_returncode()
    if errors:
        raise RuntimeError("\n".join(errors))
    return read_json(report)
