from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONTACT_URL = "https://git.omoolab.xyz/icrdr/OmooNodes"
DEFAULT_OUTPUT_DIRECTORY = Path.cwd()
VERSIONED_BLEND_PATTERN = re.compile(
    r"^(?P<stem>.+)\.b(?P<major>\d)(?P<minor>\d+)\.blend$"
)
IGNORED_FILES = {
    "_asset-library-meta.json",
    "blender_assets.cats.txt~",
}
IGNORED_DIRECTORY_NAMES = {
    "_v1",
    "__pycache__",
}


class BuildError(RuntimeError):
    """Raised when an Asset Library cannot be built safely."""


@dataclass(frozen=True)
class BlendLayers:
    """A base blend file and its selected version overlays."""

    base: Path
    overlays: tuple[Path, ...]


@dataclass
class BuildStats:
    """Counters collected while building an Asset Library."""

    blend_files: int = 0
    versioned_assets: int = 0
    linked_data: int = 0
    scenes: int = 0
    purged_data: int = 0
    libraries: int = 0
    assets: int = 0

    def merge(self, other: "BuildStats") -> None:
        self.blend_files += other.blend_files
        self.versioned_assets += other.versioned_assets
        self.linked_data += other.linked_data
        self.scenes += other.scenes
        self.purged_data += other.purged_data
        self.libraries += other.libraries
        self.assets += other.assets


def versioned_blend_info(path: Path) -> tuple[str, tuple[int, int]] | None:
    match = VERSIONED_BLEND_PATTERN.fullmatch(path.name)
    if match is None:
        return None
    stem = match.group("stem")
    version = (int(match.group("major")), int(match.group("minor")))
    return stem, version


def discover_blend_layers(
    source: Path,
    target_version: tuple[int, int],
) -> tuple[BlendLayers, ...]:
    bases: dict[tuple[Path, str], Path] = {}
    overlays: dict[tuple[Path, str], list[tuple[tuple[int, int], Path]]] = {}

    for path in sorted(source.rglob("*.blend")):
        relative_parent = path.relative_to(source).parent
        versioned = versioned_blend_info(path)
        if versioned is None:
            key = (relative_parent, path.stem)
            bases[key] = path
            continue

        stem, minimum_version = versioned
        key = (relative_parent, stem)
        overlays.setdefault(key, []).append((minimum_version, path))

    unknown = sorted(key for key in overlays if key not in bases)
    if unknown:
        names = ", ".join(
            str(parent / f"{stem}.blend") for parent, stem in unknown
        )
        raise BuildError(f"Version overlays have no base blend file: {names}")

    result = []
    for key, base in sorted(bases.items(), key=lambda item: str(item[1])):
        selected = [
            (minimum_version, path)
            for minimum_version, path in overlays.get(key, [])
            if minimum_version <= target_version
        ]
        selected.sort(key=lambda item: (item[0], item[1].name))
        result.append(
            BlendLayers(
                base=base,
                overlays=tuple(path for _, path in selected),
            )
        )
    return tuple(result)


def append_node_groups(
    blend_data: Any,
    source: Path,
    *,
    link: bool,
) -> dict[str, Any]:
    requested: list[str] = []
    loaded: list[Any] = []
    with blend_data.libraries.load(
        str(source),
        link=link,
        relative=False,
    ) as (data_from, data_to):
        requested.extend(data_from.node_groups)
        data_to.node_groups = list(data_from.node_groups)
        loaded = data_to.node_groups
    return dict(zip(requested, loaded))


def remove_library(bpy: Any, source: Path) -> None:
    blend_data = bpy.data
    expected = source.resolve()
    for library in tuple(blend_data.libraries):
        library_path = Path(bpy.path.abspath(library.filepath))
        if library_path.resolve() == expected:
            blend_data.libraries.remove(library)


