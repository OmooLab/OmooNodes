"""Clean complete node libraries and generate Blender remote listings."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
IGNORED_FILES = {".nodes.json", "_asset-library-meta.json", "blender_assets.cats.txt~"}
IGNORED_DIRECTORY_NAMES = {"_v1", "__pycache__"}


class BuildError(RuntimeError):
    """Raised when an Asset Library cannot be built safely."""

@dataclass
class BuildStats:
    """Counters collected while building an Asset Library."""
    blend_files: int = 0
    linked_data: int = 0
    scenes: int = 0
    purged_data: int = 0
    libraries: int = 0
    assets: int = 0

    def merge(self, other: 'BuildStats') -> None:
        self.blend_files += other.blend_files
        self.linked_data += other.linked_data
        self.scenes += other.scenes
        self.purged_data += other.purged_data
        self.libraries += other.libraries
        self.assets += other.assets

def is_blend_backup(path: Path) -> bool:
    return bool(re.fullmatch('.+\\.blend\\d+', path.name))

def should_ignore_source_path(path: Path, source: Path) -> bool:
    relative_path = path.relative_to(source)
    if any((part in IGNORED_DIRECTORY_NAMES for part in relative_path.parts)):
        return True
    if path.name in IGNORED_FILES or path.name.endswith('~'):
        return True
    if path.name.startswith('blendcache_'):
        return True
    if path.name.endswith('_thumbnails'):
        return True
    return is_blend_backup(path)

def copy_sidecar_files(source: Path, destination: Path) -> None:
    for source_path in source.rglob('*'):
        if should_ignore_source_path(source_path, source):
            continue
        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue
        if source_path.suffix == '.blend':
            continue
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

def iter_data_collections(blend_data: Any) -> Iterator[Any]:
    for property_definition in blend_data.bl_rna.properties:
        if property_definition.identifier == 'rna_type':
            continue
        if property_definition.type != 'COLLECTION':
            continue
        collection = getattr(blend_data, property_definition.identifier, None)
        if collection is not None:
            yield collection

def linked_data_blocks(blend_data: Any) -> list[Any]:
    linked: list[Any] = []
    seen_pointers: set[int] = set()
    for collection in iter_data_collections(blend_data):
        for data_block in collection:
            if getattr(data_block, 'library', None) is None:
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
            if getattr(data_block, 'asset_data', None) is None:
                continue
            pointer = data_block.as_pointer()
            if pointer in seen_pointers:
                continue
            seen_pointers.add(pointer)
            assets.append(data_block)
    return assets

def local_asset_data_blocks(blend_data: Any) -> list[Any]:
    return [data_block for data_block in asset_data_blocks(blend_data) if getattr(data_block, 'library', None) is None]

def describe_data_blocks(data_blocks: Iterable[Any]) -> str:
    descriptions = []
    for data_block in data_blocks:
        data_type = data_block.bl_rna.identifier
        descriptions.append(f'{data_type}:{data_block.name_full}')
    return ', '.join(descriptions)

def linked_data_key(data_block: Any) -> tuple[int, str, str]:
    return (data_block.library.as_pointer(), data_block.bl_rna.identifier, data_block.name)

def make_linked_data_local(blend_data: Any) -> int:
    local_data_by_key: dict[tuple[int, str, str], Any] = {}
    previous_pointers: set[int] | None = None
    while (linked := linked_data_blocks(blend_data)):
        current_pointers = {data_block.as_pointer() for data_block in linked}
        unresolved = [data_block for data_block in linked if linked_data_key(data_block) not in local_data_by_key]
        if not unresolved:
            for data_block in linked:
                local_data_block = local_data_by_key[linked_data_key(data_block)]
                data_block.user_remap(local_data_block)
            linked_users = blend_data.user_map(subset=set(linked))
            local_users = [user for users in linked_users.values() for user in users if getattr(user, 'library', None) is None]
            if local_users:
                descriptions = describe_data_blocks(local_users)
                raise BuildError(f'Local data still uses linked data: {descriptions}')
            break
        if current_pointers == previous_pointers:
            descriptions = describe_data_blocks(linked)
            raise BuildError(f'Unable to make linked data local: {descriptions}')
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
                local_data_block = data_block.make_local(clear_asset_data=True)
                if local_data_block.library is None:
                    local_data_by_key[key] = local_data_block
            except RuntimeError as error:
                failures.append(f'{data_block.name_full}: {error}')
        if failures:
            details = '; '.join(failures)
            raise BuildError(f'Failed to make linked data local: {details}')
    return len(local_data_by_key)

def reset_scenes(bpy: Any) -> int:
    blend_data = bpy.data
    old_scenes = tuple(blend_data.scenes)
    clean_scene = blend_data.scenes.new('__CleanScene__')
    for window in bpy.context.window_manager.windows:
        window.scene = clean_scene
    for scene in old_scenes:
        blend_data.scenes.remove(scene, do_unlink=True)
    clean_scene.name = 'Scene'
    return len(old_scenes)

def remove_library_records(blend_data: Any) -> int:
    libraries = tuple(blend_data.libraries)
    for library in libraries:
        blend_data.libraries.remove(library, do_unlink=True)
    return len(libraries)


def library_paths(blend_data: Any) -> tuple[str, ...]:
    return tuple(sorted((library.filepath for library in blend_data.libraries)))

def validate_saved_file(bpy: Any, destination: Path, expected_assets: int, expected_library_paths: tuple[str, ...] | None) -> None:
    bpy.ops.wm.open_mainfile(filepath=str(destination), load_ui=False)
    if len(bpy.data.scenes) != 1 or bpy.data.scenes[0].name != 'Scene':
        raise BuildError(f'Saved file does not contain one clean scene: {destination}')
    clean_scene = bpy.data.scenes[0]
    if clean_scene.objects or clean_scene.collection.children:
        raise BuildError(f'Saved scene is not empty: {destination}')
    actual_library_paths = library_paths(bpy.data)
    if expected_library_paths is None and actual_library_paths:
        raise BuildError(f'Saved file still contains linked libraries: {destination}')
    if expected_library_paths is not None and actual_library_paths != expected_library_paths:
        raise BuildError(f'Linked library paths changed while saving {destination}: expected {expected_library_paths}, found {actual_library_paths}')
    if expected_library_paths is None:
        remaining_linked = linked_data_blocks(bpy.data)
        if remaining_linked:
            descriptions = describe_data_blocks(remaining_linked)
            raise BuildError(f'Saved file still contains linked data: {descriptions}')
    actual_assets = len(local_asset_data_blocks(bpy.data))
    if actual_assets != expected_assets:
        raise BuildError(f'Asset count changed while saving {destination}: expected {expected_assets}, found {actual_assets}')

def release_compositor_storage(bpy: Any, cleanup: Path) -> None:
    """Release Blender 4.5's obsolete compositor storage through its native writer."""
    if bpy.app.version[:2] != (4, 5):
        return
    groups = {group for group in bpy.data.node_groups
              if group.library is None and group.bl_idname == "CompositorNodeTree"}
    if not any(node.bl_idname in {"CompositorNodeAntiAliasing", "CompositorNodeAlphaOver"}
               for group in groups for node in group.nodes):
        return
    # 4.5 reads legacy storage without a matching free callback; its writer frees it.
    bpy.data.libraries.write(str(cleanup), groups)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cleanup.unlink()


