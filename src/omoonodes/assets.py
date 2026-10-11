"""Load Python definitions and build a native asset library."""

import importlib
import types
import uuid
import json
import os
import sys
from pathlib import Path

from .builder import NodeGroupBuilder, TreeBuilder
from .rna import restore


class Library:
    def __init__(self, source, source_root=None):
        self.source = Path(source)
        self.definitions = {}
        self.metadata = {}
        self.pending = set()
        root = Path(source_root) if source_root else self.source
        package = 'nodes' if source_root else '_nodes_source_' + uuid.uuid4().hex
        # Bind imports to this target's selected sources, never another project.
        for name in list(sys.modules):
            if name == package or name.startswith(package + '.'):
                del sys.modules[name]
        module = types.ModuleType(package)
        module.__path__ = [str(root)]
        sys.modules[package] = module
        self.materials = {}
        for path in sorted(self.source.rglob('*.py')):
            if path.name == '__init__.py' or '.b' in path.name:
                continue
            name = '.'.join(path.relative_to(root).with_suffix('').parts)
            module = importlib.import_module(package + '.' + name)
            if getattr(module, 'DISABLED', False):
                continue
            material = getattr(module, 'MATERIAL', None)
            for definition in vars(module).values():
                if not isinstance(definition, type) or definition.__module__ != module.__name__:
                    continue
                if not issubclass(definition, NodeGroupBuilder):
                    continue
                name = module.MATERIAL_NAME if definition is material else definition._name
                key = ('MATERIAL' if definition is material else 'NODETREE', name)
                if self.definitions.get(key) is definition:
                    continue
                if key in self.definitions:
                    raise ValueError(f'Duplicate definition: {name}')
                self.definitions[key] = definition
                if definition is material:
                    self.materials[key] = getattr(module, 'MATERIAL_PROPERTIES', {})
                if getattr(module, 'ASSET', None) is definition:
                    self.metadata[key] = getattr(module, 'ASSET_METADATA', {})

    def reference(self, type, name):
        import bpy
        key = (type, name)
        if key in self.pending:
            raise ValueError(f"Recursive node dependency: {name}")
        collections = {"NODETREE": bpy.data.node_groups, "MATERIAL": bpy.data.materials, "IMAGE": bpy.data.images}
        if type not in collections:
            raise ValueError(f"Unsupported datablock: {type} {name}")
        existing = collections[type].get(name)
        if existing is not None:
            return existing
        if key not in self.definitions:
            raise ValueError(f"Missing {type} dependency: {name}")
        self.pending.add(key)
        try:
            definition = self.definitions[key]
            if type == 'MATERIAL':
                value = bpy.data.materials.new(name)
                value.use_nodes = True
                value.node_tree.nodes.clear()
                restore(value, self.materials[key], self.reference)
                with TreeBuilder(value.node_tree) as tree:
                    definition.__new__(definition)._build_group(tree)
            else:
                value = definition.create_group()
        except (ValueError, TypeError, RuntimeError, KeyError) as error:
            raise ValueError(f"{name}: {error}") from error
        self.pending.remove(key)
        return value

    def build(self):
        import bpy
        path = self.source / "resources/images.json"
        if path.exists():
            for data in json.loads(path.read_text(encoding="utf8")):
                image = bpy.data.images.load(str(path.parent / data["file"]), check_existing=False)
                image.name = data["name"]
                image.colorspace_settings.name = data["colorspace"]
                image.alpha_mode = data["alpha_mode"]
                image.pack()
        for key in self.materials:
            self.reference(*key)
        # Dependencies can build an asset before its own turn; mark every root.
        roots = set()
        for key, data in self.metadata.items():
            value = self.reference(*key)
            value.asset_mark()
            roots.add(value)
            for prop, item in data.items():
                if prop == 'tags':
                    for tag in item:
                        if tag not in value.asset_data.tags:
                            value.asset_data.tags.new(tag)
                else:
                    setattr(value.asset_data, prop, item)
        return roots


def build_library(source, destination, links=None, source_root=None):
    import bpy
    from .blend import dependencies
    for name, owner in (links or {}).items():
        list(dependencies(owner))
        with bpy.data.libraries.load(str(owner), link=True) as (_, target):
            target.node_groups = [name]
        if target.node_groups[0] is None:
            raise ValueError(f"Missing dependency {owner}: {name}")
    roots = Library(source, source_root).build()
    from .arrangement.arrange import arrange_nodes
    for tree in [*bpy.data.node_groups, *(material.node_tree for material in bpy.data.materials if material.use_nodes)]:
        if tree.library is None:
            arrange_nodes(tree)
    for library in bpy.data.libraries:
        absolute = Path(bpy.path.abspath(library.filepath)).resolve()
        library.filepath = "//" + os.path.relpath(absolute, Path(destination).parent).replace("\\", "/")
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    bpy.data.libraries.write(str(destination), roots, fake_user=True, compress=True)
    return roots