def compose_overlay(
    bpy: Any,
    dependency_sources: tuple[Path, ...],
    overlay: Path,
) -> int:
    blend_data = bpy.data
    base_groups = {
        node_group.name: node_group
        for node_group in blend_data.node_groups
        if node_group.library is None
    }

    for index, node_group in enumerate(base_groups.values()):
        node_group.name = f"__OMOO_BASE_{index:04d}"

    linked_dependency_groups = [
        append_node_groups(blend_data, source, link=True)
        for source in dependency_sources
    ]
    overlay_groups = append_node_groups(blend_data, overlay, link=False)

    for dependency_groups in linked_dependency_groups:
        for name, linked_group in dependency_groups.items():
            local_group = base_groups.get(name)
            if linked_group is None or local_group is None:
                continue
            linked_group.user_remap(local_group)

    for name, overlay_group in overlay_groups.items():
        if overlay_group is None:
            continue
        base_group = base_groups.pop(name, None)
        if base_group is not None:
            base_group.user_remap(overlay_group)
            blend_data.node_groups.remove(base_group, do_unlink=True)
        overlay_group.name = name

    for name, base_group in base_groups.items():
        base_group.name = name

    for dependency_groups in linked_dependency_groups:
        for linked_group in dependency_groups.values():
            if linked_group is None:
                continue
            if linked_group.name in blend_data.node_groups:
                blend_data.node_groups.remove(linked_group, do_unlink=True)

    for source in dependency_sources:
        remove_library(bpy, source)
    remove_library(bpy, overlay)
    return sum(
        1
        for group in overlay_groups.values()
        if group is not None and group.asset_data is not None
    )


def missing_node_group_references(bpy: Any) -> set[str]:
    missing_references = set()
    for node_group in bpy.data.node_groups:
        if node_group.library is not None:
            continue
        for node in node_group.nodes:
            if node.type == "GROUP" and node.node_tree is None:
                missing_references.add(f"{node_group.name}:{node.name}")
    return missing_references


def validate_composed_node_groups(
    bpy: Any,
    destination: Path,
    allowed_missing_references: set[str],
) -> None:
    missing_references = (
        missing_node_group_references(bpy) - allowed_missing_references
    )
    if missing_references:
        details = ", ".join(sorted(missing_references))
        raise BuildError(
            f"Composed node groups contain missing references in "
            f"{destination}: {details}"
        )


def compose_blend_file(
    bpy: Any,
    layers: BlendLayers,
    destination: Path,
    localize_linked: bool,
) -> BuildStats:
    bpy.ops.wm.open_mainfile(filepath=str(layers.base), load_ui=False)
    allowed_missing_references = missing_node_group_references(bpy)
    destination.parent.mkdir(parents=True, exist_ok=True)

    stats = BuildStats()
    if localize_linked:
        # Relative links must be resolved before the working copy moves.
        stats.merge(localize_linked_data(bpy.data))

    # Saving a working copy makes the base source available as a library.
    bpy.ops.wm.save_as_mainfile(
        filepath=str(destination),
        check_existing=False,
        relative_remap=False,
    )

    dependency_sources = [layers.base]
    for overlay in layers.overlays:
        stats.versioned_assets += compose_overlay(
            bpy,
            tuple(dependency_sources),
            overlay,
        )
        dependency_sources.append(overlay)

    if localize_linked:
        stats.merge(localize_linked_data(bpy.data))

    validate_composed_node_groups(
        bpy,
        destination,
        allowed_missing_references,
    )
    bpy.ops.wm.save_as_mainfile(
        filepath=str(destination),
        check_existing=False,
        relative_remap=False,
    )
    return stats


def compose_library(
    bpy: Any,
    source: Path,
    destination: Path,
    target_version: tuple[int, int],
    localize_linked: bool,
) -> BuildStats:
    layers = discover_blend_layers(source, target_version)
    if not layers:
        raise BuildError(f"No base .blend files found in: {source}")

    stats = BuildStats()
    for blend_layers in layers:
        relative_path = blend_layers.base.relative_to(source)
        print(f"Composing: {relative_path}")
        stats.merge(
            compose_blend_file(
                bpy,
                blend_layers,
                destination / relative_path,
                localize_linked,
            )
        )
    return stats


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean and build one Blender Asset Library."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source Asset Library, for example subspaces/O_Essentials.",
    )
    build_modes = parser.add_mutually_exclusive_group()
    build_modes.add_argument(
        "--remote",
        action="store_true",
        help="Generate and validate a deployable remote Asset Library listing.",
    )
    build_modes.add_argument(
        "--self-contained",
        action="store_true",
        help="Build a local library without external linked-library dependencies.",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Output parent directory. Defaults to the current directory.",
    )
    remote_options = parser.add_argument_group("remote options")
    remote_options.add_argument("--contact-name", default="Nan")
    remote_options.add_argument("--contact-url", default=DEFAULT_CONTACT_URL)
    remote_options.add_argument(
        "--contact-email",
        default="icrdr2010@outlook.com",
    )
    return parser.parse_args(argv)


