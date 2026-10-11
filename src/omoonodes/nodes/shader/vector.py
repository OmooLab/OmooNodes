# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket, VectorSocket
from ...socket_types import InputColor, InputFloat, InputVector

class Bump(BaseNode):
    _bl_idname = 'ShaderNodeBump'

    def __init__(self, strength: InputFloat=1.0, distance: InputFloat=0.001, filter_width: InputFloat=0.1, height: InputFloat=None, normal: InputVector=None, *, invert: bool=False):
        super().__init__()
        key_args = {'Strength': strength, 'Distance': distance, 'Filter Width': filter_width, 'Height': height, 'Normal': normal}
        self.invert = invert
        self._establish_links(**key_args)

    @property
    def invert(self) -> bool:
        return self.node.invert

    @invert.setter
    def invert(self, value: bool) -> None:
        set_property(self.node, 'invert', value)

class Displacement(BaseNode):
    _bl_idname = 'ShaderNodeDisplacement'

    def __init__(self, height: InputFloat=0.0, midlevel: InputFloat=0.5, scale: InputFloat=0.01, normal: InputVector=None, *, space: Literal['OBJECT', 'WORLD']='OBJECT'):
        super().__init__()
        key_args = {'Height': height, 'Midlevel': midlevel, 'Scale': scale, 'Normal': normal}
        self.space = space
        self._establish_links(**key_args)

    @property
    def space(self) -> Literal['OBJECT', 'WORLD']:
        return self.node.space

    @space.setter
    def space(self, value: Literal['OBJECT', 'WORLD']) -> None:
        set_property(self.node, 'space', value)

class Mapping(BaseNode):
    _bl_idname = 'ShaderNodeMapping'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0), location: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0), *, vector_type: Literal['POINT', 'TEXTURE', 'VECTOR', 'NORMAL']='POINT'):
        super().__init__()
        key_args = {'Vector': vector, 'Location': location, 'Rotation': rotation, 'Scale': scale}
        self.vector_type = vector_type
        self._establish_links(**key_args)

    @classmethod
    def point(cls, vector: InputVector=(0.0, 0.0, 0.0), location: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)) -> 'Mapping':
        return cls(vector_type='POINT', vector=vector, location=location, rotation=rotation, scale=scale)

    @classmethod
    def texture(cls, vector: InputVector=(0.0, 0.0, 0.0), location: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)) -> 'Mapping':
        return cls(vector_type='TEXTURE', vector=vector, location=location, rotation=rotation, scale=scale)

    @classmethod
    def vector(cls, vector: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)) -> 'Mapping':
        return cls(vector_type='VECTOR', vector=vector, rotation=rotation, scale=scale)

    @classmethod
    def normal(cls, vector: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)) -> 'Mapping':
        return cls(vector_type='NORMAL', vector=vector, rotation=rotation, scale=scale)

    @property
    def vector_type(self) -> Literal['POINT', 'TEXTURE', 'VECTOR', 'NORMAL']:
        return self.node.vector_type

    @vector_type.setter
    def vector_type(self, value: Literal['POINT', 'TEXTURE', 'VECTOR', 'NORMAL']) -> None:
        set_property(self.node, 'vector_type', value)