def clean_blend_file(bpy: Any, source: Path, destination: Path, keep_linked: bool) -> BuildStats:
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    stats = BuildStats(scenes=reset_scenes(bpy))
    if not keep_linked:
        stats.linked_data = make_linked_data_local(bpy.data)
    stats.purged_data = bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    expected_library_paths: tuple[str, ...] | None = None
    if keep_linked:
        stats.linked_data = len(linked_data_blocks(bpy.data))
        stats.libraries = len(bpy.data.libraries)
        expected_library_paths = library_paths(bpy.data)
    else:
        stats.libraries = remove_library_records(bpy.data)
        stats.purged_data += bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        if bpy.data.libraries:
            raise BuildError('Linked library records remain after cleanup.')
        remaining_linked = linked_data_blocks(bpy.data)
        if remaining_linked:
            descriptions = describe_data_blocks(remaining_linked)
            raise BuildError(f'Linked data remains after cleanup: {descriptions}')
    stats.assets = len(local_asset_data_blocks(bpy.data))
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), check_existing=False, relative_remap=not keep_linked)
    validate_saved_file(bpy, destination, stats.assets, expected_library_paths)
    # Release the reloaded file before the next file replaces Blender's data.
    release_compositor_storage(bpy, destination.with_suffix('.cleanup.blend'))
    return stats

