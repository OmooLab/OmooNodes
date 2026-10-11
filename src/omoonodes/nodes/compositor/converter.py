# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
import math
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, Socket, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, FontSocket, IntegerSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, StringSocket, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputColor, InputFloat, InputFont, InputInteger, InputIntegerVector, InputLinkable, InputMatrix, InputMenu, InputObject, InputRotation, InputString, InputVector

class AlphaConvert(BaseNode):
    _bl_idname = 'CompositorNodePremulKey'

    def __init__(self, image: InputColor=None, type: InputMenu | Literal['To Premultiplied', 'To Straight']='To Premultiplied'):
        super().__init__()
        key_args = {'Image': image, 'Type': type}
        self._establish_links(**key_args)

    @classmethod
    def to_premultiplied(cls, image: InputColor=None) -> 'AlphaConvert':
        return cls(image=image, type='To Premultiplied')

    @classmethod
    def to_straight(cls, image: InputColor=None) -> 'AlphaConvert':
        return cls(image=image, type='To Straight')

class CombineColor(BaseNode):
    _bl_idname = 'CompositorNodeCombineColor'

    def __init__(self, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, mode: Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']='RGB', ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709'):
        super().__init__()
        key_args = {'Red': red, 'Green': green, 'Blue': blue, 'Alpha': alpha}
        self.mode = mode
        self.ycc_mode = ycc_mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'CombineColor':
        return cls(mode='RGB', red=red, green=green, blue=blue, alpha=alpha, ycc_mode=ycc_mode)

    @classmethod
    def hsv(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'CombineColor':
        return cls(mode='HSV', red=red, green=green, blue=blue, alpha=alpha, ycc_mode=ycc_mode)

    @classmethod
    def hsl(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'CombineColor':
        return cls(mode='HSL', red=red, green=green, blue=blue, alpha=alpha, ycc_mode=ycc_mode)

    @classmethod
    def ycbcr(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'CombineColor':
        return cls(mode='YCC', red=red, green=green, blue=blue, alpha=alpha, ycc_mode=ycc_mode)

    @classmethod
    def yuv(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'CombineColor':
        return cls(mode='YUV', red=red, green=green, blue=blue, alpha=alpha, ycc_mode=ycc_mode)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def ycc_mode(self) -> Literal['ITUBT601', 'ITUBT709', 'JFIF']:
        return self.node.ycc_mode

    @ycc_mode.setter
    def ycc_mode(self, value: Literal['ITUBT601', 'ITUBT709', 'JFIF']) -> None:
        set_property(self.node, 'ycc_mode', value)

class ConvertToDisplay(BaseNode):
    _bl_idname = 'CompositorNodeConvertToDisplay'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), invert: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'Invert': invert}
        self._establish_links(**key_args)

class IDMask(BaseNode):
    _bl_idname = 'CompositorNodeIDMask'

    def __init__(self, id_value: InputFloat=1.0, index: InputInteger=0, anti_alias: InputBoolean=False):
        super().__init__()
        key_args = {'ID value': id_value, 'Index': index, 'Anti-Alias': anti_alias}
        self._establish_links(**key_args)

class ImplicitConversion(BaseNode):
    _bl_idname = 'NodeImplicitConversion'

    def __init__(self, value: InputAny=(0.0, 0.0, 0.0, 1.0), *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']='RGBA'):
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
    def rotation(cls, value: InputRotation=(0.0, 0.0, 0.0)) -> 'ImplicitConversion[RotationSocket]':
        return ImplicitConversion(data_type='ROTATION', value=value)

    @classmethod
    def matrix(cls, value: InputMatrix=None) -> 'ImplicitConversion[MatrixSocket]':
        return ImplicitConversion(data_type='MATRIX', value=value)

    @classmethod
    def string(cls, value: InputString='') -> 'ImplicitConversion[StringSocket]':
        return ImplicitConversion(data_type='STRING', value=value)

    @classmethod
    def menu(cls, value: InputMenu=None) -> 'ImplicitConversion[MenuSocket]':
        return ImplicitConversion(data_type='MENU', value=value)

    @classmethod
    def object(cls, value: InputObject=None) -> 'ImplicitConversion[ObjectSocket]':
        return ImplicitConversion(data_type='OBJECT', value=value)

    @classmethod
    def font(cls, value: InputFont=None) -> 'ImplicitConversion[FontSocket]':
        return ImplicitConversion(data_type='FONT', value=value)

    @classmethod
    def integer_vector(cls, value: InputIntegerVector=(0, 0, 0)) -> 'ImplicitConversion[IntegerSocket]':
        return ImplicitConversion(data_type='INT_VECTOR', value=value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class IndexSwitch(BaseNode):
    _bl_idname = 'GeometryNodeIndexSwitch'

    def __init__(self, index: InputInteger=0, item_0: InputAny=(0.8, 0.8, 0.8, 1.0), item_1: InputAny=(0.8, 0.8, 0.8, 1.0), extend: InputLinkable=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']='RGBA'):
        super().__init__()
        key_args = {'Index': index, 'Item_0': item_0, 'Item_1': item_1, '__extend__': extend}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, index: InputInteger=0, item_0: InputFloat=0.0, item_1: InputFloat=0.0, extend: InputLinkable=None) -> 'IndexSwitch[FloatSocket]':
        return IndexSwitch(data_type='FLOAT', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def integer(cls, index: InputInteger=0, item_0: InputInteger=0, item_1: InputInteger=0, extend: InputLinkable=None) -> 'IndexSwitch[IntegerSocket]':
        return IndexSwitch(data_type='INT', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def boolean(cls, index: InputInteger=0, item_0: InputBoolean=False, item_1: InputBoolean=False, extend: InputLinkable=None) -> 'IndexSwitch[BooleanSocket]':
        return IndexSwitch(data_type='BOOLEAN', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def vector(cls, index: InputInteger=0, item_0: InputVector=(0.0, 0.0, 0.0), item_1: InputVector=(0.0, 0.0, 0.0), extend: InputLinkable=None) -> 'IndexSwitch[VectorSocket]':
        return IndexSwitch(data_type='VECTOR', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def color(cls, index: InputInteger=0, item_0: InputColor=(0.8, 0.8, 0.8, 1.0), item_1: InputColor=(0.8, 0.8, 0.8, 1.0), extend: InputLinkable=None) -> 'IndexSwitch[ColorSocket]':
        return IndexSwitch(data_type='RGBA', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def rotation(cls, index: InputInteger=0, item_0: InputRotation=(0.0, 0.0, 0.0), item_1: InputRotation=(0.0, 0.0, 0.0), extend: InputLinkable=None) -> 'IndexSwitch[RotationSocket]':
        return IndexSwitch(data_type='ROTATION', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def matrix(cls, index: InputInteger=0, item_0: InputMatrix=None, item_1: InputMatrix=None, extend: InputLinkable=None) -> 'IndexSwitch[MatrixSocket]':
        return IndexSwitch(data_type='MATRIX', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def string(cls, index: InputInteger=0, item_0: InputString='', item_1: InputString='', extend: InputLinkable=None) -> 'IndexSwitch[StringSocket]':
        return IndexSwitch(data_type='STRING', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def menu(cls, index: InputInteger=0, item_0: InputMenu=None, item_1: InputMenu=None, extend: InputLinkable=None) -> 'IndexSwitch[MenuSocket]':
        return IndexSwitch(data_type='MENU', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def object(cls, index: InputInteger=0, item_0: InputObject=None, item_1: InputObject=None, extend: InputLinkable=None) -> 'IndexSwitch[ObjectSocket]':
        return IndexSwitch(data_type='OBJECT', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def font(cls, index: InputInteger=0, item_0: InputFont=None, item_1: InputFont=None, extend: InputLinkable=None) -> 'IndexSwitch[FontSocket]':
        return IndexSwitch(data_type='FONT', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @classmethod
    def integer_vector(cls, index: InputInteger=0, item_0: InputIntegerVector=(0, 0, 0), item_1: InputIntegerVector=(0, 0, 0), extend: InputLinkable=None) -> 'IndexSwitch[IntegerSocket]':
        return IndexSwitch(data_type='INT_VECTOR', index=index, item_0=item_0, item_1=item_1, extend=extend)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class Levels(BaseNode):
    _bl_idname = 'CompositorNodeLevels'

    def __init__(self, image: InputColor=(0.0, 0.0, 0.0, 1.0), channel: InputMenu | Literal['Combined', 'Red', 'Green', 'Blue', 'Luminance']='Combined'):
        super().__init__()
        key_args = {'Image': image, 'Channel': channel}
        self._establish_links(**key_args)

class RGBToBW(BaseNode):
    _bl_idname = 'CompositorNodeRGBToBW'

    def __init__(self, image: InputColor=(0.8, 0.8, 0.8, 1.0)):
        super().__init__()
        key_args = {'Image': image}
        self._establish_links(**key_args)

class RelativeToPixel(BaseNode):
    _bl_idname = 'CompositorNodeRelativeToPixel'

    def __init__(self, vector_value: InputVector=(0.0, 0.0), float_value: InputFloat=0.0, image: InputColor=(0.8, 0.8, 0.8, 1.0), *, data_type: Literal['FLOAT', 'VECTOR']='FLOAT', reference_dimension: Literal['PER_DIMENSION', 'X', 'Y', 'Greater', 'Smaller', 'Diagonal']='X'):
        super().__init__()
        key_args = {'Vector Value': vector_value, 'Float Value': float_value, 'Image': image}
        self.data_type = data_type
        self.reference_dimension = reference_dimension
        self._establish_links(**key_args)

    @classmethod
    def float(cls, float_value: InputFloat=0.0, image: InputColor=(0.8, 0.8, 0.8, 1.0), *, reference_dimension: Literal['PER_DIMENSION', 'X', 'Y', 'Greater', 'Smaller', 'Diagonal']='X') -> 'RelativeToPixel':
        return cls(data_type='FLOAT', float_value=float_value, image=image, reference_dimension=reference_dimension)

    @classmethod
    def vector(cls, vector_value: InputVector=(0.0, 0.0), image: InputColor=(0.8, 0.8, 0.8, 1.0), *, reference_dimension: Literal['PER_DIMENSION', 'X', 'Y', 'Greater', 'Smaller', 'Diagonal']='X') -> 'RelativeToPixel':
        return cls(data_type='VECTOR', vector_value=vector_value, image=image, reference_dimension=reference_dimension)

    @property
    def data_type(self) -> Literal['FLOAT', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def reference_dimension(self) -> Literal['PER_DIMENSION', 'X', 'Y', 'Greater', 'Smaller', 'Diagonal']:
        return self.node.reference_dimension

    @reference_dimension.setter
    def reference_dimension(self, value: Literal['PER_DIMENSION', 'X', 'Y', 'Greater', 'Smaller', 'Diagonal']) -> None:
        set_property(self.node, 'reference_dimension', value)

class SeparateColor(BaseNode):
    _bl_idname = 'CompositorNodeSeparateColor'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, mode: Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']='RGB', ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709'):
        super().__init__()
        key_args = {'Image': image}
        self.mode = mode
        self.ycc_mode = ycc_mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'SeparateColor':
        return cls(mode='RGB', image=image, ycc_mode=ycc_mode)

    @classmethod
    def hsv(cls, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'SeparateColor':
        return cls(mode='HSV', image=image, ycc_mode=ycc_mode)

    @classmethod
    def hsl(cls, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'SeparateColor':
        return cls(mode='HSL', image=image, ycc_mode=ycc_mode)

    @classmethod
    def ycbcr(cls, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'SeparateColor':
        return cls(mode='YCC', image=image, ycc_mode=ycc_mode)

    @classmethod
    def yuv(cls, image: InputColor=(1.0, 1.0, 1.0, 1.0), *, ycc_mode: Literal['ITUBT601', 'ITUBT709', 'JFIF']='ITUBT709') -> 'SeparateColor':
        return cls(mode='YUV', image=image, ycc_mode=ycc_mode)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL', 'YCC', 'YUV']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def ycc_mode(self) -> Literal['ITUBT601', 'ITUBT709', 'JFIF']:
        return self.node.ycc_mode

    @ycc_mode.setter
    def ycc_mode(self, value: Literal['ITUBT601', 'ITUBT709', 'JFIF']) -> None:
        set_property(self.node, 'ycc_mode', value)

class SetAlpha(BaseNode):
    _bl_idname = 'CompositorNodeSetAlpha'

    def __init__(self, image: InputColor=None, alpha: InputFloat=1.0, type: InputMenu | Literal['Apply Mask', 'Replace Alpha']='Apply Mask'):
        super().__init__()
        key_args = {'Image': image, 'Alpha': alpha, 'Type': type}
        self._establish_links(**key_args)

    @classmethod
    def apply_mask(cls, image: InputColor=None, alpha: InputFloat=1.0) -> 'SetAlpha':
        return cls(image=image, alpha=alpha, type='Apply Mask')

    @classmethod
    def replace_alpha(cls, image: InputColor=None, alpha: InputFloat=1.0) -> 'SetAlpha':
        return cls(image=image, alpha=alpha, type='Replace Alpha')

class Split(BaseNode):
    _bl_idname = 'CompositorNodeSplit'

    def __init__(self, position: InputVector=(0.5, 0.5), rotation: InputFloat=math.pi / 4, image: InputColor=(0.8, 0.8, 0.8, 1.0), image_001: InputColor=(0.8, 0.8, 0.8, 1.0)):
        super().__init__()
        key_args = {'Position': position, 'Rotation': rotation, 'Image': image, 'Image_001': image_001}
        self._establish_links(**key_args)

class Switch(BaseNode):
    _bl_idname = 'CompositorNodeSwitch'

    def __init__(self, switch: InputBoolean=False, off: InputColor=(0.8, 0.8, 0.8, 1.0), on: InputColor=(0.8, 0.8, 0.8, 1.0)):
        super().__init__()
        key_args = {'Switch': switch, 'Off': off, 'On': on}
        self._establish_links(**key_args)

class SwitchView(BaseNode):
    _bl_idname = 'CompositorNodeSwitchView'

    def __init__(self, left: InputColor=(0.0, 0.0, 0.0, 1.0), right: InputColor=(0.0, 0.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'left': left, 'right': right}
        self._establish_links(**key_args)