class Normal(BaseNode):
    _bl_idname = 'ShaderNodeNormal'

    def __init__(self, normal: InputVector=(0.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'Normal': normal}
        self._establish_links(**key_args)

class NormalMap(BaseNode):
    _bl_idname = 'ShaderNodeNormalMap'

    def __init__(self, strength: InputFloat=1.0, color: InputColor=(0.5, 0.5, 1.0, 1.0), *, space: Literal['TANGENT', 'OBJECT', 'WORLD', 'BLENDER_OBJECT', 'BLENDER_WORLD']='TANGENT', uv_map: str='', convention: Literal['OPENGL', 'DIRECTX']='OPENGL', base: Literal['ORIGINAL', 'DISPLACED']='DISPLACED'):
        super().__init__()
        key_args = {'Strength': strength, 'Color': color}
        self.space = space
        self.uv_map = uv_map
        self.convention = convention
        self.base = base
        self._establish_links(**key_args)

    @property
    def space(self) -> Literal['TANGENT', 'OBJECT', 'WORLD', 'BLENDER_OBJECT', 'BLENDER_WORLD']:
        return self.node.space

    @space.setter
    def space(self, value: Literal['TANGENT', 'OBJECT', 'WORLD', 'BLENDER_OBJECT', 'BLENDER_WORLD']) -> None:
        set_property(self.node, 'space', value)

    @property
    def uv_map(self) -> str:
        return self.node.uv_map

    @uv_map.setter
    def uv_map(self, value: str) -> None:
        set_property(self.node, 'uv_map', value)

    @property
    def convention(self) -> Literal['OPENGL', 'DIRECTX']:
        return self.node.convention

    @convention.setter
    def convention(self, value: Literal['OPENGL', 'DIRECTX']) -> None:
        set_property(self.node, 'convention', value)

    @property
    def base(self) -> Literal['ORIGINAL', 'DISPLACED']:
        return self.node.base

    @base.setter
    def base(self, value: Literal['ORIGINAL', 'DISPLACED']) -> None:
        set_property(self.node, 'base', value)

class VectorDisplacement(BaseNode):
    _bl_idname = 'ShaderNodeVectorDisplacement'

    def __init__(self, vector: InputColor=None, midlevel: InputFloat=0.0, scale: InputFloat=0.01, *, space: Literal['TANGENT', 'OBJECT', 'WORLD']='TANGENT'):
        super().__init__()
        key_args = {'Vector': vector, 'Midlevel': midlevel, 'Scale': scale}
        self.space = space
        self._establish_links(**key_args)

    @property
    def space(self) -> Literal['TANGENT', 'OBJECT', 'WORLD']:
        return self.node.space

    @space.setter
    def space(self, value: Literal['TANGENT', 'OBJECT', 'WORLD']) -> None:
        set_property(self.node, 'space', value)

class VectorTransform(BaseNode):
    _bl_idname = 'ShaderNodeVectorTransform'

    def __init__(self, vector: InputVector=(0.5, 0.5, 0.5), *, vector_type: Literal['POINT', 'VECTOR', 'NORMAL']='VECTOR', convert_from: Literal['WORLD', 'OBJECT', 'CAMERA']='WORLD', convert_to: Literal['WORLD', 'OBJECT', 'CAMERA']='OBJECT'):
        super().__init__()
        key_args = {'Vector': vector}
        self.vector_type = vector_type
        self.convert_from = convert_from
        self.convert_to = convert_to
        self._establish_links(**key_args)

    @classmethod
    def point(cls, vector: InputVector=(0.5, 0.5, 0.5), *, convert_from: Literal['WORLD', 'OBJECT', 'CAMERA']='WORLD', convert_to: Literal['WORLD', 'OBJECT', 'CAMERA']='OBJECT') -> 'VectorTransform':
        return cls(vector_type='POINT', vector=vector, convert_from=convert_from, convert_to=convert_to)

    @classmethod
    def vector(cls, vector: InputVector=(0.5, 0.5, 0.5), *, convert_from: Literal['WORLD', 'OBJECT', 'CAMERA']='WORLD', convert_to: Literal['WORLD', 'OBJECT', 'CAMERA']='OBJECT') -> 'VectorTransform':
        return cls(vector_type='VECTOR', vector=vector, convert_from=convert_from, convert_to=convert_to)

    @classmethod
    def normal(cls, vector: InputVector=(0.5, 0.5, 0.5), *, convert_from: Literal['WORLD', 'OBJECT', 'CAMERA']='WORLD', convert_to: Literal['WORLD', 'OBJECT', 'CAMERA']='OBJECT') -> 'VectorTransform':
        return cls(vector_type='NORMAL', vector=vector, convert_from=convert_from, convert_to=convert_to)

    @property
    def vector_type(self) -> Literal['POINT', 'VECTOR', 'NORMAL']:
        return self.node.vector_type

    @vector_type.setter
    def vector_type(self, value: Literal['POINT', 'VECTOR', 'NORMAL']) -> None:
        set_property(self.node, 'vector_type', value)

    @property
    def convert_from(self) -> Literal['WORLD', 'OBJECT', 'CAMERA']:
        return self.node.convert_from

    @convert_from.setter
    def convert_from(self, value: Literal['WORLD', 'OBJECT', 'CAMERA']) -> None:
        set_property(self.node, 'convert_from', value)

    @property
    def convert_to(self) -> Literal['WORLD', 'OBJECT', 'CAMERA']:
        return self.node.convert_to

    @convert_to.setter
    def convert_to(self, value: Literal['WORLD', 'OBJECT', 'CAMERA']) -> None:
        set_property(self.node, 'convert_to', value)
