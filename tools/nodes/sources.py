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


def merge_exports(base: Path, updated: dict[str, Path], destination: Path, targets=VERSIONS) -> None:
    """Merge complete modules; callers validate their logical equivalence first."""
    shutil.copytree(base, destination)
    files = {path.relative_to(root) for root in updated.values()
             for path in root.rglob("*.py") if "__pycache__" not in path.parts}
    for relative in sorted(files):
        generic = destination / relative
        specialized = generic.with_name(generic.stem + ".b52.py")
        old45 = generic.read_bytes() if generic.exists() else None
        old52 = specialized.read_bytes() if specialized.exists() else old45
        contents = {version: (root / relative).read_bytes()
                    for version, root in updated.items() if (root / relative).is_file()}
        b45 = contents.get("b45", old45)
        b52 = contents.get("b52", old52)
        generic.parent.mkdir(parents=True, exist_ok=True)
        if b45 is not None:
            generic.write_bytes(b45)
        if b52 == b45:
            specialized.unlink(missing_ok=True)
        elif b52 is not None:
            specialized.write_bytes(b52)
    resources = {path.relative_to(root) for root in updated.values()
                 for path in root.rglob("*") if path.is_file() and "resources" in path.relative_to(root).parts}
    for relative in sorted(resources):
        original = base / relative
        before = original.read_bytes() if original.exists() else None
        contents = {(root / relative).read_bytes() if (root / relative).exists() else None
                    for root in updated.values()}
        if contents == {before}:
            continue
        if set(updated) != set(targets) or len(contents) != 1:
            raise ValueError(f"Shared resource conflict; synchronize the same resource in all configured targets: {relative}")
        value = contents.pop()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if value is not None:
            target.write_bytes(value)
