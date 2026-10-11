"""Blender node libraries with the nodebpy authoring API."""

import importlib


def __getattr__(name):
    if name in {"geometry", "shader", "compositor"}:
        return importlib.import_module(f".nodes.{name}", __name__)
    if name in {"TreeBuilder", "MaterialBuilder"}:
        return getattr(importlib.import_module(".builder", __name__), name)
    raise AttributeError(name)
