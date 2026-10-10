"""Select complete sources and merge version exports."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

VERSIONS = ("b45", "b52")


def select_sources(source: Path, destination: Path, version: str) -> None:
    if version not in VERSIONS:
        raise ValueError(f"Unsupported target: {version}")
    selected: dict[Path, Path] = {}
    for path in sorted(source.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        if path.name.endswith(".b52.py"):
            if version == "b52":
                selected[relative.with_name(path.name.removesuffix(".b52.py") + ".py")] = path
            continue
        if ".b" in path.name and path.suffix == ".py":
            raise ValueError(f"Unsupported version suffix: {path}")
        selected.setdefault(relative, path)
    for relative, path in selected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def source_digest(source: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(source.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(source).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def merge_exports(base: Path, updated: dict[str, Path], destination: Path) -> None:
    """Write edits to their existing source definition; never create implicit variants."""
    shutil.copytree(base, destination)
    changes = {}
    for version, root in updated.items():
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            relative = path.relative_to(root)
            specialized = relative.with_name(relative.stem + ".b52.py")
            origin = specialized if version == "b52" and (base / specialized).is_file() else relative
            value = path.read_bytes()
            if (base / origin).is_file() and (base / origin).read_bytes() == value:
                continue
            if origin in changes and changes[origin] != value:
                raise ValueError(f"Conflicting edits to shared source: {origin}")
            changes[origin] = value
    for relative, value in changes.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    resources = {path.relative_to(root) for root in updated.values()
                 for path in root.rglob("*") if path.is_file() and "resources" in path.relative_to(root).parts}
    for relative in sorted(resources):
        original = base / relative
        before = original.read_bytes() if original.exists() else None
        contents = {(root / relative).read_bytes() if (root / relative).exists() else None
                    for root in updated.values()}
        contents.discard(before)
        if not contents:
            continue
        if len(contents) != 1:
            raise ValueError(f"Shared resource conflict: {relative}")
        value = contents.pop()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if value is not None:
            target.write_bytes(value)
