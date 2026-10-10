from pathlib import Path

import pytest

from nodes_tool.sources import apply_changes, select_sources


def write(root: Path, name: str, content: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf8")


def test_select_versions_preserves_dependencies_and_specialized_precedence(tmp_path):
    source = tmp_path / "sources"
    write(source, "geometry/a.py", "common")
    write(source, "geometry/a.b52.py", "special")
    write(source, "geometry/new.b52.py", "new")
    write(source, "geometry/_shared/helper.py", "helper")
    write(source, "geometry/__pycache__/old.pyc", "stale")
    write(source, "collection.json", "{}")
    select_sources(source, tmp_path / "b45", "b45")
    select_sources(source, tmp_path / "b52", "b52")
    assert (tmp_path / "b45/geometry/a.py").read_text() == "common"
    assert not (tmp_path / "b45/geometry/new.py").exists()
    assert (tmp_path / "b52/geometry/a.py").read_text() == "special"
    assert (tmp_path / "b52/geometry/new.py").read_text() == "new"
    assert (tmp_path / "b52/geometry/_shared/helper.py").read_text() == "helper"
    assert not list((tmp_path / "b52").rglob("*.b52.py"))
    assert not (tmp_path / "b52/geometry/__pycache__").exists()


def test_unknown_version_cannot_silently_select_sources(tmp_path):
    with pytest.raises(ValueError, match="Unsupported target"):
        select_sources(tmp_path, tmp_path / "out", "b53")


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_apply_edits_preserves_unedited_code_and_targets_existing_variant(tmp_path, version):
    source, before, after = (tmp_path / name for name in ("source", "before", "after"))
    for root in (source, before, after):
        write(root, "a.py", "original")
        write(root, "untouched.py", "native_export")
    write(source, "untouched.py", "# Authored code")
    write(source, "a.b52.py", "specific")
    write(after, "a.py", "edited")
    write(after, "new.py", "new asset")
    apply_changes(source, before, after, version)
    assert (source / "untouched.py").read_text() == "# Authored code"
    assert (source / "a.py").read_text() == ("original" if version == "b52" else "edited")
    assert (source / "a.b52.py").read_text() == ("edited" if version == "b52" else "specific")
    assert (source / "new.py").read_text() == "new asset"


def test_b52_deletion_is_explicitly_disabled(tmp_path):
    source, before, after = (tmp_path / name for name in ("source", "before", "after"))
    write(source, "a.py", "shared")
    write(before, "a.py", "native_export")
    after.mkdir()
    apply_changes(source, before, after, "b52")
    assert (source / "a.py").read_text() == "shared"
    assert (source / "a.b52.py").read_text() == "DISABLED = True\n"


def test_sync_keeps_authored_filename(tmp_path):
    source, before, after = (tmp_path / name for name in ("source", "before", "after"))
    definition = "class Example(CustomGeometryGroup):\n    _name = 'My Group'\n"
    write(source, "authored.py", definition + "    # Original authoring\n")
    write(before, "geometry/my_group.py", definition)
    write(after, "geometry/my_group.py", definition + "    _description = 'Edited'\n")
    apply_changes(source, before, after, "b52")
    assert "Edited" in (source / "authored.py").read_text()
    assert list(source.rglob("*.py")) == [source / "authored.py"]
