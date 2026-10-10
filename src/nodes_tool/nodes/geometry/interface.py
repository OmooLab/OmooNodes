# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
T = typing.TypeVar('T')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, BundleSocket, ClosureSocket, CollectionSocket, ColorSocket, FloatSocket, FontSocket, GeometrySocket, ImageSocket, IntegerSocket, MaterialSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, SoundSocket, StringSocket, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputBundle, InputClosure, InputCollection, InputColor, InputFloat, InputFont, InputGeometry, InputImage, InputInteger, InputMaterial, InputMatrix, InputMenu, InputObject, InputRotation, InputSound, InputString, InputVector

class DialGizmo(BaseNode):
    _bl_idname = 'GeometryNodeGizmoDial'

    def __init__(self, value: InputFloat=None, position: InputVector=(0.0, 0.0, 0.0), up: InputVector=(0.0, 0.0, 1.0), screen_space: InputBoolean=True, radius: InputFloat=1.0, *, color_id: Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']='PRIMARY'):
        super().__init__()
        key_args = {'Value': value, 'Position': position, 'Up': up, 'Screen Space': screen_space, 'Radius': radius}
        self.color_id = color_id
        self._establish_links(**key_args)

    @property
    def color_id(self) -> Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']:
        return self.node.color_id

    @color_id.setter
    def color_id(self, value: Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']) -> None:
        set_property(self.node, 'color_id', value)

class EnableOutput(BaseNode):
    _bl_idname = 'NodeEnableOutput'

    def __init__(self, enable: InputBoolean=False, value: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT'):
        super().__init__()
        key_args = {'Enable': enable, 'Value': value}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, enable: InputBoolean=False, value: InputFloat=None) -> 'EnableOutput[FloatSocket]':
        return EnableOutput(data_type='FLOAT', enable=enable, value=value)

    @classmethod
    def integer(cls, enable: InputBoolean=False, value: InputInteger=None) -> 'EnableOutput[IntegerSocket]':
        return EnableOutput(data_type='INT', enable=enable, value=value)

    @classmethod
    def boolean(cls, enable: InputBoolean=False, value: InputBoolean=None) -> 'EnableOutput[BooleanSocket]':
        return EnableOutput(data_type='BOOLEAN', enable=enable, value=value)

    @classmethod
    def vector(cls, enable: InputBoolean=False, value: InputVector=None) -> 'EnableOutput[VectorSocket]':
        return EnableOutput(data_type='VECTOR', enable=enable, value=value)

    @classmethod
    def color(cls, enable: InputBoolean=False, value: InputColor=None) -> 'EnableOutput[ColorSocket]':
        return EnableOutput(data_type='RGBA', enable=enable, value=value)

    @classmethod
    def rotation(cls, enable: InputBoolean=False, value: InputRotation=None) -> 'EnableOutput[RotationSocket]':
        return EnableOutput(data_type='ROTATION', enable=enable, value=value)

    @classmethod
    def matrix(cls, enable: InputBoolean=False, value: InputMatrix=None) -> 'EnableOutput[MatrixSocket]':
        return EnableOutput(data_type='MATRIX', enable=enable, value=value)

    @classmethod
    def string(cls, enable: InputBoolean=False, value: InputString=None) -> 'EnableOutput[StringSocket]':
        return EnableOutput(data_type='STRING', enable=enable, value=value)

    @classmethod
    def menu(cls, enable: InputBoolean=False, value: InputMenu=None) -> 'EnableOutput[MenuSocket]':
        return EnableOutput(data_type='MENU', enable=enable, value=value)

    @classmethod
    def object(cls, enable: InputBoolean=False, value: InputObject=None) -> 'EnableOutput[ObjectSocket]':
        return EnableOutput(data_type='OBJECT', enable=enable, value=value)

    @classmethod
    def image(cls, enable: InputBoolean=False, value: InputImage=None) -> 'EnableOutput[ImageSocket]':
        return EnableOutput(data_type='IMAGE', enable=enable, value=value)

    @classmethod
    def geometry(cls, enable: InputBoolean=False, value: InputGeometry=None) -> 'EnableOutput[GeometrySocket]':
        return EnableOutput(data_type='GEOMETRY', enable=enable, value=value)

    @classmethod
    def collection(cls, enable: InputBoolean=False, value: InputCollection=None) -> 'EnableOutput[CollectionSocket]':
        return EnableOutput(data_type='COLLECTION', enable=enable, value=value)

    @classmethod
    def material(cls, enable: InputBoolean=False, value: InputMaterial=None) -> 'EnableOutput[MaterialSocket]':
        return EnableOutput(data_type='MATERIAL', enable=enable, value=value)

    @classmethod
    def bundle(cls, enable: InputBoolean=False, value: InputBundle=None) -> 'EnableOutput[BundleSocket]':
        return EnableOutput(data_type='BUNDLE', enable=enable, value=value)

    @classmethod
    def closure(cls, enable: InputBoolean=False, value: InputClosure=None) -> 'EnableOutput[ClosureSocket]':
        return EnableOutput(data_type='CLOSURE', enable=enable, value=value)

    @classmethod
    def font(cls, enable: InputBoolean=False, value: InputFont=None) -> 'EnableOutput[FontSocket]':
        return EnableOutput(data_type='FONT', enable=enable, value=value)

    @classmethod
    def sound(cls, enable: InputBoolean=False, value: InputSound=None) -> 'EnableOutput[SoundSocket]':
        return EnableOutput(data_type='SOUND', enable=enable, value=value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GroupInput(BaseNode):
    _bl_idname = 'NodeGroupInput'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class GroupOutput(BaseNode):
    _bl_idname = 'NodeGroupOutput'

    def __init__(self, is_active_output: bool=False):
        super().__init__()
        key_args = {}
        self.is_active_output = is_active_output
        self._establish_links(**key_args)

    @property
    def is_active_output(self) -> bool:
        return self.node.is_active_output

    @is_active_output.setter
    def is_active_output(self, value: bool) -> None:
        set_property(self.node, 'is_active_output', value)

class LinearGizmo(BaseNode):
    _bl_idname = 'GeometryNodeGizmoLinear'

    def __init__(self, value: InputFloat=None, position: InputVector=(0.0, 0.0, 0.0), direction: InputVector=(0.0, 0.0, 1.0), *, color_id: Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']='PRIMARY', draw_style: Literal['ARROW', 'CROSS', 'BOX']='ARROW'):
        super().__init__()
        key_args = {'Value': value, 'Position': position, 'Direction': direction}
        self.color_id = color_id
        self.draw_style = draw_style
        self._establish_links(**key_args)

    @property
    def color_id(self) -> Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']:
        return self.node.color_id

    @color_id.setter
    def color_id(self, value: Literal['PRIMARY', 'SECONDARY', 'X', 'Y', 'Z']) -> None:
        set_property(self.node, 'color_id', value)

    @property
    def draw_style(self) -> Literal['ARROW', 'CROSS', 'BOX']:
        return self.node.draw_style

    @draw_style.setter
    def draw_style(self, value: Literal['ARROW', 'CROSS', 'BOX']) -> None:
        set_property(self.node, 'draw_style', value)

class TransformGizmo(BaseNode):
    _bl_idname = 'GeometryNodeGizmoTransform'

    def __init__(self, value: InputMatrix=None, position: InputVector=(0.0, 0.0, 0.0), rotation: InputRotation=(0.0, 0.0, 0.0), *, use_translation_x: bool=False, use_translation_y: bool=False, use_translation_z: bool=False, use_rotation_x: bool=False, use_rotation_y: bool=False, use_rotation_z: bool=False, use_scale_x: bool=False, use_scale_y: bool=False, use_scale_z: bool=False):
        super().__init__()
        key_args = {'Value': value, 'Position': position, 'Rotation': rotation}
        self.use_translation_x = use_translation_x
        self.use_translation_y = use_translation_y
        self.use_translation_z = use_translation_z
        self.use_rotation_x = use_rotation_x
        self.use_rotation_y = use_rotation_y
        self.use_rotation_z = use_rotation_z
        self.use_scale_x = use_scale_x
        self.use_scale_y = use_scale_y
        self.use_scale_z = use_scale_z
        self._establish_links(**key_args)

    @property
    def use_translation_x(self) -> bool:
        return self.node.use_translation_x

    @use_translation_x.setter
    def use_translation_x(self, value: bool) -> None:
        set_property(self.node, 'use_translation_x', value)

    @property
    def use_translation_y(self) -> bool:
        return self.node.use_translation_y

    @use_translation_y.setter
    def use_translation_y(self, value: bool) -> None:
        set_property(self.node, 'use_translation_y', value)

    @property
    def use_translation_z(self) -> bool:
        return self.node.use_translation_z

    @use_translation_z.setter
    def use_translation_z(self, value: bool) -> None:
        set_property(self.node, 'use_translation_z', value)

    @property
    def use_rotation_x(self) -> bool:
        return self.node.use_rotation_x

    @use_rotation_x.setter
    def use_rotation_x(self, value: bool) -> None:
        set_property(self.node, 'use_rotation_x', value)

    @property
    def use_rotation_y(self) -> bool:
        return self.node.use_rotation_y

    @use_rotation_y.setter
    def use_rotation_y(self, value: bool) -> None:
        set_property(self.node, 'use_rotation_y', value)

    @property
    def use_rotation_z(self) -> bool:
        return self.node.use_rotation_z

    @use_rotation_z.setter
    def use_rotation_z(self, value: bool) -> None:
        set_property(self.node, 'use_rotation_z', value)

    @property
    def use_scale_x(self) -> bool:
        return self.node.use_scale_x

    @use_scale_x.setter
    def use_scale_x(self, value: bool) -> None:
        set_property(self.node, 'use_scale_x', value)

    @property
    def use_scale_y(self) -> bool:
        return self.node.use_scale_y

    @use_scale_y.setter
    def use_scale_y(self, value: bool) -> None:
        set_property(self.node, 'use_scale_y', value)

    @property
    def use_scale_z(self) -> bool:
        return self.node.use_scale_z

    @use_scale_z.setter
    def use_scale_z(self, value: bool) -> None:
        set_property(self.node, 'use_scale_z', value)

class Warning(BaseNode):
    _bl_idname = 'GeometryNodeWarning'

    def __init__(self, show: InputBoolean=None, message: InputString='', *, warning_type: Literal['ERROR', 'WARNING', 'INFO']='ERROR'):
        super().__init__()
        key_args = {'Show': show, 'Message': message}
        self.warning_type = warning_type
        self._establish_links(**key_args)

    @classmethod
    def error(cls, show: InputBoolean=None, message: InputString='') -> 'Warning':
        return cls(warning_type='ERROR', show=show, message=message)

    @classmethod
    def warning(cls, show: InputBoolean=None, message: InputString='') -> 'Warning':
        return cls(warning_type='WARNING', show=show, message=message)

    @classmethod
    def info(cls, show: InputBoolean=None, message: InputString='') -> 'Warning':
        return cls(warning_type='INFO', show=show, message=message)

    @property
    def warning_type(self) -> Literal['ERROR', 'WARNING', 'INFO']:
        return self.node.warning_type

    @warning_type.setter
    def warning_type(self, value: Literal['ERROR', 'WARNING', 'INFO']) -> None:
        set_property(self.node, 'warning_type', value)
