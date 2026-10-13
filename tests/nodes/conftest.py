"""Run node-named pytest modules in each configured native Blender environment."""

import os
import importlib
import shutil
import subprocess
import sys
from functools import partial
from pathlib import Path

import pytest

from omoonodes.runtimes import configuration, runtime_environment
from omoonodes.sources import select_sources

ROOT = Path(__file__).resolve().parents[2]


def pytest_pycollect_makemodule(module_path, parent):
    if module_path.name.startswith("test_o_") and not os.environ.get("OMOO_TEST_SOURCES"):
        return NativeModule.from_parent(parent, path=module_path)


class NativeModule(pytest.File):
    def collect(self):
        targets = configuration(self.config.getoption("--node-target"), prepare_targets=False)["versions"]
        for target in targets:
            yield pytest.Function.from_parent(self, name=f"{self.path.stem}[{target}]",
                                              callobj=partial(run_node, path=self.path, target=target))


def run_node(native_targets, *, path, target):
    python, directory, environment = native_targets(target)
    name = "-".join(path.relative_to(ROOT / "tests/nodes").with_suffix("").parts)
    log = directory / f"{name}.log"
    with log.open("w", encoding="utf8") as output:
        try:
            result = subprocess.run([python, "-m", "pytest", str(path), "-q", "--tb=short",
                                     "--basetemp", str(directory / name)], cwd=ROOT, env=environment,
                                    stdout=output, stderr=subprocess.STDOUT, timeout=120)
        except subprocess.TimeoutExpired:
            pytest.fail(f"{target}/{path.stem} timed out after 120s; log: {log}", pytrace=False)
    assert result.returncode == 0, f"{target}: {log}\n{log.read_text(encoding='utf8')}"


@pytest.fixture(scope="session")
def native_targets(tmp_path_factory):
    prepared = {}

    def prepare(target):
        if target not in prepared:
            config = configuration(target)
            directory = tmp_path_factory.mktemp(f"nodes-{target}")
            environment = runtime_environment()
            environment["PYTHONIOENCODING"] = "utf-8"
            environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            # Reuse the existing test dependency in the cached native environment.
            subprocess.run([shutil.which("uv"), "pip", "install", "--python", config[target], "pytest>=8.3.2,<9"],
                           env=environment, check=True, timeout=120)
            select_sources(ROOT / "nodes", directory / "nodes", target)
            environment["OMOO_TEST_SOURCES"] = str(directory)
            for suffix in ("RESOURCES", "CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
                folder = directory / "user" / suffix.lower()
                folder.mkdir(parents=True)
                environment["BLENDER_USER_" + suffix] = str(folder)
            prepared[target] = config[target], directory, environment
        return prepared[target]

    return prepare


@pytest.fixture(autouse=True)
def node(request, tmp_path):
    folder = os.environ.get("OMOO_TEST_SOURCES")
    if not folder:
        yield
        return
    import bpy
    from omoonodes.publication import release_compositor_storage

    owner, kind, filename = request.path.relative_to(ROOT / "tests/nodes").parts
    category = {"geometry": "Geometry", "shader": "Shader", "compositor": "Compositing"}[kind]
    collection = "O_Extra" if owner == "O_Extra" else f"{owner}_{category}Nodes"
    if folder not in sys.path:
        sys.path.insert(0, folder)
    module = importlib.import_module(f"nodes.{owner}.{collection}.{kind}.{Path(filename).stem.removeprefix('test_')}")
    assert Path(module.__file__).is_relative_to(folder), f"Node did not load selected target sources: {module.__file__}"
    assert not getattr(module, "DISABLED", False), f"Tested node is disabled: {module.__name__}"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    module.ASSET.create_group()
    yield
    release_compositor_storage(bpy, tmp_path / "cleanup.blend")
