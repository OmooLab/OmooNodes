# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import FloatSocket, VectorSocket
from ...socket_types import InputFloat, InputVector

class RadialTiling(BaseNode):
    _bl_idname = 'ShaderNodeRadialTiling'

    def __init__(self, vector: InputVector=(0.0, 0.0), sides: InputFloat=5.0, roundness: InputFloat=0.0, *, normalize: bool=False):
        super().__init__()
        key_args = {'Vector': vector, 'Sides': sides, 'Roundness': roundness}
        self.normalize = normalize
        self._establish_links(**key_args)

    @property
    def normalize(self) -> bool:
        return self.node.normalize

    @normalize.setter
    def normalize(self, value: bool) -> None:
        set_property(self.node, 'normalize', value)

class VectorCurves(BaseNode):
    _bl_idname = 'ShaderNodeVectorCurve'

    def __init__(self, fac: InputFloat=1.0, vector: InputVector=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Fac': fac, 'Vector': vector}
        self._establish_links(**key_args)

class VectorMath(BaseNode):
    _bl_idname = 'ShaderNodeVectorMath'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0), vector_002: InputVector=(0.0, 0.0, 0.0), scale: InputFloat=1.0, *, operation: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT', 'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH', 'SCALE', 'NORMALIZE', 'ABSOLUTE', 'POWER', 'SIGN', 'MINIMUM', 'MAXIMUM', 'ROUND', 'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP', 'SINE', 'COSINE', 'TANGENT']='ADD'):
        super().__init__()
        key_args = {'Vector': vector, 'Vector_001': vector_001, 'Vector_002': vector_002, 'Scale': scale}
        self.operation = operation
        self._establish_links(**key_args)

    @classmethod
    def add(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='ADD', vector=vector, vector_001=vector_001)

    @classmethod
    def subtract(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='SUBTRACT', vector=vector, vector_001=vector_001)

    @classmethod
    def multiply(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='MULTIPLY', vector=vector, vector_001=vector_001)

    @classmethod
    def divide(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='DIVIDE', vector=vector, vector_001=vector_001)

    @classmethod
    def multiply_add(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0), vector_002: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='MULTIPLY_ADD', vector=vector, vector_001=vector_001, vector_002=vector_002)

    @classmethod
    def cross_product(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='CROSS_PRODUCT', vector=vector, vector_001=vector_001)

    @classmethod
    def project(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='PROJECT', vector=vector, vector_001=vector_001)

    @classmethod
    def reflect(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='REFLECT', vector=vector, vector_001=vector_001)

    @classmethod
    def refract(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0), scale: InputFloat=1.0) -> 'VectorMath':
        return cls(operation='REFRACT', vector=vector, vector_001=vector_001, scale=scale)

    @classmethod
    def faceforward(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0), vector_002: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='FACEFORWARD', vector=vector, vector_001=vector_001, vector_002=vector_002)

    @classmethod
    def dot_product(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='DOT_PRODUCT', vector=vector, vector_001=vector_001)

    @classmethod
    def distance(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='DISTANCE', vector=vector, vector_001=vector_001)

    @classmethod
    def length(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='LENGTH', vector=vector)

    @classmethod
    def scale(cls, vector: InputVector=(0.0, 0.0, 0.0), scale: InputFloat=1.0) -> 'VectorMath':
        return cls(operation='SCALE', vector=vector, scale=scale)

    @classmethod
    def normalize(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='NORMALIZE', vector=vector)

    @classmethod
    def absolute(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='ABSOLUTE', vector=vector)

    @classmethod
    def power(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='POWER', vector=vector, vector_001=vector_001)

    @classmethod
    def sign(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='SIGN', vector=vector)

    @classmethod
    def minimum(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='MINIMUM', vector=vector, vector_001=vector_001)

    @classmethod
    def maximum(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='MAXIMUM', vector=vector, vector_001=vector_001)

    @classmethod
    def round(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='ROUND', vector=vector)

    @classmethod
    def floor(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='FLOOR', vector=vector)

    @classmethod
    def ceil(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='CEIL', vector=vector)

    @classmethod
    def fraction(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='FRACTION', vector=vector)

    @classmethod
    def modulo(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='MODULO', vector=vector, vector_001=vector_001)

    @classmethod
    def wrap(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0), vector_002: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='WRAP', vector=vector, vector_001=vector_001, vector_002=vector_002)

    @classmethod
    def snap(cls, vector: InputVector=(0.0, 0.0, 0.0), vector_001: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='SNAP', vector=vector, vector_001=vector_001)

    @classmethod
    def sine(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='SINE', vector=vector)

    @classmethod
    def cosine(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='COSINE', vector=vector)

    @classmethod
    def tangent(cls, vector: InputVector=(0.0, 0.0, 0.0)) -> 'VectorMath':
        return cls(operation='TANGENT', vector=vector)

    @property
    def operation(self) -> Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT', 'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH', 'SCALE', 'NORMALIZE', 'ABSOLUTE', 'POWER', 'SIGN', 'MINIMUM', 'MAXIMUM', 'ROUND', 'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP', 'SINE', 'COSINE', 'TANGENT']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT', 'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH', 'SCALE', 'NORMALIZE', 'ABSOLUTE', 'POWER', 'SIGN', 'MINIMUM', 'MAXIMUM', 'ROUND', 'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP', 'SINE', 'COSINE', 'TANGENT']) -> None:
        set_property(self.node, 'operation', value)