def is_blend_backup(path: Path) -> bool:
    return bool(re.fullmatch(r".+\.blend\d+", path.name))


def should_ignore_source_path(path: Path, source: Path) -> bool:
    relative_path = path.relative_to(source)
    if any(part in IGNORED_DIRECTORY_NAMES for part in relative_path.parts):
        return True
    if path.name in IGNORED_FILES or path.name.endswith("~"):
        return True
    if path.name.startswith("blendcache_"):
        return True
    if path.name.endswith("_thumbnails"):
        return True
    return is_blend_backup(path)


def copy_sidecar_files(source: Path, destination: Path) -> None:
    for source_path in source.rglob("*"):
        if should_ignore_source_path(source_path, source):
            continue

        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue
        if source_path.suffix == ".blend":
            continue

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def iter_data_collections(blend_data: Any) -> Iterator[Any]:
    for property_definition in blend_data.bl_rna.properties:
        if property_definition.identifier == "rna_type":
            continue
        if property_definition.type != "COLLECTION":
            continue

        collection = getattr(blend_data, property_definition.identifier, None)
        if collection is not None:
            yield collection


def linked_data_blocks(blend_data: Any) -> list[Any]:
    linked: list[Any] = []
    seen_pointers: set[int] = set()

    for collection in iter_data_collections(blend_data):
        for data_block in collection:
            if getattr(data_block, "library", None) is None:
                continue

            pointer = data_block.as_pointer()
            if pointer in seen_pointers:
                continue
            seen_pointers.add(pointer)
            linked.append(data_block)
    return linked


def asset_data_blocks(blend_data: Any) -> list[Any]:
    assets: list[Any] = []
    seen_pointers: set[int] = set()

    for collection in iter_data_collections(blend_data):
        for data_block in collection:
            if getattr(data_block, "asset_data", None) is None:
                continue

            pointer = data_block.as_pointer()
            if pointer in seen_pointers:
                continue
            seen_pointers.add(pointer)
            assets.append(data_block)
    return assets


def local_asset_data_blocks(blend_data: Any) -> list[Any]:
    return [
        data_block
        for data_block in asset_data_blocks(blend_data)
        if getattr(data_block, "library", None) is None
    ]


def describe_data_blocks(data_blocks: Iterable[Any]) -> str:
    descriptions = []
    for data_block in data_blocks:
        data_type = data_block.bl_rna.identifier
        descriptions.append(f"{data_type}:{data_block.name_full}")
    return ", ".join(descriptions)


def linked_data_key(data_block: Any) -> tuple[int, str, str]:
    return (
        data_block.library.as_pointer(),
        data_block.bl_rna.identifier,
        data_block.name,
    )


def make_linked_data_local(blend_data: Any) -> int:
    local_data_by_key: dict[tuple[int, str, str], Any] = {}
    previous_pointers: set[int] | None = None

    while linked := linked_data_blocks(blend_data):
        current_pointers = {data_block.as_pointer() for data_block in linked}
        unresolved = [
            data_block
            for data_block in linked
            if linked_data_key(data_block) not in local_data_by_key
        ]
        if not unresolved:
            for data_block in linked:
                local_data_block = local_data_by_key[
                    linked_data_key(data_block)
                ]
                data_block.user_remap(local_data_block)
            linked_users = blend_data.user_map(subset=set(linked))
            local_users = [
                user
                for users in linked_users.values()
                for user in users
                if getattr(user, "library", None) is None
            ]
            if local_users:
                descriptions = describe_data_blocks(local_users)
                raise BuildError(
                    f"Local data still uses linked data: {descriptions}"
                )
            break
        if current_pointers == previous_pointers:
            descriptions = describe_data_blocks(linked)
            raise BuildError(
                f"Unable to make linked data local: {descriptions}"
            )
        previous_pointers = current_pointers

        failures: list[str] = []
        linked.sort(key=lambda data_block: data_block.is_library_indirect)
        for data_block in linked:
            key = linked_data_key(data_block)
            local_data_block = local_data_by_key.get(key)
            if local_data_block is not None:
                data_block.user_remap(local_data_block)
                continue

            try:
                local_data_block = data_block.make_local(
                    clear_asset_data=True
                )
                if local_data_block.library is None:
                    local_data_by_key[key] = local_data_block
            except RuntimeError as error:
                failures.append(f"{data_block.name_full}: {error}")

        if failures:
            details = "; ".join(failures)
            raise BuildError(f"Failed to make linked data local: {details}")

    return len(local_data_by_key)


