from pathlib import Path


from tools.nodes.publication import (
    BuildError,
    BuildStats,
    copy_sidecar_files,
    is_blend_backup,
    linked_data_key,
    sha256_reference,
    update_library_metadata,
)


def test_build_stats_merge() -> None:
    totals = BuildStats(blend_files=1, linked_data=2, assets=3)

    totals.merge(
        BuildStats(
            linked_data=5,
            scenes=6,
            purged_data=7,
            libraries=8,
            assets=9,
        )
    )

    assert totals == BuildStats(
        blend_files=1,
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
    (source / ".nodes.json").write_text("{}", encoding="utf-8")
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
    assert not (destination / ".nodes.json").exists()
    assert not (destination / "_v1").exists()
    assert not (destination / "blender_assets.cats.txt~").exists()




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












