# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket, ShaderSocket, VectorSocket
from ...socket_types import InputColor, InputFloat, InputShader, InputVector

class AOVOutput(BaseNode):
    _bl_idname = 'ShaderNodeOutputAOV'

    def __init__(self, color: InputColor=(0.0, 0.0, 0.0, 1.0), value: InputFloat=0.0, *, aov_name: str=''):
        super().__init__()
        key_args = {'Color': color, 'Value': value}
        self.aov_name = aov_name
        self._establish_links(**key_args)

    @property
    def aov_name(self) -> str:
        return self.node.aov_name

    @aov_name.setter
    def aov_name(self, value: str) -> None:
        set_property(self.node, 'aov_name', value)

class LightOutput(BaseNode):
    _bl_idname = 'ShaderNodeOutputLight'

    def __init__(self, surface: InputShader=None, *, is_active_output: bool=False, target: Literal['ALL', 'EEVEE', 'CYCLES']='ALL'):
        super().__init__()
        key_args = {'Surface': surface}
        self.is_active_output = is_active_output
        self.target = target
        self._establish_links(**key_args)

    @property
    def is_active_output(self) -> bool:
        return self.node.is_active_output

    @is_active_output.setter
    def is_active_output(self, value: bool) -> None:
        set_property(self.node, 'is_active_output', value)

    @property
    def target(self) -> Literal['ALL', 'EEVEE', 'CYCLES']:
        return self.node.target

    @target.setter
    def target(self, value: Literal['ALL', 'EEVEE', 'CYCLES']) -> None:
        set_property(self.node, 'target', value)

class LineStyleOutput(BaseNode):
    _bl_idname = 'ShaderNodeOutputLineStyle'

    def __init__(self, color: InputColor=(1.0, 0.0, 1.0, 1.0), color_fac: InputFloat=1.0, alpha: InputFloat=1.0, alpha_fac: InputFloat=1.0, *, is_active_output: bool=False, target: Literal['ALL', 'EEVEE', 'CYCLES']='ALL', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', use_alpha: bool=False, use_clamp: bool=False):
        super().__init__()
        key_args = {'Color': color, 'Color Fac': color_fac, 'Alpha': alpha, 'Alpha Fac': alpha_fac}
        self.is_active_output = is_active_output
        self.target = target
        self.blend_type = blend_type
        self.use_alpha = use_alpha
        self.use_clamp = use_clamp
        self._establish_links(**key_args)

    @property
    def is_active_output(self) -> bool:
        return self.node.is_active_output

    @is_active_output.setter
    def is_active_output(self, value: bool) -> None:
        set_property(self.node, 'is_active_output', value)

    @property
    def target(self) -> Literal['ALL', 'EEVEE', 'CYCLES']:
        return self.node.target

    @target.setter
    def target(self, value: Literal['ALL', 'EEVEE', 'CYCLES']) -> None:
        set_property(self.node, 'target', value)

    @property
    def blend_type(self) -> Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']:
        return self.node.blend_type

    @blend_type.setter
    def blend_type(self, value: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']) -> None:
        set_property(self.node, 'blend_type', value)

    @property
    def use_alpha(self) -> bool:
        return self.node.use_alpha

    @use_alpha.setter
    def use_alpha(self, value: bool) -> None:
        set_property(self.node, 'use_alpha', value)

    @property
    def use_clamp(self) -> bool:
        return self.node.use_clamp

    @use_clamp.setter
    def use_clamp(self, value: bool) -> None:
        set_property(self.node, 'use_clamp', value)

class MaterialOutput(BaseNode):
    _bl_idname = 'ShaderNodeOutputMaterial'

    def __init__(self, surface: InputShader=None, volume: InputShader=None, displacement: InputVector=None, thickness: InputFloat=None, *, is_active_output: bool=False, target: Literal['ALL', 'EEVEE', 'CYCLES']='ALL'):
        super().__init__()
        key_args = {'Surface': surface, 'Volume': volume, 'Displacement': displacement, 'Thickness': thickness}
        self.is_active_output = is_active_output
        self.target = target
        self._establish_links(**key_args)

    @property
    def is_active_output(self) -> bool:
        return self.node.is_active_output

    @is_active_output.setter
    def is_active_output(self, value: bool) -> None:
        set_property(self.node, 'is_active_output', value)

    @property
    def target(self) -> Literal['ALL', 'EEVEE', 'CYCLES']:
        return self.node.target

    @target.setter
    def target(self, value: Literal['ALL', 'EEVEE', 'CYCLES']) -> None:
        set_property(self.node, 'target', value)

class WorldOutput(BaseNode):
    _bl_idname = 'ShaderNodeOutputWorld'

    def __init__(self, surface: InputShader=None, volume: InputShader=None, *, is_active_output: bool=False, target: Literal['ALL', 'EEVEE', 'CYCLES']='ALL'):
        super().__init__()
        key_args = {'Surface': surface, 'Volume': volume}
        self.is_active_output = is_active_output
        self.target = target
        self._establish_links(**key_args)

    @property
    def is_active_output(self) -> bool:
        return self.node.is_active_output

    @is_active_output.setter
    def is_active_output(self, value: bool) -> None:
        set_property(self.node, 'is_active_output', value)

    @property
    def target(self) -> Literal['ALL', 'EEVEE', 'CYCLES']:
        return self.node.target

    @target.setter
    def target(self, value: Literal['ALL', 'EEVEE', 'CYCLES']) -> None:
        set_property(self.node, 'target', value)