def reset_scenes(bpy: Any) -> int:
    blend_data = bpy.data
    old_scenes = tuple(blend_data.scenes)
    clean_scene = blend_data.scenes.new("__CleanScene__")
    for window in bpy.context.window_manager.windows:
        window.scene = clean_scene
    for scene in old_scenes:
        blend_data.scenes.remove(scene, do_unlink=True)
    clean_scene.name = "Scene"
    return len(old_scenes)


def remove_library_records(blend_data: Any) -> int:
    libraries = tuple(blend_data.libraries)
    for library in libraries:
        blend_data.libraries.remove(library, do_unlink=True)
    return len(libraries)


def localize_linked_data(blend_data: Any) -> BuildStats:
    stats = BuildStats(
        linked_data=make_linked_data_local(blend_data),
        libraries=remove_library_records(blend_data),
    )
    remaining_linked = linked_data_blocks(blend_data)
    if remaining_linked:
        descriptions = describe_data_blocks(remaining_linked)
        raise BuildError(
            f"Linked data remains after localization: {descriptions}"
        )
    if blend_data.libraries:
        raise BuildError("Linked library records remain after localization.")
    return stats


def library_paths(blend_data: Any) -> tuple[str, ...]:
    return tuple(sorted(library.filepath for library in blend_data.libraries))


def validate_saved_file(
    bpy: Any,
    destination: Path,
    expected_assets: int,
    expected_library_paths: tuple[str, ...] | None,
) -> None:
    bpy.ops.wm.open_mainfile(filepath=str(destination), load_ui=False)

    if len(bpy.data.scenes) != 1 or bpy.data.scenes[0].name != "Scene":
        raise BuildError(
            f"Saved file does not contain one clean scene: {destination}"
        )
    clean_scene = bpy.data.scenes[0]
    if clean_scene.objects or clean_scene.collection.children:
        raise BuildError(f"Saved scene is not empty: {destination}")
    actual_library_paths = library_paths(bpy.data)
    if expected_library_paths is None and actual_library_paths:
        raise BuildError(
            f"Saved file still contains linked libraries: {destination}"
        )
    if (
        expected_library_paths is not None
        and actual_library_paths != expected_library_paths
    ):
        raise BuildError(
            f"Linked library paths changed while saving {destination}: "
            f"expected {expected_library_paths}, found {actual_library_paths}"
        )

    if expected_library_paths is None:
        remaining_linked = linked_data_blocks(bpy.data)
        if remaining_linked:
            descriptions = describe_data_blocks(remaining_linked)
            raise BuildError(
                f"Saved file still contains linked data: {descriptions}"
            )

    actual_assets = len(local_asset_data_blocks(bpy.data))
    if actual_assets != expected_assets:
        raise BuildError(
            f"Asset count changed while saving {destination}: "
            f"expected {expected_assets}, found {actual_assets}"
        )


