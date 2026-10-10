"""Develop, import, and build native node libraries."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

from .sources import merge_exports, select_sources, source_digest
from .runtimes import ensure_runtime, runtime_environment, target_settings

WORKER = Path(__file__).with_name("blender.py")
DEFAULT_BACKEND = {"python": "3.13", "nodebpy": "520.34.1", "bpy": "5.2.2"}
DEFAULT_VERSIONS = {"b45": "4.5.14", "b52": "5.2.2"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")


def read_baseline(library):
    baseline = read_json(library / ".nodes.json")
    if baseline.get("format") != 2 or any("own_signature" not in graph for graphs in baseline["files"].values() for graph in graphs.values()):
        raise ValueError(f"Recreate the development library to capture metadata and resources: {library}")
    return baseline


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
    if not isinstance(declared, list) or not declared or any(not isinstance(label, str) or label not in DEFAULT_VERSIONS for label in declared) or len(set(declared)) != len(declared):
        raise ValueError('Set tool.nodes.targets to a nonempty list of supported targets: ["b45", "b52"]')
    overrides = settings.get("versions", {})
    if not isinstance(overrides, dict) or set(overrides) - set(declared):
        raise ValueError("tool.nodes.versions may only override declared targets")
    targets = {label: target_settings(label, overrides.get(label, DEFAULT_VERSIONS[label])) for label in declared}
    base_target = min(targets, key=lambda label: tuple(map(int, targets[label]["bpy"].split("."))))
    if target and target not in targets:
        raise ValueError(f"Unknown target: {target}")
    chosen = [target or base_target] if target or development else list(targets)
    backend = {**DEFAULT_BACKEND, **settings.get("backend", {})}
    cache = root / ".cache/nodes"
    data = {"root": root, "cache": cache, "settings": settings, "base_target": base_target,
            "builder": ensure_runtime(cache, "backend", backend), "builder_version": backend["bpy"],
            "versions": {label: targets[label]["bpy"] for label in chosen}}
    for label in chosen if prepare_targets else ():
        data[label] = ensure_runtime(cache, label, targets[label])
    return data


def run_worker(config, temporary, action, version=None, **options):
    runtime = version or "builder"
    job = temporary / f"{action}-{runtime}.json"
    report = job.with_suffix(".report.json")
    expected = config["versions"][version] if version else config["builder_version"]
    write_json(job, {"action": action, "report": str(report),
                     "expected_version": expected, **options})
    environment = runtime_environment()
    user = temporary / "blender-user"
    for suffix in ("RESOURCES", "CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
        path = user / suffix.lower()
        path.mkdir(parents=True, exist_ok=True)
        environment["BLENDER_USER_" + suffix] = str(path)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([config[runtime], str(WORKER), "--", str(job)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding="utf8", errors="replace", env=environment)
    backend_version = tuple(map(int, config["builder_version"].split(".")[:2]))
    target_version = tuple(map(int, expected.split(".")[:2]))
    for line in result.stdout.splitlines():
        # Asset-only files have no scene/UI; these messages are normal during inspection.
        if result.returncode == 0 and (line.strip() == "Warning: Library file, loading empty scene"
                                      or line.startswith("Info: Read library: ")
                                      or line.startswith('Read blend: "')
                                      or re.fullmatch(r'\d+:\d+\.\d+\s+blend\s+\| Read blend: .*', line.strip())):
            continue
        warning = re.fullmatch(r"Warning: File written by newer Blender binary \((\d+)\.(\d+)\), expect loss of data!", line.strip())
        if (result.returncode == 0 and action == "inspect" and options.get("save")
                and backend_version > target_version and warning
                and int(warning[1]) == backend_version[0] * 100 + backend_version[1]):
            continue
        print(line, flush=True)
    result.check_returncode()
    return read_json(report)


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


def verify_graphs(expected, actual, label):
    if expected != actual:
        names = sorted(name for name in expected.keys() | actual.keys()
                       if expected.get(name) != actual.get(name))
        raise ValueError(f"Logical roundtrip failed ({label}): {', '.join(names)}")


def build_staged(config, sources, destination, temporary):
    for version in config["versions"]:
        print(f"Target {version} · Blender {config['versions'][version]}", flush=True)
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
            records = {}
            for filename, data in manifest["files"].items():
                output = library_out / filename
                module_root = selected_root / source.name / data["source"]
                if not any(path.name != "__init__.py" for path in module_root.rglob("*.py")):
                    continue
                links = {name: str(destination / version / owner["library"] / owner["file"])
                         for name, owner in data.get("links", {}).items()}
                label = f"{version}/{source.name}/{filename}"
                print(f"  {filename}: build -> save -> check", flush=True)
                run_worker(config, temporary, "build", input=str(module_root),
                           output=str(output), package_root=str(package_root), links=links)
                # Both targets save and validate using their own bpy runtime.
                result = run_worker(config, temporary, "inspect", version=version, input=str(output), save=True)
                reload = run_worker(config, temporary, "inspect", version=version, input=str(output))
                expected_version = list(map(int, config["versions"][version].split(".")[:2]))
                if reload["file_version"][:2] != expected_version:
                    raise ValueError(f"Unexpected saved file version ({label}): {reload['file_version']}")
                verify_graphs(result["graphs"], reload["graphs"], f"{version}/{filename}")
                records[filename] = reload["graphs"]
            catalog = source / "blender_assets.cats.txt"
            if catalog.exists():
                shutil.copy2(catalog, library_out)
            write_json(library_out / ".nodes.json", {
                "format": 2, "source": source_digest(source), "version": version, "files": records,
            })


def verify_workspace(config, source, workspace, temporary):
    for version in config["versions"]:
        library = workspace / version / source.name
        baseline_file = library / ".nodes.json"
        if not library.exists():
            continue
        if not baseline_file.exists():
            raise ValueError(f"Missing baseline: {library}")
        baseline = read_baseline(library)
        if baseline["source"] != source_digest(source):
            raise ValueError(f"Source changed since workspace build: {source}")
        for filename, graph in baseline["files"].items():
            result = run_worker(config, temporary, "inspect", version=version, input=str(library / filename))
            verify_graphs(graph, result["graphs"], f"Unsynchronized edits in {library / filename}")


def replace_directories(replacements):
    """Commit directories together, restoring every old directory on failure."""
    backups = []
    installed = []
    try:
        for source, target in replacements:
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = target.with_name(target.name + ".nodes-backup")
            if backup.exists():
                raise ValueError(f"Unfinished transaction: {backup}")
            if target.exists():
                target.rename(backup)
                backups.append((backup, target))
            source.rename(target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            shutil.rmtree(target)
        for backup, target in reversed(backups):
            backup.rename(target)
        raise
    for backup, _ in backups:
        shutil.rmtree(backup)


def directory_changes(source, target):
    """List changed files without replacing the containing directories."""
    paths = {path.relative_to(root) for root in (source, target) for path in root.rglob("*")
             if path.is_file() and "__pycache__" not in path.relative_to(root).parts}
    changes = []
    for relative in sorted(paths):
        updated, current = source / relative, target / relative
        if updated.is_file() and current.is_file() and updated.read_bytes() == current.read_bytes():
            continue
        changes.append((updated if updated.is_file() else None, current))
    return changes


def replace_files(replacements):
    """Commit changed files together; preserve backups if rollback is blocked."""
    backups = {}
    installed = []
    for _, target in replacements:
        backup = target.with_name(target.name + ".nodes-backup")
        if backup.exists():
            raise ValueError(f"Unfinished transaction: {backup}")
    try:
        for _, target in replacements:
            if target.exists():
                backup = target.with_name(target.name + ".nodes-backup")
                backups[target] = backup
                shutil.copy2(target, backup)
        for source, target in replacements:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source is None:
                target.unlink()
            else:
                source.replace(target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            if target in backups:
                backups[target].replace(target)
            else:
                target.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
        raise
    for backup in backups.values():
        backup.unlink()


def dev(source, workspace, target=None):
    if source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise ValueError("Source and editing workspace must not overlap")
    print("Preparing development libraries: checking runtimes", flush=True)
    config = configuration(target, development=True)
    closure = libraries(source)
    print(f"Collections: {' -> '.join(library.name for library in closure)}", flush=True)
    cache = config["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        temporary = Path(directory)
        print("Checking existing development libraries for unsynchronized changes", flush=True)
        for library in closure:
            verify_workspace(config, library, workspace, temporary)
        staged = temporary / "workspaces"
        build_staged(config, closure, staged, temporary)
        replace_directories([(staged / version / library.name, workspace / version / library.name)
                             for version in config["versions"] for library in closure])
    print("Done: development libraries exported", flush=True)
    for version in config["versions"]:
        for library in closure:
            print(f"  {(workspace / version / library.name).as_posix()}", flush=True)


def sync(source, workspace, target=None):
    # Sync never bypasses logical validation or writes sources directly from dump.
    print("Preparing sync: checking runtimes", flush=True)
    config = configuration(target, prepare_targets=False)
    if source.is_relative_to(workspace) or workspace.is_relative_to(source):
        raise ValueError("Source and editing workspace must not overlap")
    if not workspace.is_dir():
        raise ValueError(f"Development directory does not exist: {workspace}")
    closure = libraries(source)
    available = [label for label in config["versions"] if not target or label == target
                 if any((workspace / label / library.name / ".nodes.json").is_file() for library in closure)]
    if not available:
        raise ValueError(f"No development libraries found for the selected source/target in {workspace}; run nodes dev first")
    if len(available) > 1:
        raise ValueError("Sync requires one workspace target; use --target when multiple versions exist")
    version = available[0]
    config = {**config, "versions": {version: config["versions"][version]}}
    config[version] = ensure_runtime(config["cache"], version, target_settings(version, config["versions"][version]))
    print(f"Collections: {' -> '.join(library.name for library in closure)}", flush=True)
    source_versions = {library: source_digest(library) for library in closure}
    workspace_versions = {}
    cache = config["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        temporary = Path(directory)
        replacements = []
        baselines = []
        for library in closure:
            manifest = read_json(library / "collection.json")
            exports = {}
            changed = False
            for version in config["versions"]:
                edited = workspace / version / library.name
                if not edited.exists():
                    continue
                workspace_versions[edited] = source_digest(edited)
                baseline = read_baseline(edited)
                if baseline["source"] != source_digest(library):
                    raise ValueError(f"Source changed since workspace build: {library}")
                export_root = temporary / "exports" / version / library.name
                select_sources(library, export_root, version)
                for filename, data in manifest["files"].items():
                    if filename not in baseline["files"]:
                        continue
                    print(f"  {version}/{filename}: checking changes", flush=True)
                    current = run_worker(config, temporary, "inspect", version=version, input=str(edited / filename))
                    if current["graphs"] == baseline["files"][filename]:
                        continue
                    if set(baseline["files"][filename]) - set(current["graphs"]):
                        raise ValueError(f"Missing assets; explicit source reconciliation required: {filename}")
                    if set(current["graphs"]) & set(data.get("links", {})):
                        raise ValueError(f"Foreign group was localized; resolve ownership first: {filename}")
                    names = [name for name, graph in current["graphs"].items()
                             if graph["own_signature"] != baseline["files"][filename].get(name, {}).get("own_signature")]
                    if names:
                        changed = True
                        print(f"  {version}/{filename}: exporting {len(names)} changed assets", flush=True)
                        run_worker(config, temporary, "dump", input=str(edited / filename),
                                   output=str(export_root / data["source"]), names=names)
                        rewrite_foreign_modules(export_root / data["source"], data.get("imports", {}))
                    baseline["files"][filename] = current["graphs"]
                exports[version] = export_root
                baselines.append((edited / ".nodes.json", baseline))
            if changed:
                candidate = temporary / "candidate" / library.name
                print(f"  {library.name}: merging versions", flush=True)
                merge_exports(library, exports, candidate)
                replacements.append((candidate, library))
        if not replacements:
            print("Done: no logical changes", flush=True)
            return
        candidates = {target.name: candidate for candidate, target in replacements}
        staged_sources = []
        # Keep sibling library paths valid while validating the combined candidate.
        for library in closure:
            candidate = temporary / "validation-sources" / library.name
            shutil.copytree(candidates.get(library.name, library), candidate)
            staged_sources.append(candidate)
        validated = temporary / "validated"
        print("Validating: rebuilding all configured targets", flush=True)
        validation_config = configuration()
        build_staged(validation_config, staged_sources, validated, temporary)
        for baseline_path, baseline in baselines:
            validated_baseline = read_json(validated / baseline["version"] / baseline_path.parent.name / ".nodes.json")
            for filename, expected in baseline["files"].items():
                verify_graphs(expected, validated_baseline["files"][filename], filename)
        source_changes = list(replacements)
        file_changes = [change for candidate, library in source_changes
                        for change in directory_changes(candidate, library)]
        for baseline_path, baseline in baselines:
            library_name = baseline_path.parent.name
            version = baseline["version"]
            staged_baseline = temporary / "baselines" / version / library_name / ".nodes.json"
            staged_baseline.parent.mkdir(parents=True, exist_ok=True)
            baseline["source"] = source_digest(candidates.get(library_name, next(library for library in closure if library.name == library_name)))
            write_json(staged_baseline, baseline)
            file_changes.append((staged_baseline, baseline_path))
        print("Committing: checking concurrent changes", flush=True)
        for library, expected in source_versions.items():
            if source_digest(library) != expected:
                raise ValueError(f"Source changed during synchronization: {library}")
        for edited, expected in workspace_versions.items():
            if source_digest(edited) != expected:
                raise ValueError(f"Development library changed during synchronization: {edited}")
        replace_files(file_changes)
        print("Done: sources synchronized", flush=True)
        for _, destination in source_changes:
            print(f"  {destination.as_posix()}", flush=True)


def rewrite_foreign_modules(root, imports):
    """Replace dumped foreign class copies with imports from their owner."""
    forwarded = {}
    trees = {}
    removable = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf8"))
        replacements = {}
        kept = []
        for statement in tree.body:
            if isinstance(statement, ast.ClassDef):
                names = [ast.literal_eval(item.value) for item in statement.body
                         if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_name" for t in item.targets)]
                if names and names[0] in imports:
                    replacements[statement.name] = imports[names[0]]
                    forwarded[(path.resolve(), statement.name)] = imports[names[0]]
                    continue
            kept.append(statement)
        if replacements:
            if not any(isinstance(item, ast.ClassDef) for item in kept) and path.name != "__init__.py":
                removable.append(path)
                continue
            for alias, owner in replacements.items():
                kept.insert(0, ast.ImportFrom(module=owner["module"], names=[ast.alias(name=owner["class"], asname=alias)], level=0))
            tree.body = kept
        trees[path] = tree
    for path, tree in trees.items():
        original = ast.dump(ast.parse(path.read_text(encoding="utf8")))
        body = []
        for statement in tree.body:
            if not isinstance(statement, ast.ImportFrom) or not statement.level:
                body.append(statement)
                continue
            parent = path.parent
            for _ in range(statement.level - 1):
                parent = parent.parent
            module_path = parent.joinpath(*(statement.module or "").split(".")).with_suffix(".py").resolve()
            remaining = []
            for alias in statement.names:
                owner = forwarded.get((module_path, alias.name))
                if owner:
                    body.append(ast.ImportFrom(module=owner["module"], level=0,
                                               names=[ast.alias(name=owner["class"], asname=alias.asname or alias.name)]))
                else:
                    remaining.append(alias)
            if remaining:
                statement.names = remaining
                body.append(statement)
        tree.body = body
        if ast.dump(tree) != original:
            path.write_text(ast.unparse(tree) + "\n", encoding="utf8")
    for path in removable:
        path.unlink()


def build(source, output, target=None, remote=False, self_contained=False):
    if source.is_relative_to(output) or output.is_relative_to(source):
        raise ValueError("Source and output must not overlap")
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
                run_worker(config, temporary, "publish", version=version,
                           input=str(workspace / version / collection.name),
                           output=str(published / version / collection.name),
                           remote=remote, self_contained=self_contained,
                           contact=config["settings"].get("contact", {}))
        replace_directories([(published / version / collection.name, output / version / collection.name)
                             for version in config["versions"] for collection in closure])
    print("Done: node libraries built", flush=True)
    for version in config["versions"]:
        for collection in closure:
            print(f"  {(output / version / collection.name).as_posix()}", flush=True)


def parser():
    result = argparse.ArgumentParser(description="Develop, import, and build node libraries")
    commands = result.add_subparsers(dest="command", required=True)
    development = commands.add_parser("dev", help="Prepare or synchronize editable node libraries")
    development.add_argument("source", nargs="?", type=Path, help="Collection or nodes root; defaults to project source")
    direction = development.add_mutually_exclusive_group()
    direction.add_argument("-o", "--output", type=Path, help="Development parent; defaults to workspaces")
    direction.add_argument("-s", "--sync", type=Path, help="Read target libraries from this development parent and synchronize sources")
    development.add_argument("--target", help="Dev: lowest configured target by default; sync: recorded workspace target")
    formal = commands.add_parser("build", help="Build formal node libraries")
    formal.add_argument("source", nargs="?", type=Path, help="Collection or nodes root; defaults to project source")
    formal.add_argument("-o", "--output", type=Path, default=Path("dist"), help="Output parent; defaults to dist")
    formal.add_argument("--target", help="Configured target; defaults to all")
    formal.add_argument("--remote", action="store_true", help="Generate a remote library; default is local")
    formal.add_argument("--self-contained", action="store_true", help="Embed external dependencies in local libraries")
    importing = commands.add_parser("dump", help="Import all asset node groups as native sources")
    importing.add_argument("input", type=Path, help="Asset library blend file or directory")
    importing.add_argument("-o", "--output", type=Path, required=True, help="New native source destination")
    return result


def main(argv=None):
    command = parser()
    args = command.parse_args(argv)
    try:
        if args.command == "dump":
            from .importing import dump_sources
            dump_sources(args.input.resolve(), args.output.resolve())
            return
        settings = tomllib.loads((project_root() / "pyproject.toml").read_text(encoding="utf8"))["tool"]["nodes"]
        source = (args.source or project_root() / settings.get("source", "nodes")).resolve()
        if args.command == "dev":
            if args.sync:
                sync(source, args.sync.resolve(), args.target)
            else:
                dev(source, (args.output or Path("workspaces")).resolve(), args.target)
        else:
            build(source, args.output.resolve(), args.target, args.remote, args.self_contained)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        command.exit(1, f"nodes: {error}\n")


if __name__ == "__main__":
    main()
