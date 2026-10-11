"""Select target modules and apply only edited native definitions."""

import ast
import shutil

from .runtimes import TARGETS


def select_sources(source, destination, version):
    if version not in TARGETS:
        raise ValueError(f"Unsupported target: {version}")
    selected = {}
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
    destination.mkdir(parents=True, exist_ok=True)
    for relative, path in selected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def source_files(root):
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
            and (path.suffix == ".py" or "resources" in path.relative_to(root).parts)}


def definitions(root, version=None):
    result = {}
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts or (path.name.endswith(".b52.py") and version != "b52"):
            continue
        statements = ast.parse(path.read_text(encoding="utf8")).body
        assignments = {target.id: statement.value for statement in statements if isinstance(statement, ast.Assign)
                       for target in statement.targets if isinstance(target, ast.Name)}
        for statement in statements:
            if not isinstance(statement, ast.ClassDef):
                continue
            name = statement.name
            for item in statement.body:
                if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_name" for t in item.targets):
                    name = ast.literal_eval(item.value) or statement.name
            recipe = assignments.get('MATERIAL')
            kind = 'MATERIAL' if isinstance(recipe, ast.Name) and recipe.id == statement.name else 'NODETREE'
            if kind == 'MATERIAL':
                name = ast.literal_eval(assignments['MATERIAL_NAME'])
            key = (kind, name)
            if key not in result or path.name.endswith(".b52.py"):
                result[key] = (path, statement.name)
    return result


def apply_changes(source, before, after, version):
    """Keep hand-written modules untouched when their native content is unchanged."""
    old, new = source_files(before), source_files(after)
    authored = {name: path for name, (path, _) in definitions(source, version).items()}
    exported = {path.relative_to(before): name for name, (path, _) in definitions(before).items()}
    changed = set()
    for relative in old.keys() | new.keys():
        if old.get(relative) == new.get(relative):
            continue
        path = source / relative
        if relative in exported and exported[relative] in authored:
            path = authored[exported[relative]]
            if sum(candidate == path for candidate in authored.values()) > 1:
                raise ValueError(f"Split definitions into separate modules before syncing: {path}")
        variant = path if path.name.endswith(".b52.py") else path.with_name(path.stem + ".b52.py")
        if path.suffix == ".py" and version == "b52" and variant.exists():
            path = variant
        if relative not in new:
            if path.suffix == ".py" and version == "b52":
                variant.write_text("DISABLED = True\n", encoding="utf8")
            else:
                path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(new[relative])
        changed.add(relative)
    return changed
