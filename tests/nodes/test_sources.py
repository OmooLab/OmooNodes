import ast
from pathlib import Path

import pytest

from tools.nodes import sources
from tools.nodes.sources import overwrite_sources, select_sources


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


def test_foreign_shared_class_is_imported_from_owner_without_forwarding_file(tmp_path):
    root = tmp_path / "sources"
    shared = root / "geometry/_shared"
    shared.mkdir(parents=True)
    (shared / "helper.py").write_text("class Helper:\n    _name = 'Public Helper'\n", encoding="utf8")
    asset = root / "geometry/asset.py"
    asset.write_text("from ._shared.helper import Helper\nclass Asset:\n    _name = 'Asset'\n", encoding="utf8")
    sources.rewrite_foreign_modules(root, {"Public Helper": {"module": "nodes.Owner.geometry.helper", "class": "Helper"}})
    assert not (shared / "helper.py").exists()
    statements = ast.parse(asset.read_text()).body
    assert isinstance(statements[0], ast.ImportFrom)
    assert statements[0].module == "nodes.Owner.geometry.helper"
    assert statements[0].names[0].asname == "Helper"
    assert statements[1].name == "Asset"


def test_foreign_rewrite_keeps_untouched_comments_and_format(tmp_path):
    source = tmp_path / "asset.py"
    original = "# Authored comment\nclass Asset:\n    _name = \"Asset\"\n"
    source.write_text(original)
    sources.rewrite_foreign_modules(tmp_path, {})
    assert source.read_text() == original


@pytest.mark.parametrize("version", ["b45", "b52"])
def test_overwrite_sources_replaces_python_resources_and_existing_variant(tmp_path, version):
    source = tmp_path / "source"
    exported = tmp_path / "exported"
    write(source, "a.py", "common")
    write(source, "a.b52.py", "specialized")
    write(source, "removed.py", "stale")
    write(source, "resources/old.png", "old image")
    write(source, "collection.json", "manifest")
    write(exported, "a.py", "edited")
    write(exported, "new.py", "new asset")
    write(exported, "resources/new.png", "new image")
    overwrite_sources(source, exported, version)
    assert (source / "a.py").read_text() == ("common" if version == "b52" else "edited")
    assert (source / "a.b52.py").read_text() == ("edited" if version == "b52" else "specialized")
    assert not (source / "removed.py").exists()
    assert not (source / "resources/old.png").exists()
    assert (source / "resources/new.png").read_text() == "new image"
    assert (source / "new.py").read_text() == "new asset"
    assert (source / "collection.json").read_text() == "manifest"
