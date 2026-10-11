# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket
from ...socket_types import InputColor, InputFloat

class BrightnessContrast(BaseNode):
    _bl_idname = 'ShaderNodeBrightContrast'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), bright: InputFloat=0.0, contrast: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Bright': bright, 'Contrast': contrast}
        self._establish_links(**key_args)

class HueSaturationValue(BaseNode):
    _bl_idname = 'ShaderNodeHueSaturation'

    def __init__(self, hue: InputFloat=0.5, saturation: InputFloat=1.0, value: InputFloat=1.0, fac: InputFloat=1.0, color: InputColor=(0.8, 0.8, 0.8, 1.0)):
        super().__init__()
        key_args = {'Hue': hue, 'Saturation': saturation, 'Value': value, 'Fac': fac, 'Color': color}
        self._establish_links(**key_args)

class InvertColor(BaseNode):
    _bl_idname = 'ShaderNodeInvert'

    def __init__(self, fac: InputFloat=1.0, color: InputColor=(0.0, 0.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'Fac': fac, 'Color': color}
        self._establish_links(**key_args)

class LightFalloff(BaseNode):
    _bl_idname = 'ShaderNodeLightFalloff'

    def __init__(self, strength: InputFloat=100.0, smooth: InputFloat=0.0):
        super().__init__()
        key_args = {'Strength': strength, 'Smooth': smooth}
        self._establish_links(**key_args)