class VectorRotate(BaseNode):
    _bl_idname = 'ShaderNodeVectorRotate'

    def __init__(self, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), axis: InputVector=(0.0, 0.0, 1.0), angle: InputFloat=0.0, rotation: InputVector=(0.0, 0.0, 0.0), *, rotation_type: Literal['AXIS_ANGLE', 'X_AXIS', 'Y_AXIS', 'Z_AXIS', 'EULER_XYZ']='AXIS_ANGLE', invert: bool=False):
        super().__init__()
        key_args = {'Vector': vector, 'Center': center, 'Axis': axis, 'Angle': angle, 'Rotation': rotation}
        self.rotation_type = rotation_type
        self.invert = invert
        self._establish_links(**key_args)

    @classmethod
    def axis_angle(cls, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), axis: InputVector=(0.0, 0.0, 1.0), angle: InputFloat=0.0, *, invert: bool=False) -> 'VectorRotate':
        return cls(rotation_type='AXIS_ANGLE', vector=vector, center=center, axis=axis, angle=angle, invert=invert)

    @classmethod
    def x_axis(cls, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), angle: InputFloat=0.0, *, invert: bool=False) -> 'VectorRotate':
        return cls(rotation_type='X_AXIS', vector=vector, center=center, angle=angle, invert=invert)

    @classmethod
    def y_axis(cls, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), angle: InputFloat=0.0, *, invert: bool=False) -> 'VectorRotate':
        return cls(rotation_type='Y_AXIS', vector=vector, center=center, angle=angle, invert=invert)

    @classmethod
    def z_axis(cls, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), angle: InputFloat=0.0, *, invert: bool=False) -> 'VectorRotate':
        return cls(rotation_type='Z_AXIS', vector=vector, center=center, angle=angle, invert=invert)

    @classmethod
    def euler(cls, vector: InputVector=None, center: InputVector=(0.0, 0.0, 0.0), rotation: InputVector=(0.0, 0.0, 0.0), *, invert: bool=False) -> 'VectorRotate':
        return cls(rotation_type='EULER_XYZ', vector=vector, center=center, rotation=rotation, invert=invert)

    @property
    def rotation_type(self) -> Literal['AXIS_ANGLE', 'X_AXIS', 'Y_AXIS', 'Z_AXIS', 'EULER_XYZ']:
        return self.node.rotation_type

    @rotation_type.setter
    def rotation_type(self, value: Literal['AXIS_ANGLE', 'X_AXIS', 'Y_AXIS', 'Z_AXIS', 'EULER_XYZ']) -> None:
        set_property(self.node, 'rotation_type', value)

    @property
    def invert(self) -> bool:
        return self.node.invert

    @invert.setter
    def invert(self, value: bool) -> None:
        set_property(self.node, 'invert', value)
