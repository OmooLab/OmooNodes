from pathlib import Path

import pytest

from tools.nodes.sources import merge_exports, select_sources, source_digest


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


def test_merge_one_version_preserves_other_version_then_deduplicates(tmp_path):
    base = tmp_path / "base"
    write(base, "a.py", "original")
    edited = tmp_path / "edited"
    write(edited, "a.py", "changed")
    split = tmp_path / "split"
    merge_exports(base, {"b52": edited}, split)
    assert (split / "a.py").read_text() == "original"
    assert (split / "a.b52.py").read_text() == "changed"
    merged = tmp_path / "merged"
    merge_exports(split, {"b45": edited}, merged)
    assert (merged / "a.py").read_text() == "changed"
    assert not (merged / "a.b52.py").exists()


def test_b52_only_stays_specialized_and_digest_detects_source_changes(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    edited = tmp_path / "edited"
    write(edited, "new.py", "new")
    output = tmp_path / "output"
    merge_exports(base, {"b52": edited}, output)
    assert not (output / "new.py").exists()
    assert (output / "new.b52.py").read_text() == "new"
    before = source_digest(output)
    write(output, "new.b52.py", "modified")
    assert before != source_digest(output)


def test_unknown_version_cannot_silently_select_sources(tmp_path):
    with pytest.raises(ValueError, match="Unsupported target"):
        select_sources(tmp_path, tmp_path / "out", "b53")



def test_shared_resources_require_matching_edits_in_both_versions(tmp_path):
    base = tmp_path / "base"
    write(base, "resources/images.json", "original")
    old = tmp_path / "old"
    new = tmp_path / "new"
    write(old, "resources/images.json", "original")
    write(new, "resources/images.json", "changed")
    with pytest.raises(ValueError, match="Shared resource conflict"):
        merge_exports(base, {"b45": old, "b52": new}, tmp_path / "rejected")
    assert (base / "resources/images.json").read_text() == "original"
    output = tmp_path / "accepted"
    merge_exports(base, {"b45": new, "b52": new}, output)
    assert (output / "resources/images.json").read_text() == "changed"



def test_shared_resource_can_change_when_project_only_declares_one_target(tmp_path):
    base = tmp_path / "base"
    write(base, "resources/images.json", "old")
    edited = tmp_path / "edited"
    write(edited, "resources/images.json", "new")
    output = tmp_path / "output"
    merge_exports(base, {"b45": edited}, output, targets=("b45",))
    assert (output / "resources/images.json").read_text() == "new"
