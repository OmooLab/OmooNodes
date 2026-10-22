"""Build, verify, and synchronize collections and their dependencies."""

import shutil
import tempfile
from pathlib import Path
from contextlib import nullcontext

from .console import done, progress
from .files import read_json, replace_directories
from .runtimes import configuration, run_worker
from .sources import apply_changes, select_sources


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


def build_staged(config, sources, destination, temporary, quiet=False):
    for version in config["versions"]:
        if not quiet:
            print(f"{version} ({config['versions'][version]})", flush=True)
        selected_root = temporary / version
        selected_root.mkdir(parents=True)
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
                with nullcontext() if quiet else progress(filename, indent="  "):
                    run_worker(config, temporary, "build", version=version, input=str(module_root),
                               output=str(output), links=links, source_root=str(selected_root))
            catalog = source / "blender_assets.cats.txt"
            if catalog.exists():
                shutil.copy2(catalog, library_out)


def check_dependents(sources, destination, versions):
    """Keep existing consumers in the same rebuild as their dependencies."""
    selected = set(sources)
    root = sources[0].parent
    for manifest in sorted(root.glob("*/collection.json")):
        consumer = manifest.parent
        if consumer in selected:
            continue
        existing = [version for version in versions
                    if any((destination / version / consumer.name).rglob("*.blend"))]
        if not existing:
            continue
        affected = selected.intersection(libraries(consumer))
        if not affected:
            continue
        names = ", ".join(sorted(path.name for path in affected))
        raise ValueError(
            f"{existing[0]}/{consumer.name} depends on {names}; rebuild these collections together "
            f"by selecting {root}. Sync any workspace edits to sources first."
        )


def dev(source, workspace, target=None):
    if source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise ValueError("Source and editing workspace must not overlap")
    with progress("Checking runtimes"):
        config = configuration(target, development=True)
    closure = libraries(source)
    check_dependents(closure, workspace, config["versions"])
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
        config = configuration(prepare_targets=False)
    closure = libraries(source)
    available = [label for label in config["versions"] if not target or label == target
                 if any(list((workspace / label / library.name).glob("*.blend")) for library in closure)]
    if not available:
        raise ValueError(f"No development libraries found for the selected source/target in {workspace}; run omoonodes dev first")
    if len(available) > 1:
        raise ValueError("Sync requires one workspace target; use --target when multiple versions exist")
    version = available[0]
    print(f"{version} ({config['versions'][version]})", flush=True)
    config["cache"].mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=config["cache"]) as directory:
        temporary = Path(directory)
        baseline = temporary / "baseline"
        editing = {**config, "versions": {version: config["targets"][version]}}
        build_staged(editing, closure, baseline, temporary / "selected", quiet=True)
        candidates = temporary / "sources"
        for library in closure:
            shutil.copytree(library, candidates / library.name, ignore=shutil.ignore_patterns("__pycache__"))
        expected = {}
        changed = False
        for library in closure:
            edited = workspace / version / library.name
            manifest = read_json(library / "collection.json")
            for filename, data in manifest["files"].items():
                blend = edited / filename
                if not blend.is_file():
                    continue
                before = temporary / "before" / library.name / data["source"]
                output = temporary / "after" / library.name / data["source"]
                with progress(filename, indent="  "):
                    run_worker(config, temporary, "dump", version=version,
                               input=str(baseline / version / library.name / filename), output=str(before),
                               source_root=str(temporary / "selected" / version))
                    report = run_worker(config, temporary, "dump", version=version, input=str(blend), output=str(output),
                                        source_root=str(temporary / "selected" / version))
                    expected[(library.name, filename)] = report["graphs"]
                    changed |= bool(apply_changes(candidates / library.name / data["source"], before, output, version))
        for library in closure:
            catalog = workspace / version / library.name / "blender_assets.cats.txt"
            if catalog.is_file():
                original = library / catalog.name
                changed |= not original.exists() or catalog.read_bytes() != original.read_bytes()
                shutil.copy2(catalog, candidates / library.name)
        if changed:
            with progress("Checking sources"):
                validated = temporary / "validated"
                all_targets = {**config, "versions": config["targets"]}
                build_staged(all_targets, [candidates / library.name for library in closure], validated, temporary / "validation", quiet=True)
                for (name, filename), graph in expected.items():
                    actual = run_worker(config, temporary, "inspect", version=version,
                                        input=str(validated / version / name / filename))
                    if actual["graphs"] != graph:
                        raise ValueError(f"Sources do not preserve edits: {name}/{filename}")
            replace_directories([(candidates / library.name, library) for library in closure])
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
    check_dependents(closure, output, config["versions"])
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
