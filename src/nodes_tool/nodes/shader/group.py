# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor

class Group(BaseNode):
    _bl_idname = 'ShaderNodeGroup'

    def __init__(self, node_tree=None, **inputs) -> None:
        super().__init__()
        if isinstance(node_tree, str):
            node_tree = bpy.data.node_groups[node_tree]
        self.node.node_tree = node_tree
        named_links = inputs.pop('_named_links', None)
        self._establish_links(**inputs)
        if named_links:
            self._establish_named_links(named_links)
