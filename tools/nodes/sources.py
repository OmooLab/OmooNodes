"""Select target sources and reconcile exported modules with their owners."""

from __future__ import annotations

import ast
import shutil
from pathlib import Path

from .runtimes import TARGETS


def select_sources(source: Path, destination: Path, version: str) -> None:
    if version not in TARGETS:
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


def overwrite_sources(source: Path, exported: Path, version: str) -> None:
    """Replace generated Python and resources, retaining other target variants."""
    if version not in TARGETS:
        raise ValueError(f"Unsupported target: {version}")
    variants = {path.relative_to(source).with_name(path.name.removesuffix(".b52.py") + ".py")
                for path in source.rglob("*.b52.py")}
    for path in source.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        if "resources" in relative.parts:
            path.unlink()
        elif path.suffix == ".py":
            if version != "b52" and path.name.endswith(".b52.py"):
                continue
            if version == "b52" and relative in variants and (exported / relative).is_file():
                continue
            path.unlink()
    for path in exported.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(exported)
        if path.suffix != ".py" and "resources" not in relative.parts:
            continue
        if version == "b52" and relative in variants:
            relative = relative.with_name(relative.stem + ".b52.py")
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def rewrite_foreign_modules(root, imports):
    """Replace dumped foreign class copies with imports from their owner."""
    forwarded = {}
    trees = {}
    removable = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf8"))
        replacements = {}
        kept = []
        for statement in tree.body:
            if isinstance(statement, ast.ClassDef):
                names = [ast.literal_eval(item.value) for item in statement.body
                         if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_name" for t in item.targets)]
                if names and names[0] in imports:
                    replacements[statement.name] = imports[names[0]]
                    forwarded[(path.resolve(), statement.name)] = imports[names[0]]
                    continue
            kept.append(statement)
        if replacements:
            if not any(isinstance(item, ast.ClassDef) for item in kept) and path.name != "__init__.py":
                removable.append(path)
                continue
            for alias, owner in replacements.items():
                kept.insert(0, ast.ImportFrom(module=owner["module"], names=[ast.alias(name=owner["class"], asname=alias)], level=0))
            tree.body = kept
        trees[path] = tree
    for path, tree in trees.items():
        original = ast.dump(ast.parse(path.read_text(encoding="utf8")))
        body = []
        for statement in tree.body:
            if not isinstance(statement, ast.ImportFrom) or not statement.level:
                body.append(statement)
                continue
            parent = path.parent
            for _ in range(statement.level - 1):
                parent = parent.parent
            module_path = parent.joinpath(*(statement.module or "").split(".")).with_suffix(".py").resolve()
            remaining = []
            for alias in statement.names:
                owner = forwarded.get((module_path, alias.name))
                if owner:
                    body.append(ast.ImportFrom(module=owner["module"], level=0,
                                               names=[ast.alias(name=owner["class"], asname=alias.asname or alias.name)]))
                else:
                    remaining.append(alias)
            if remaining:
                statement.names = remaining
                body.append(statement)
        tree.body = body
        if ast.dump(tree) != original:
            path.write_text(ast.unparse(tree) + "\n", encoding="utf8")
    for path in removable:
        path.unlink()
