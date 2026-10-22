"""Export nodebpy-style Python definitions and their library resources."""
import hashlib
import json
import re
from pathlib import Path
from functools import lru_cache
from ..rna import read
from .codegen import _class_name as class_name, to_python

@lru_cache(maxsize=1)
def material_defaults():
    import bpy
    material = bpy.data.materials.new("_nodes_defaults")
    material.use_nodes = True
    try:
        return read(material, skip={"name", "use_nodes"})
    finally:
        bpy.data.materials.remove(material)


def difference(values, defaults):
    result = {}
    for key, value in values.items():
        if isinstance(value, dict) and isinstance(defaults.get(key), dict):
            value = difference(value, defaults[key])
            if value:
                result[key] = value
        elif key not in defaults or value != defaults[key]:
            result[key] = value
    return result


def slug(name):
    value = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return value if value and not value[0].isdigit() else "node_" + value


def metadata(value):
    if value.asset_data is None:
        return None
    data = {key: getattr(value.asset_data, key) for key in ("description", "author", "copyright", "license", "catalog_id")}
    data["tags"] = sorted(tag.name for tag in value.asset_data.tags)
    return data


def library_data():
    import bpy
    trees = set()
    materials = set()
    images = set()
    owners = {}

    def visit(value):
        if value is None:
            return
        animation = getattr(value, "animation_data", None)
        if animation and (animation.action or animation.drivers):
            raise ValueError(f"Unsupported animated datablock: {value.name}")
        if value.library is not None:
            if value.id_type != "NODETREE":
                raise ValueError(f"Unsupported linked resource: {value.name}")
            owners[value.name] = str(Path(bpy.path.abspath(value.library.filepath)).resolve())
            return
        collection = {"NODETREE": trees, "MATERIAL": materials, "IMAGE": images}.get(value.id_type)
        if collection is None:
            raise ValueError(f"Unsupported datablock dependency: {value.id_type} {value.name}")
        if value in collection:
            return
        collection.add(value)
        tree = value if value.id_type == "NODETREE" else getattr(value, "node_tree", None)
        if tree is None:
            return
        for node in tree.nodes:
            for prop in node.bl_rna.properties:
                if prop.type == "POINTER" and prop.identifier not in {"rna_type", "id_data", "parent"}:
                    child = getattr(node, prop.identifier)
                    if child is not None and hasattr(child, "id_type"):
                        visit(child)
            for item in node.inputs:
                child = getattr(item, "default_value", None)
                if child is not None and hasattr(child, "id_type"):
                    visit(child)

    for value in [*bpy.data.node_groups, *bpy.data.materials]:
        if value.asset_data and value.library is None:
            visit(value)
    return trees, materials, images, owners

def module_path(value):
    category = 'materials' if value.id_type == 'MATERIAL' else {
        'GeometryNodeTree': 'geometry', 'ShaderNodeTree': 'shader', 'CompositorNodeTree': 'compositor'
    }[value.bl_idname]
    folder = Path(category)
    if value.id_type == 'NODETREE' and value.asset_data is None:
        folder /= '_shared'
    return folder / (slug(value.name) + '.py')


def tree_source(tree, material=None, references=None):
    import bpy
    from ..arrangement.source import clear_layout
    from ..native import validate_menus
    validate_menus(tree)
    value = material or tree
    copied = tree.copy()
    try:
        clear_layout(copied)
        from ..native import prepare_export
        prepare_export(copied)
        names = {group.name: class_name(group.name) for group in bpy.data.node_groups}
        for name, (_, imported_class) in (references or {}).items():
            if name in names and bpy.data.node_groups[name].library is not None:
                names[name] = imported_class
        names[copied.name] = class_name(value.name)
        code = to_python(copied, format=False, top_level='class',
                         group_class_names=names, external_groups=set(names)-{copied.name})
        code = code.replace(repr(copied.name), repr(value.name)).replace('"'+copied.name+'"', '"'+value.name+'"')
        dependencies = {node.node_tree for node in copied.nodes
                        if getattr(node, 'node_tree', None) is not None}
        imports = []
        relative = '.' * (len(module_path(value).parent.parts) + 1)
        for dependency in sorted(dependencies, key=lambda group: group.name):
            module = module_path(dependency).with_suffix('').as_posix().replace('/', '.')
            if dependency.library is not None:
                owner = Path(bpy.path.abspath(dependency.library.filepath))
                module, imported_class = (references or {}).get(dependency.name, (
                    f'nodes.{owner.parent.name}.{owner.stem}.{module}', class_name(dependency.name)))
                imports.append(f'from {module} import {imported_class}')
            else:
                imports.append(f'from {relative}{module} import {class_name(dependency.name)}')
        if imports:
            code = '\n'.join(imports) + '\n' + code
        if material:
            properties = difference(read(material, skip={'name', 'use_nodes'}), material_defaults())
            # Material recipes describe native settings, not add-on IDProperty state.
            properties.pop('$custom', None)
            fields = [f'    "{key}": {value!r},' for key, value in properties.items()]
            code += f'\n\nMATERIAL = {class_name(value.name)}\nMATERIAL_NAME = {json.dumps(value.name, ensure_ascii=False)}\n'
            if fields:
                code += '\nMATERIAL_PROPERTIES = {\n' + '\n'.join(fields) + '\n}\n'
        asset = metadata(value)
        if asset is not None:
            fields = [f'    "{key}": {json.dumps(value, ensure_ascii=False)},' for key, value in asset.items() if value]
            code += f'\n\nASSET = {class_name(value.name)}\n\nASSET_METADATA = {{\n' + '\n'.join(fields) + '\n}\n'
        return code
    finally:
        bpy.data.node_groups.remove(copied)


def dump_library(destination, references=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    trees, materials, images, owners = library_data()
    modules = {}
    for value in sorted([*trees, *materials], key=lambda value: (value.id_type, value.name)):
        is_material = value.id_type == 'MATERIAL'
        path = module_path(value)
        if str(path) in modules.values():
            raise ValueError(f'Colliding source filenames: {path}')
        modules[value.name] = str(path)
        output = destination / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(tree_source(value.node_tree if is_material else value, value if is_material else None, references), encoding='utf8')
    resources = []
    for image in sorted(images, key=lambda image: image.name):
        if image.packed_file is None or len(image.packed_files) != 1:
            raise ValueError(f'Expected one packed image: {image.name}')
        data = bytes(image.packed_file.data)
        filename = hashlib.sha256(data).hexdigest()[:16] + (Path(image.filepath).suffix or '.png')
        path = destination / 'resources' / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        resources.append({'name': image.name, 'file': filename, 'colorspace': image.colorspace_settings.name, 'alpha_mode': image.alpha_mode})
    if resources:
        (destination / 'resources/images.json').write_text(json.dumps(resources, indent=2), encoding='utf8')
    return {'owners': owners, 'modules': modules}
