from pathlib import Path

import pytest

from build_assets import (
    BuildError,
    BuildStats,
    arguments_after_separator,
    copy_sidecar_files,
    discover_blend_layers,
    is_blend_backup,
    linked_data_key,
    parse_arguments,
    paths_overlap,
    sha256_reference,
    update_library_metadata,
    versioned_blend_info,
)


def test_build_stats_merge() -> None:
    totals = BuildStats(blend_files=1, linked_data=2, assets=3)

    totals.merge(
        BuildStats(
            versioned_assets=4,
            linked_data=5,
            scenes=6,
            purged_data=7,
            libraries=8,
            assets=9,
        )
    )

    assert totals == BuildStats(
        blend_files=1,
        versioned_assets=4,
        linked_data=7,
        scenes=6,
        purged_data=7,
        libraries=8,
        assets=12,
    )


def test_is_blend_backup() -> None:
    assert is_blend_backup(Path("library.blend1"))
    assert is_blend_backup(Path("library.blend12"))
    assert not is_blend_backup(Path("library.blend"))
    assert not is_blend_backup(Path("library.blend-old"))


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


def test_paths_overlap() -> None:
    source = Path("C:/workspace/subspaces/b52/O_Extra")

    assert paths_overlap(source, source)
    assert paths_overlap(source, source / "nested")
    assert not paths_overlap(source, Path("C:/workspace/contents/b52/O_Extra"))


def test_linked_data_key_identifies_the_original_data_block() -> None:
    class FakeRna:
        identifier = "GeometryNodeTree"

    class FakeLibrary:
        def as_pointer(self) -> int:
            return 42

    class FakeDataBlock:
        library = FakeLibrary()
        bl_rna = FakeRna()
        name = "O Displace"

    assert linked_data_key(FakeDataBlock()) == (
        42,
        "GeometryNodeTree",
        "O Displace",
    )


def test_sha256_reference(tmp_path: Path) -> None:
    source = tmp_path / "asset.blend"
    source.write_bytes(b"asset")

    assert sha256_reference(source) == (
        "SHA256:d59386e0ae435e292fbe0ebcdb954b75"
        "ed5fb3922091277cb19f798fc5d50718"
    )


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


def test_arguments_after_separator() -> None:
    assert arguments_after_separator(
        ["blender.exe", "--background", "--", "source", "--remote"]
    ) == ["source", "--remote"]
    assert arguments_after_separator(["build_assets.py", "source"]) == []


def test_versioned_blend_info() -> None:
    assert versioned_blend_info(Path("GeometryNodes.b52.blend")) == (
        "GeometryNodes",
        (5, 2),
    )
    assert versioned_blend_info(Path("GeometryNodes.b410.blend")) == (
        "GeometryNodes",
        (4, 10),
    )
    assert versioned_blend_info(Path("GeometryNodes.blend")) is None


def test_discover_blend_layers_selects_compatible_overlays(
    tmp_path: Path,
) -> None:
    source = tmp_path / "O_Essentials"
    source.mkdir()
    base = source / "GeometryNodes.blend"
    b45 = source / "GeometryNodes.b45.blend"
    b52 = source / "GeometryNodes.b52.blend"
    for path in (base, b45, b52):
        path.write_bytes(b"blend")

    layers = discover_blend_layers(source, (4, 7))

    assert len(layers) == 1
    assert layers[0].base == base
    assert layers[0].overlays == (b45,)


def test_discover_blend_layers_rejects_overlay_without_base(
    tmp_path: Path,
) -> None:
    source = tmp_path / "O_Essentials"
    source.mkdir()
    (source / "GeometryNodes.b52.blend").write_bytes(b"blend")

    with pytest.raises(BuildError, match="no base"):
        discover_blend_layers(source, (5, 2))


def test_remote_and_self_contained_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit) as error:
        parse_arguments(["source", "--remote", "--self-contained"])

    assert error.value.code == 2


def test_local_build_preserves_links_by_default() -> None:
    arguments = parse_arguments(["source"])

    assert arguments.remote is False
    assert arguments.self_contained is False
