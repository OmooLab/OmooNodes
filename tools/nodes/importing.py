"""Import complete asset libraries into native, unversioned nodebpy modules."""

from __future__ import annotations

import ast
import shutil
import tempfile
from pathlib import Path

from .cli import configuration, replace_directories, rewrite_foreign_modules, run_worker, verify_graphs, write_json


def module_classes(root):
    result = {}
    for path in root.rglob("*.py"):
        for statement in ast.parse(path.read_text(encoding="utf8")).body:
            if not isinstance(statement, ast.ClassDef):
                continue
            for item in statement.body:
                if isinstance(item, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "_name" for target in item.targets):
                    result[ast.literal_eval(item.value)] = (path, statement.name)
    return result


def dump_sources(source, destination):
    if destination.exists():
        raise ValueError(f"Source already exists: {destination}; use dev --sync")
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("Input and source output must not overlap")
    config = configuration(prepare_targets=False)
    config["cache"].mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=config["cache"]) as directory:
        temporary = Path(directory)
        staging = temporary / "nodes"
        staging.mkdir()
        (staging / "__init__.py").write_text("")
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
            if not collection.isidentifier() or not path.stem.isidentifier():
                raise ValueError(f"Collection and file stems must be Python identifiers: {path}")
            module_root = staging / collection / path.stem
            if module_root.exists():
                raise ValueError(f"Duplicate source file: {collection}/{path.name}")
            module_root.parent.mkdir(exist_ok=True)
            (module_root.parent / "__init__.py").write_text("")
            report = run_worker(config, temporary, "dump", input=str(path), output=str(module_root))
            for owner in set(report["owners"].values()):
                visit(Path(owner))
            for name, (module, class_name) in module_classes(module_root).items():
                if name in report["owners"] or name not in report["groups"]:
                    continue
                if name in owners and owners[name]["file_path"] != path:
                    raise ValueError(f"Ambiguous node ownership: {name}")
                owners[name] = {"library": collection, "file": path.name, "file_path": path,
                                "module": "nodes." + ".".join(module.relative_to(staging).with_suffix("").parts),
                                "class": class_name}
            reports[path] = (collection, module_root, report)
            visiting.remove(path)

        for path in sorted(files):
            visit(path)
        if not reports:
            raise ValueError(f"No blend files: {source}")
        manifests = {}
        for path, (collection, module_root, report) in reports.items():
            imports = {name: {"module": owners[name]["module"], "class": owners[name]["class"]}
                       for name in report["owners"]}
            rewrite_foreign_modules(module_root, imports)
            manifest = manifests.setdefault(collection, {"dependencies": [], "files": {}})
            dependencies = {owners[name]["library"] for name in imports} - {collection}
            manifest["dependencies"] = sorted(set(manifest["dependencies"]) | dependencies)
            manifest["files"][path.name] = {
                "source": path.stem, "source_version": report["source_version"],
                "links": {name: {"library": owners[name]["library"], "file": owners[name]["file"]} for name in imports},
                "imports": imports,
            }
            output = temporary / "validation" / collection / path.name
            output.parent.mkdir(parents=True, exist_ok=True)
            links = {name: str(temporary / "validation" / owners[name]["library"] / owners[name]["file"]) for name in imports}
            run_worker(config, temporary, "build", input=str(module_root), output=str(output),
                       package_root=str(temporary), links=links)
            actual = run_worker(config, temporary, "inspect", input=str(output))
            verify_graphs(report["graphs"], actual["graphs"], f"Initial import: {path.name}")
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
