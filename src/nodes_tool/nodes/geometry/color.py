# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket
from ...socket_types import InputColor, InputFloat

class Gamma(BaseNode):
    _bl_idname = 'ShaderNodeGamma'

    def __init__(self, color: InputColor=None, gamma: InputFloat=1.0):
        super().__init__()
        key_args = {'Color': color, 'Gamma': gamma}
        self._establish_links(**key_args)

class RGBCurves(BaseNode):
    _bl_idname = 'ShaderNodeRGBCurve'

    def __init__(self, fac: InputFloat=1.0, color: InputColor=(1.0, 1.0, 1.0, 1.0)):
        super().__init__()
        key_args = {'Fac': fac, 'Color': color}
        self._establish_links(**key_args)
