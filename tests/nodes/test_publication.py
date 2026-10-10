from pathlib import Path


from tools.nodes.publication import (
    copy_sidecar_files,
    update_library_metadata,
)


def test_copy_sidecar_files_excludes_generated_and_backup_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    nested = source / "nested"
    listing = source / "_v1"
    nested.mkdir(parents=True)
    listing.mkdir()
    (source / "library.blend").write_bytes(b"blend")
    (source / "library.blend1").write_bytes(b"backup")
    (source / "_asset-library-meta.json").write_text("{}", encoding="utf-8")
    (listing / "index.json").write_text("{}", encoding="utf-8")
    (source / "blender_assets.cats.txt~").write_text("backup", encoding="utf-8")
    (nested / "blender_assets.cats.txt").write_text("catalog", encoding="utf-8")

    copy_sidecar_files(source, destination)

    assert (destination / "nested" / "blender_assets.cats.txt").read_text(
        encoding="utf-8"
    ) == "catalog"
    assert not (destination / "library.blend").exists()
    assert not (destination / "library.blend1").exists()
    assert not (destination / "_asset-library-meta.json").exists()
    assert not (destination / "_v1").exists()
    assert not (destination / "blender_assets.cats.txt~").exists()


def test_update_library_metadata_uses_source_library_name(
    tmp_path: Path,
) -> None:
    staging = tmp_path / ".Stanford 3D Scanning.tmp-build-id"
    staging.mkdir()
    metadata = staging / "_asset-library-meta.json"
    metadata.write_text("{}", encoding="utf-8")

    update_library_metadata(
        staging,
        "Stanford 3D Scanning",
        "OmooLab",
        "https://example.com",
        "assets@example.com",
    )

    result = metadata.read_text(encoding="utf-8")
    assert '"name": "Stanford 3D Scanning"' in result
    assert ".tmp-" not in result