def clean_blend_file(
    bpy: Any,
    source: Path,
    destination: Path,
    keep_linked: bool,
) -> BuildStats:
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)

    stats = BuildStats(scenes=reset_scenes(bpy))
    if not keep_linked:
        stats.linked_data = make_linked_data_local(bpy.data)
    stats.purged_data = bpy.data.orphans_purge(
        do_local_ids=True,
        do_linked_ids=True,
        do_recursive=True,
    )

    expected_library_paths: tuple[str, ...] | None = None
    if keep_linked:
        stats.linked_data = len(linked_data_blocks(bpy.data))
        stats.libraries = len(bpy.data.libraries)
        expected_library_paths = library_paths(bpy.data)
    else:
        stats.libraries = remove_library_records(bpy.data)
        stats.purged_data += bpy.data.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True,
        )
        if bpy.data.libraries:
            raise BuildError("Linked library records remain after cleanup.")
        remaining_linked = linked_data_blocks(bpy.data)
        if remaining_linked:
            descriptions = describe_data_blocks(remaining_linked)
            raise BuildError(
                f"Linked data remains after cleanup: {descriptions}"
            )

    stats.assets = len(local_asset_data_blocks(bpy.data))
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(
        filepath=str(destination),
        check_existing=False,
        relative_remap=not keep_linked,
    )
    validate_saved_file(
        bpy,
        destination,
        stats.assets,
        expected_library_paths,
    )
    return stats


def run_cleanup(
    bpy: Any,
    source: Path,
    staging_dir: Path,
    keep_linked: bool,
) -> BuildStats:
    blend_files = sorted(source.rglob("*.blend"))
    stats = BuildStats(blend_files=len(blend_files))
    for source_path in blend_files:
        relative_path = source_path.relative_to(source)
        destination_path = staging_dir / relative_path
        print(f"Cleaning: {relative_path}")
        stats.merge(
            clean_blend_file(
                bpy,
                source_path,
                destination_path,
                keep_linked,
            )
        )
    return stats


def generate_listing(blender: Path, library_dir: Path) -> None:
    command = [
        str(blender),
        "--factory-startup",
        "-b",
        "-c",
        "asset_listing",
        "generate",
        str(library_dir),
    ]
    print(f"Generating remote listing: {library_dir}")
    subprocess.run(command, check=True)