def run_cleanup(bpy: Any, source: Path, staging_dir: Path, keep_linked: bool) -> BuildStats:
    blend_files = sorted(source.rglob('*.blend'))
    stats = BuildStats(blend_files=len(blend_files))
    for source_path in blend_files:
        relative_path = source_path.relative_to(source)
        destination_path = staging_dir / relative_path
        print(f'Cleaning: {relative_path}')
        stats.merge(clean_blend_file(bpy, source_path, destination_path, keep_linked))
    return stats

def update_library_metadata(library_dir: Path, library_name: str, contact_name: str, contact_url: str, contact_email: str) -> None:
    metadata_path = library_dir / '_asset-library-meta.json'
    metadata = read_json(metadata_path)
    metadata['name'] = library_name.replace('_', ' ')
    metadata['contact'] = {'name': contact_name, 'url': contact_url, 'email': contact_email}
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as error:
        raise BuildError(f'Generated file is missing: {path}') from error
    except json.JSONDecodeError as error:
        raise BuildError(f'Generated JSON is invalid: {path}: {error}') from error

def sha256_reference(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return f'SHA256:{digest.hexdigest()}'

def validate_hash(root: Path, relative_url: str, expected_hash: str) -> Path:
    path = root.joinpath(*Path(relative_url).parts)
    if not path.is_file():
        raise BuildError(f'Listed file is missing: {path}')
    actual_hash = sha256_reference(path)
    if actual_hash != expected_hash:
        raise BuildError(f'Hash mismatch: {path}')
    return path

def validate_listing(library_dir: Path) -> tuple[int, int, int]:
    metadata = read_json(library_dir / '_asset-library-meta.json')
    version_link = metadata.get('api_versions', {}).get('v1')
    if not isinstance(version_link, dict):
        raise BuildError(f'Missing v1 API metadata: {library_dir}')
    index_path = validate_hash(library_dir, version_link['url'], version_link['hash'])
    index = read_json(index_path)
    if index.get('schema_version') != '1.0.0':
        raise BuildError(f'Unsupported listing schema in: {index_path}')
    assets_checked = 0
    files_checked: set[str] = set()
    thumbnails_checked: set[str] = set()
    for page_link in index.get('pages', []):
        page_path = validate_hash(library_dir, page_link['url'], page_link['hash'])
        page = read_json(page_path)
        assets_checked += len(page.get('assets', []))
        for file_info in page.get('files', []):
            relative_path = file_info['path']
            if relative_path not in files_checked:
                validate_hash(library_dir, relative_path, file_info['hash'])
                files_checked.add(relative_path)
        for asset in page.get('assets', []):
            thumbnail = asset.get('thumbnail')
            if not thumbnail or thumbnail['url'] in thumbnails_checked:
                continue
            validate_hash(library_dir, thumbnail['url'], thumbnail['hash'])
            thumbnails_checked.add(thumbnail['url'])
    if assets_checked != index.get('asset_count'):
        raise BuildError(f'Asset count mismatch: {library_dir}')
    if len(files_checked) != index.get('file_count'):
        raise BuildError(f'File count mismatch: {library_dir}')
    return (assets_checked, len(files_checked), len(thumbnails_checked))


def publish_library(bpy, source, output, remote=False, self_contained=False, contact=None):
    output.mkdir(parents=True)
    copy_sidecar_files(source, output)
    stats = run_cleanup(bpy, source, output, keep_linked=not (remote or self_contained))
    if remote:
        # Blender's versioned module defines the native repository schema.
        from _bpy_internal.assets.remote_library.cli_listing_generator import cli_main
        cli_main(argparse.Namespace(repository=output, limit=0, page=0))
        metadata = read_json(output / "_asset-library-meta.json")
        details = {**metadata["contact"], **(contact or {})}
        update_library_metadata(output, output.name, details["name"], details["url"], details["email"])
        assets, _, _ = validate_listing(output)
        if assets != stats.assets:
            raise BuildError(f"Remote asset count changed: {assets} != {stats.assets}")
    return stats
