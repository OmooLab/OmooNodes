"""Import complete asset libraries into native Python modules."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .console import done, progress
from .files import replace_directories, write_json
from .runtimes import configuration, run_worker
from .sources import definitions


def dump_sources(source, destination, target=None):
    if destination.exists():
        raise ValueError(f"Source already exists: {destination}; use dev --sync")
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("Input and source output must not overlap")
    with progress("Checking runtimes"):
        config = configuration(target, development=True)
    version = next(iter(config["versions"]))
    config["cache"].mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=config["cache"]) as directory:
        temporary = Path(directory)
        staging = temporary / "nodes"
        staging.mkdir()
        single_collection = source.is_file() or any(source.glob("*.blend"))
        files = set(source.rglob("*.blend") if source.is_dir() else [source])
        reports = {}
        owners = {}
        visiting = set()

        def visit(path):
            path = path.resolve()
            if path in reports:
                return
            if path in visiting:
                raise ValueError(f"Recursive file dependency: {path}")
            if not path.is_file() or path.suffix != ".blend":
                raise ValueError(f"Missing blend source: {path}")
            visiting.add(path)
            primary = path == source if source.is_file() else path.parent == source
            collection = destination.name if single_collection and primary else path.parent.name
            module_root = staging / collection / path.stem
            if module_root.exists():
                raise ValueError(f"Duplicate source file: {collection}/{path.name}")
            module_root.parent.mkdir(exist_ok=True)
            with progress(path.name, indent="  "):
                report = run_worker(config, temporary, "dump", version=version, input=str(path), output=str(module_root))
                if not report["graphs"]:
                    raise ValueError(f"No local node assets: {path}")
            for owner in set(report["owners"].values()):
                visit(Path(owner))
            if report["owners"]:
                run_worker(config, temporary, "dump", version=version, input=str(path), output=str(module_root),
                           source_root=str(staging))
            for kind, name in definitions(module_root):
                if kind != "NODETREE":
                    continue
                if name in owners and owners[name]["file_path"] != path:
                    raise ValueError(f"Ambiguous node ownership: {name}")
                owners[name] = {"library": collection, "file": path.name, "file_path": path}
            reports[path] = (collection, module_root, report)
            visiting.remove(path)

        for path in sorted(files):
            visit(path)
        if not reports:
            raise ValueError(f"No blend files: {source}")
        with progress("Checking sources"):
            manifests = {}
            for path, (collection, module_root, report) in reports.items():
                imports = report["owners"]
                manifest = manifests.setdefault(collection, {"dependencies": [], "files": {}})
                dependencies = {owners[name]["library"] for name in imports} - {collection}
                manifest["dependencies"] = sorted(set(manifest["dependencies"]) | dependencies)
                manifest["files"][path.name] = {
                    "source": path.stem,
                    "links": {name: {"library": owners[name]["library"], "file": owners[name]["file"]} for name in imports},
                }
                output = temporary / "validation" / collection / path.name
                output.parent.mkdir(parents=True, exist_ok=True)
                links = {name: str(temporary / "validation" / owners[name]["library"] / owners[name]["file"]) for name in imports}
                run_worker(config, temporary, "build", version=version, input=str(module_root), output=str(output),
                           links=links, source_root=str(staging))
                actual = run_worker(config, temporary, "inspect", version=version, input=str(output))
                if report["graphs"] != actual["graphs"]:
                    raise ValueError(f"Logical roundtrip failed: {path.name}")
        for collection, manifest in manifests.items():
            write_json(staging / collection / "collection.json", manifest)
            originals = [path.parent for path, (name, _, _) in reports.items() if name == collection]
            catalog = originals[0] / "blender_assets.cats.txt"
            if catalog.exists():
                shutil.copy2(catalog, staging / collection)
        if single_collection:
            dependencies = [(staging / name, destination.parent / name) for name in manifests if name != destination.name]
            for _, path in dependencies:
                if path.exists():
                    raise ValueError(f"Dependency source already exists: {path}")
            replace_directories([*dependencies, (staging / destination.name, destination)])
        else:
            replace_directories([(staging, destination)])
    done([destination])