def update_library_metadata(
    library_dir: Path,
    library_name: str,
    contact_name: str,
    contact_url: str,
    contact_email: str,
) -> None:
    metadata_path = library_dir / "_asset-library-meta.json"
    metadata = read_json(metadata_path)
    metadata["name"] = library_name.replace("_", " ")
    metadata["contact"] = {
        "name": contact_name,
        "url": contact_url,
        "email": contact_email,
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise BuildError(f"Generated file is missing: {path}") from error
    except json.JSONDecodeError as error:
        raise BuildError(
            f"Generated JSON is invalid: {path}: {error}"
        ) from error


def sha256_reference(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"SHA256:{digest.hexdigest()}"


def validate_hash(root: Path, relative_url: str, expected_hash: str) -> Path:
    path = root.joinpath(*Path(relative_url).parts)
    if not path.is_file():
        raise BuildError(f"Listed file is missing: {path}")
    actual_hash = sha256_reference(path)
    if actual_hash != expected_hash:
        raise BuildError(f"Hash mismatch: {path}")
    return path


def validate_listing(library_dir: Path) -> tuple[int, int, int]:
    metadata = read_json(library_dir / "_asset-library-meta.json")
    version_link = metadata.get("api_versions", {}).get("v1")
    if not isinstance(version_link, dict):
        raise BuildError(f"Missing v1 API metadata: {library_dir}")

    index_path = validate_hash(
        library_dir,
        version_link["url"],
        version_link["hash"],
    )
    index = read_json(index_path)
    if index.get("schema_version") != "1.0.0":
        raise BuildError(f"Unsupported listing schema in: {index_path}")

    assets_checked = 0
    files_checked: set[str] = set()
    thumbnails_checked: set[str] = set()
    for page_link in index.get("pages", []):
        page_path = validate_hash(
            library_dir,
            page_link["url"],
            page_link["hash"],
        )
        page = read_json(page_path)
        assets_checked += len(page.get("assets", []))

        for file_info in page.get("files", []):
            relative_path = file_info["path"]
            if relative_path not in files_checked:
                validate_hash(library_dir, relative_path, file_info["hash"])
                files_checked.add(relative_path)

        for asset in page.get("assets", []):
            thumbnail = asset.get("thumbnail")
            if not thumbnail or thumbnail["url"] in thumbnails_checked:
                continue
            validate_hash(library_dir, thumbnail["url"], thumbnail["hash"])
            thumbnails_checked.add(thumbnail["url"])

    if assets_checked != index.get("asset_count"):
        raise BuildError(f"Asset count mismatch: {library_dir}")
    if len(files_checked) != index.get("file_count"):
        raise BuildError(f"File count mismatch: {library_dir}")
    return assets_checked, len(files_checked), len(thumbnails_checked)


def paths_overlap(first: Path, second: Path) -> bool:
    return (
        first == second
        or first.is_relative_to(second)
        or second.is_relative_to(first)
    )


def arguments_after_separator(argv: list[str]) -> list[str]:
    if "--" not in argv:
        return []
    return argv[argv.index("--") + 1:]


def commit_staging_directory(staging_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    staging_dir.replace(target_dir)


def print_build_summary(
    target_dir: Path,
    remote: bool,
    keep_linked: bool,
    stats: BuildStats,
    remote_totals: tuple[int, int, int] | None,
) -> None:
    mode = "remote" if remote else "local"
    print(f"\nBuilt {mode} Asset Library: {target_dir}")
    print(f"- {stats.blend_files} blend files cleaned")
    print(f"- {stats.versioned_assets} versioned assets composed")
    linked_action = "preserved" if keep_linked else "made local"
    print(f"- {stats.linked_data} linked data-blocks {linked_action}")
    print(f"- {stats.scenes} scenes replaced")
    print(f"- {stats.purged_data} unused data-blocks purged")
    library_action = "preserved" if keep_linked else "removed"
    print(f"- {stats.libraries} linked library records {library_action}")
    print(f"- {stats.assets} assets preserved")
    if remote_totals is None:
        return

    asset_count, file_count, thumbnail_count = remote_totals
    print(
        f"- remote listing: {asset_count} assets, "
        f"{file_count} blend files, {thumbnail_count} thumbnails"
    )


def build(args: argparse.Namespace) -> None:
    try:
        import bpy
    except ModuleNotFoundError as error:
        raise BuildError(
            "Run build_assets.py with Blender: "
            "blender --background --python build_assets.py -- <source>"
        ) from error

    if args.remote and args.self_contained:
        raise BuildError("--remote and --self-contained cannot be used together.")

    keep_linked = not args.remote and not args.self_contained

    source = args.source.expanduser().resolve()
    if not source.is_dir():
        raise BuildError(f"Asset Library directory does not exist: {source}")

    target_version = tuple(bpy.app.version[:2])
    blender = Path(bpy.app.binary_path).resolve()

    output_dir = args.out.expanduser().resolve()
    target_name = source.name
    target_dir = output_dir / target_name
    if paths_overlap(source, target_dir):
        raise BuildError(
            "Source and destination Asset Library directories must not overlap."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    compose_dir = output_dir / f".{target_name}.compose-{uuid.uuid4().hex}"
    staging_dir = output_dir / f".{target_name}.tmp-{uuid.uuid4().hex}"
    compose_dir.mkdir()
    staging_dir.mkdir()

    stats = BuildStats()
    remote_totals: tuple[int, int, int] | None = None
    try:
        copy_sidecar_files(source, staging_dir)
        stats.merge(
            compose_library(
                bpy,
                source,
                compose_dir,
                target_version,
                not keep_linked,
            )
        )
        stats.merge(
            run_cleanup(
                bpy,
                compose_dir,
                staging_dir,
                keep_linked,
            )
        )

        if args.remote:
            generate_listing(blender, staging_dir)
            update_library_metadata(
                staging_dir,
                source.name,
                args.contact_name,
                args.contact_url,
                args.contact_email,
            )
            remote_totals = validate_listing(staging_dir)

        commit_staging_directory(staging_dir, target_dir)
    except Exception:
        if compose_dir.exists():
            shutil.rmtree(compose_dir)
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise
    else:
        shutil.rmtree(compose_dir)

    print_build_summary(
        target_dir,
        args.remote,
        keep_linked,
        stats,
        remote_totals,
    )


def main() -> int:
    try:
        build(parse_arguments(arguments_after_separator(sys.argv)))
    except (
        BuildError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
