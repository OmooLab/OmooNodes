"""Build, verify, and synchronize collections and their dependencies."""

import shutil
import tempfile
from pathlib import Path

from .console import done, progress
from .files import read_json, replace_directories
from .runtimes import configuration, run_worker
from .sources import overwrite_sources, rewrite_foreign_modules, select_sources


def libraries(source):
    """Read the dependency closure in build order."""
    result = []
    visiting = set()

    def visit(path):
        if path in result:
            return
        if path in visiting:
            raise ValueError(f"Recursive library dependency: {path}")
        visiting.add(path)
        manifest = read_json(path / "collection.json")
        for name in manifest.get("dependencies", []):
            visit(path.parent / name)
        visiting.remove(path)
        result.append(path)

    if (source / "collection.json").is_file():
        visit(source)
    else:
        for manifest in sorted(source.glob("*/collection.json")):
            visit(manifest.parent)
    if not result:
        raise ValueError(f"No node collections: {source}")
    return result


def build_staged(config, sources, destination, temporary):
    for version in config["versions"]:
        print(f"{version} ({config['versions'][version]})", flush=True)
        package_root = temporary / version
        selected_root = package_root / "nodes"
        selected_root.mkdir(parents=True)
        (selected_root / "__init__.py").write_text("", encoding="utf8")
        for source in sources:
            select_sources(source, selected_root / source.name, version)
        for source in sources:
            manifest = read_json(source / "collection.json")
            library_out = destination / version / source.name
            library_out.mkdir(parents=True, exist_ok=True)
            for filename, data in manifest["files"].items():
                output = library_out / filename
                module_root = selected_root / source.name / data["source"]
                if not any(path.name != "__init__.py" for path in module_root.rglob("*.py")):
                    continue
                links = {name: str(destination / version / owner["library"] / owner["file"])
                         for name, owner in data.get("links", {}).items()}
                with progress(filename, indent="  "):
                    run_worker(config, temporary, "build", input=str(module_root),
                               output=str(output), package_root=str(package_root), links=links)
                    run_worker(config, temporary, "inspect", version=version, input=str(output), save=True)
            catalog = source / "blender_assets.cats.txt"
            if catalog.exists():
                shutil.copy2(catalog, library_out)


def dev(source, workspace, target=None):
    if source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise ValueError("Source and editing workspace must not overlap")
    with progress("Checking runtimes"):
        config = configuration(target, development=True)
    closure = libraries(source)
    cache = config["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        temporary = Path(directory)
        staged = temporary / "workspaces"
        build_staged(config, closure, staged, temporary)
        replace_directories([(staged / version / library.name, workspace / version / library.name)
                             for version in config["versions"] for library in closure])
    done(workspace / version / library.name for version in config["versions"] for library in closure)


def sync(source, workspace, target=None):
    if source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise ValueError("Source and editing workspace must not overlap")
    if not workspace.is_dir():
        raise ValueError(f"Development directory does not exist: {workspace}")
    with progress("Checking runtimes"):
        config = configuration(target, prepare_targets=False)
    closure = libraries(source)
    available = [label for label in config["versions"] if not target or label == target
                 if any(list((workspace / label / library.name).glob("*.blend")) for library in closure)]
    if not available:
        raise ValueError(f"No development libraries found for the selected source/target in {workspace}; run nodes dev first")
    if len(available) > 1:
        raise ValueError("Sync requires one workspace target; use --target when multiple versions exist")
    version = available[0]
    print(f"{version} ({config['versions'][version]})", flush=True)
    config["cache"].mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=config["cache"]) as directory:
        temporary = Path(directory)
        exports = []
        for library in closure:
            edited = workspace / version / library.name
            manifest = read_json(library / "collection.json")
            for filename, data in manifest["files"].items():
                blend = edited / filename
                if not blend.is_file():
                    continue
                output = temporary / library.name / data["source"]
                with progress(filename, indent="  "):
                    run_worker(config, temporary, "dump", input=str(blend), output=str(output))
                    rewrite_foreign_modules(output, data.get("imports", {}))
                exports.append((library / data["source"], output))
        for destination, exported in exports:
            overwrite_sources(destination, exported, version)
        for library in closure:
            catalog = workspace / version / library.name / "blender_assets.cats.txt"
            if catalog.is_file():
                shutil.copy2(catalog, library)
    done(closure)


def build(source, output, target=None, remote=False, self_contained=False):
    if source.is_relative_to(output) or output.is_relative_to(source):
        raise ValueError("Source and output must not overlap")
    with progress("Checking runtimes"):
        config = configuration(target)
    if remote and any(tuple(map(int, value.split(".")[:2])) < (5, 2)
                      for value in config["versions"].values()):
        raise ValueError("Remote libraries require a configured Blender 5.2+ target")
    closure = libraries(source)
    cache = config["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        temporary = Path(directory)
        workspace = temporary / "workspace"
        build_staged(config, closure, workspace, temporary)
        published = temporary / "published"
        for version in config["versions"]:
            for collection in closure:
                with progress(f"Publishing {version}/{collection.name}", indent="  "):
                    run_worker(config, temporary, "publish", version=version,
                               input=str(workspace / version / collection.name),
                               output=str(published / version / collection.name),
                               remote=remote, self_contained=self_contained,
                               contact=config["settings"].get("contact", {}))
        replace_directories([(published / version / collection.name, output / version / collection.name)
                             for version in config["versions"] for collection in closure])
    done(output / version / collection.name for version in config["versions"] for collection in closure)
