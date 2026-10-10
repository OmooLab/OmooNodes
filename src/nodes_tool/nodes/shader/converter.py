# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
T = typing.TypeVar('T')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, BundleSocket, ClosureSocket, ColorSocket, FloatSocket, IntegerSocket, MenuSocket, RotationSocket, ShaderSocket, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputBundle, InputClosure, InputColor, InputFloat, InputInteger, InputMenu, InputRotation, InputShader, InputVector

class CombineColor(BaseNode):
    _bl_idname = 'ShaderNodeCombineColor'

    def __init__(self, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, *, mode: Literal['RGB', 'HSV', 'HSL']='RGB'):
        super().__init__()
        key_args = {'Red': red, 'Green': green, 'Blue': blue}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0) -> 'CombineColor':
        return cls(mode='RGB', red=red, green=green, blue=blue)

    @classmethod
    def hsv(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0) -> 'CombineColor':
        return cls(mode='HSV', red=red, green=green, blue=blue)

    @classmethod
    def hsl(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0) -> 'CombineColor':
        return cls(mode='HSL', red=red, green=green, blue=blue)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL']) -> None:
        set_property(self.node, 'mode', value)

class ImplicitConversion(BaseNode):
    _bl_idname = 'NodeImplicitConversion'

    def __init__(self, value: InputAny=(0.0, 0.0, 0.0, 1.0), *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'MENU', 'SHADER', 'BUNDLE', 'CLOSURE']='RGBA'):
        super().__init__()
        key_args = {'Value': value}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, value: InputFloat=0.0) -> 'ImplicitConversion[FloatSocket]':
        return ImplicitConversion(data_type='FLOAT', value=value)

    @classmethod
    def integer(cls, value: InputInteger=0) -> 'ImplicitConversion[IntegerSocket]':
        return ImplicitConversion(data_type='INT', value=value)

    @classmethod
    def boolean(cls, value: InputBoolean=False) -> 'ImplicitConversion[BooleanSocket]':
        return ImplicitConversion(data_type='BOOLEAN', value=value)

    @classmethod
    def vector(cls, value: InputVector=(0.0, 0.0, 0.0)) -> 'ImplicitConversion[VectorSocket]':
        return ImplicitConversion(data_type='VECTOR', value=value)

    @classmethod
    def color(cls, value: InputColor=(0.0, 0.0, 0.0, 1.0)) -> 'ImplicitConversion[ColorSocket]':
        return ImplicitConversion(data_type='RGBA', value=value)

    @classmethod
    def menu(cls, value: InputMenu=None) -> 'ImplicitConversion[MenuSocket]':
        return ImplicitConversion(data_type='MENU', value=value)

    @classmethod
    def shader(cls, value: InputShader=None) -> 'ImplicitConversion[ShaderSocket]':
        return ImplicitConversion(data_type='SHADER', value=value)

    @classmethod
    def bundle(cls, value: InputBundle=None) -> 'ImplicitConversion[BundleSocket]':
        return ImplicitConversion(data_type='BUNDLE', value=value)

    @classmethod
    def closure(cls, value: InputClosure=None) -> 'ImplicitConversion[ClosureSocket]':
        return ImplicitConversion(data_type='CLOSURE', value=value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'MENU', 'SHADER', 'BUNDLE', 'CLOSURE']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'MENU', 'SHADER', 'BUNDLE', 'CLOSURE']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class Mix(BaseNode):
    _bl_idname = 'ShaderNodeMix'

    def __init__(self, factor_float: InputFloat=1.0, factor_vector: InputVector=(0.5, 0.5, 0.5), a_float: InputFloat=0.0, b_float: InputFloat=0.0, a_vector: InputVector=(0.0, 0.0, 0.0), b_vector: InputVector=(0.0, 0.0, 0.0), a_color: InputColor=(0.5, 0.5, 0.5, 1.0), b_color: InputColor=(0.5, 0.5, 0.5, 1.0), a_rotation: InputRotation=(0.0, 0.0, 0.0), b_rotation: InputRotation=(0.0, 0.0, 0.0), *, data_type: Literal['FLOAT', 'VECTOR', 'RGBA']='FLOAT', factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False):
        super().__init__()
        key_args = {'Factor_Float': factor_float, 'Factor_Vector': factor_vector, 'A_Float': a_float, 'B_Float': b_float, 'A_Vector': a_vector, 'B_Vector': b_vector, 'A_Color': a_color, 'B_Color': b_color, 'A_Rotation': a_rotation, 'B_Rotation': b_rotation}
        self.data_type = data_type
        self.factor_mode = factor_mode
        self.blend_type = blend_type
        self.clamp_factor = clamp_factor
        self.clamp_result = clamp_result
        self._establish_links(**key_args)

    @classmethod
    def float(cls, factor: InputFloat=1.0, a: InputFloat=0.0, b: InputFloat=0.0, *, factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False) -> 'Mix':
        return cls(data_type='FLOAT', factor_float=factor, a_float=a, b_float=b, factor_mode=factor_mode, blend_type=blend_type, clamp_factor=clamp_factor, clamp_result=clamp_result)

    @classmethod
    def vector(cls, factor: InputFloat=1.0, a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False) -> 'Mix':
        return cls(data_type='VECTOR', factor_float=factor, a_vector=a, b_vector=b, factor_mode=factor_mode, blend_type=blend_type, clamp_factor=clamp_factor, clamp_result=clamp_result)

    @classmethod
    def color(cls, factor: InputFloat=1.0, a: InputColor=(0.5, 0.5, 0.5, 1.0), b: InputColor=(0.5, 0.5, 0.5, 1.0), *, factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False) -> 'Mix':
        return cls(data_type='RGBA', factor_float=factor, a_color=a, b_color=b, factor_mode=factor_mode, blend_type=blend_type, clamp_factor=clamp_factor, clamp_result=clamp_result)

    @property
    def data_type(self) -> Literal['FLOAT', 'VECTOR', 'RGBA']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'VECTOR', 'RGBA']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def factor_mode(self) -> Literal['UNIFORM', 'NON_UNIFORM']:
        return self.node.factor_mode

    @factor_mode.setter
    def factor_mode(self, value: Literal['UNIFORM', 'NON_UNIFORM']) -> None:
        set_property(self.node, 'factor_mode', value)

    @property
    def blend_type(self) -> Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']:
        return self.node.blend_type

    @blend_type.setter
    def blend_type(self, value: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']) -> None:
        set_property(self.node, 'blend_type', value)

    @property
    def clamp_factor(self) -> bool:
        return self.node.clamp_factor

    @clamp_factor.setter
    def clamp_factor(self, value: bool) -> None:
        set_property(self.node, 'clamp_factor', value)

    @property
    def clamp_result(self) -> bool:
        return self.node.clamp_result

    @clamp_result.setter
    def clamp_result(self, value: bool) -> None:
        set_property(self.node, 'clamp_result', value)

class RGBToBW(BaseNode):
    _bl_idname = 'ShaderNodeRGBToBW'

    def __init__(self, color: InputColor=(0.5, 0.5, 0.5, 1.0)):
        super().__init__()
        key_args = {'Color': color}
        self._establish_links(**key_args)

class SeparateColor(BaseNode):
    _bl_idname = 'ShaderNodeSeparateColor'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), *, mode: Literal['RGB', 'HSV', 'HSL']='RGB'):
        super().__init__()
        key_args = {'Color': color}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, color: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'SeparateColor':
        return cls(mode='RGB', color=color)

    @classmethod
    def hsv(cls, color: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'SeparateColor':
        return cls(mode='HSV', color=color)

    @classmethod
    def hsl(cls, color: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'SeparateColor':
        return cls(mode='HSL', color=color)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL']) -> None:
        set_property(self.node, 'mode', value)

class ShaderToRGB(BaseNode):
    _bl_idname = 'ShaderNodeShaderToRGB'

    def __init__(self, shader: InputShader=None):
        super().__init__()
        key_args = {'Shader': shader}
        self._establish_links(**key_args)

class Wavelength(BaseNode):
    _bl_idname = 'ShaderNodeWavelength'

    def __init__(self, wavelength: InputFloat=500.0):
        super().__init__()
        key_args = {'Wavelength': wavelength}
        self._establish_links(**key_args)
