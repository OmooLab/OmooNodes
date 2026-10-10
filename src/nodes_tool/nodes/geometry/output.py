# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor

class Viewer(BaseNode):
    _bl_idname = 'GeometryNodeViewer'

    def __init__(self, ui_shortcut: int=0, domain: Literal['AUTO', 'POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='AUTO'):
        super().__init__()
        key_args = {}
        self.ui_shortcut = ui_shortcut
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def auto(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='AUTO', ui_shortcut=ui_shortcut)

    @classmethod
    def point(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='POINT', ui_shortcut=ui_shortcut)

    @classmethod
    def edge(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='EDGE', ui_shortcut=ui_shortcut)

    @classmethod
    def face(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='FACE', ui_shortcut=ui_shortcut)

    @classmethod
    def face_corner(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='CORNER', ui_shortcut=ui_shortcut)

    @classmethod
    def spline(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='CURVE', ui_shortcut=ui_shortcut)

    @classmethod
    def instance(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='INSTANCE', ui_shortcut=ui_shortcut)

    @classmethod
    def layer(cls, *, ui_shortcut: int=0) -> 'Viewer':
        return cls(domain='LAYER', ui_shortcut=ui_shortcut)

    @property
    def ui_shortcut(self) -> int:
        return self.node.ui_shortcut

    @ui_shortcut.setter
    def ui_shortcut(self, value: int) -> None:
        set_property(self.node, 'ui_shortcut', value)

    @property
    def domain(self) -> Literal['AUTO', 'POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['AUTO', 'POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)
