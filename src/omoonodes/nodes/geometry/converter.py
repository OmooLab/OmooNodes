# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
TList = typing.TypeVar('TList')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, BooleanSocketList, BundleSocket, BundleSocketList, ClosureSocket, ClosureSocketList, CollectionSocket, CollectionSocketList, ColorSocket, ColorSocketList, FloatSocket, FloatSocketList, FontSocket, FontSocketList, GeometrySocket, GeometrySocketList, ImageSocket, ImageSocketList, IntegerSocket, IntegerSocketList, MaterialSocket, MaterialSocketList, MatrixSocket, MatrixSocketList, MenuSocket, MenuSocketList, ObjectSocket, ObjectSocketList, RotationSocket, RotationSocketList, SoundSocket, SoundSocketList, StringSocket, StringSocketList, VectorSocket, VectorSocketList
from ...socket_types import InputAny, InputBoolean, InputBooleanList, InputBundle, InputBundleList, InputClosure, InputClosureList, InputCollection, InputCollectionList, InputColor, InputColorList, InputFloat, InputFloatGrid, InputFloatList, InputFont, InputFontList, InputGeometry, InputGeometryList, InputImage, InputImageList, InputInteger, InputIntegerList, InputMaterial, InputMaterialList, InputMatrix, InputMatrixList, InputMenu, InputMenuList, InputObject, InputObjectList, InputRotation, InputRotationList, InputSound, InputSoundList, InputString, InputStringList, InputVector, InputVectorList, _AttributeDomains
from .._mixins import _ClosureToListMixin, _CombineBundleMixin, _FieldToListMixin, _FormatStringMixin, _SeparateBundleMixin

class AccumulateField(BaseNode):
    _bl_idname = 'GeometryNodeAccumulateField'

    def __init__(self, value: InputAny=1.0, group_index: InputInteger=None, *, data_type: Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'TRANSFORM']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Value': value, 'Group Index': group_index}
        self.data_type = data_type
        self.domain = domain
        self._establish_links(**key_args)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'TRANSFORM']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'TRANSFORM']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    class _AccumulateFieldDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None, group_index: InputInteger=0) -> 'AccumulateField[FloatSocket]':
            return AccumulateField(value, group_index, domain=self._domain, data_type='FLOAT')

        def integer(self, value: InputInteger=None, group_index: InputInteger=0) -> 'AccumulateField[IntegerSocket]':
            return AccumulateField(value, group_index, domain=self._domain, data_type='INT')

        def vector(self, value: InputVector=None, group_index: InputInteger=0) -> 'AccumulateField[VectorSocket]':
            return AccumulateField(value, group_index, domain=self._domain, data_type='FLOAT_VECTOR')

        def transform(self, value: InputMatrix=None, group_index: InputInteger=0) -> 'AccumulateField[MatrixSocket]':
            return AccumulateField(value, group_index, domain=self._domain, data_type='TRANSFORM')
    point: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('POINT')
    edge: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('EDGE')
    face: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('FACE')
    corner: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('CORNER')
    spline: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('CURVE')
    instance: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('INSTANCE')
    layer: _AccumulateFieldDomainFactory = _AccumulateFieldDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class AlignRotationToVector(BaseNode):
    _bl_idname = 'FunctionNodeAlignRotationToVector'

    def __init__(self, rotation: InputRotation=None, factor: InputFloat=1.0, vector: InputVector=(0.0, 0.0, 1.0), *, axis: Literal['X', 'Y', 'Z']='Z', pivot_axis: Literal['AUTO', 'X', 'Y', 'Z']='AUTO'):
        super().__init__()
        key_args = {'Rotation': rotation, 'Factor': factor, 'Vector': vector}
        self.axis = axis
        self.pivot_axis = pivot_axis
        self._establish_links(**key_args)

    @property
    def axis(self) -> Literal['X', 'Y', 'Z']:
        return self.node.axis

    @axis.setter
    def axis(self, value: Literal['X', 'Y', 'Z']) -> None:
        set_property(self.node, 'axis', value)

    @property
    def pivot_axis(self) -> Literal['AUTO', 'X', 'Y', 'Z']:
        return self.node.pivot_axis

    @pivot_axis.setter
    def pivot_axis(self, value: Literal['AUTO', 'X', 'Y', 'Z']) -> None:
        set_property(self.node, 'pivot_axis', value)

class AxesToRotation(BaseNode):
    _bl_idname = 'FunctionNodeAxesToRotation'

    def __init__(self, primary_axis: InputVector=(0.0, 0.0, 1.0), secondary_axis: InputVector=(1.0, 0.0, 0.0), *, primary: Literal['X', 'Y', 'Z']='Z', secondary: Literal['X', 'Y', 'Z']='X'):
        super().__init__()
        key_args = {'Primary Axis': primary_axis, 'Secondary Axis': secondary_axis}
        self.primary = primary
        self.secondary = secondary
        self._establish_links(**key_args)

    @property
    def primary(self) -> Literal['X', 'Y', 'Z']:
        return self.node.primary_axis

    @primary.setter
    def primary(self, value: Literal['X', 'Y', 'Z']) -> None:
        set_property(self.node, 'primary_axis', value)

    @property
    def secondary(self) -> Literal['X', 'Y', 'Z']:
        return self.node.secondary_axis

    @secondary.setter
    def secondary(self, value: Literal['X', 'Y', 'Z']) -> None:
        set_property(self.node, 'secondary_axis', value)

class AxisAngleToRotation(BaseNode):
    _bl_idname = 'FunctionNodeAxisAngleToRotation'

    def __init__(self, axis: InputVector=(0.0, 0.0, 1.0), angle: InputFloat=0.0):
        super().__init__()
        key_args = {'Axis': axis, 'Angle': angle}
        self._establish_links(**key_args)

class BitMath(BaseNode):
    _bl_idname = 'FunctionNodeBitMath'

    def __init__(self, a: InputInteger=0, b: InputInteger=0, shift: InputInteger=0, *, operation: Literal['AND', 'OR', 'XOR', 'NOT', 'SHIFT', 'ROTATE']='AND'):
        super().__init__()
        key_args = {'A': a, 'B': b, 'Shift': shift}
        self.operation = operation
        self._establish_links(**key_args)

    @classmethod
    def l_and(cls, a: InputInteger=0, b: InputInteger=0) -> 'BitMath':
        return cls(operation='AND', a=a, b=b)

    @classmethod
    def l_or(cls, a: InputInteger=0, b: InputInteger=0) -> 'BitMath':
        return cls(operation='OR', a=a, b=b)

    @classmethod
    def exclusive_or(cls, a: InputInteger=0, b: InputInteger=0) -> 'BitMath':
        return cls(operation='XOR', a=a, b=b)

    @classmethod
    def l_not(cls, a: InputInteger=0) -> 'BitMath':
        return cls(operation='NOT', a=a)

    @classmethod
    def shift(cls, a: InputInteger=0, shift: InputInteger=0) -> 'BitMath':
        return cls(operation='SHIFT', a=a, shift=shift)

    @classmethod
    def rotate(cls, a: InputInteger=0, shift: InputInteger=0) -> 'BitMath':
        return cls(operation='ROTATE', a=a, shift=shift)

    @property
    def operation(self) -> Literal['AND', 'OR', 'XOR', 'NOT', 'SHIFT', 'ROTATE']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['AND', 'OR', 'XOR', 'NOT', 'SHIFT', 'ROTATE']) -> None:
        set_property(self.node, 'operation', value)

class Blackbody(BaseNode):
    _bl_idname = 'ShaderNodeBlackbody'

    def __init__(self, temperature: InputFloat=6500.0):
        super().__init__()
        key_args = {'Temperature': temperature}
        self._establish_links(**key_args)

class BooleanMath(BaseNode):
    _bl_idname = 'FunctionNodeBooleanMath'

    def __init__(self, boolean: InputBoolean=False, boolean_001: InputBoolean=False, *, operation: Literal['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XNOR', 'XOR', 'IMPLY', 'NIMPLY']='AND'):
        super().__init__()
        key_args = {'Boolean': boolean, 'Boolean_001': boolean_001}
        self.operation = operation
        self._establish_links(**key_args)

    @classmethod
    def l_and(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='AND', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def l_or(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='OR', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def l_not(cls, boolean: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='NOT', boolean=boolean)

    @classmethod
    def not_and(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='NAND', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def nor(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='NOR', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def equal(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='XNOR', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def not_equal(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='XOR', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def imply(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='IMPLY', boolean=boolean, boolean_001=boolean_001)

    @classmethod
    def subtract(cls, boolean: InputBoolean=False, boolean_001: InputBoolean=False) -> 'BooleanMath':
        return cls(operation='NIMPLY', boolean=boolean, boolean_001=boolean_001)

    @property
    def operation(self) -> Literal['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XNOR', 'XOR', 'IMPLY', 'NIMPLY']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XNOR', 'XOR', 'IMPLY', 'NIMPLY']) -> None:
        set_property(self.node, 'operation', value)

class Clamp(BaseNode):
    _bl_idname = 'ShaderNodeClamp'

    def __init__(self, value: InputFloat=1.0, min: InputFloat=0.0, max: InputFloat=1.0, *, clamp_type: Literal['MINMAX', 'RANGE']='MINMAX'):
        super().__init__()
        key_args = {'Value': value, 'Min': min, 'Max': max}
        self.clamp_type = clamp_type
        self._establish_links(**key_args)

    @classmethod
    def min_max(cls, value: InputFloat=1.0, min: InputFloat=0.0, max: InputFloat=1.0) -> 'Clamp':
        return cls(clamp_type='MINMAX', value=value, min=min, max=max)

    @classmethod
    def range(cls, value: InputFloat=1.0, min: InputFloat=0.0, max: InputFloat=1.0) -> 'Clamp':
        return cls(clamp_type='RANGE', value=value, min=min, max=max)

    @property
    def clamp_type(self) -> Literal['MINMAX', 'RANGE']:
        return self.node.clamp_type

    @clamp_type.setter
    def clamp_type(self, value: Literal['MINMAX', 'RANGE']) -> None:
        set_property(self.node, 'clamp_type', value)

class ClosureToList(_ClosureToListMixin, BaseNode):
    _bl_idname = 'GeometryNodeClosureToList'

class ClusterByConnected(BaseNode):
    _bl_idname = 'GeometryNodeClusterByConnected'

    def __init__(self, selection: InputBoolean=None, position: InputVector=None, distance: InputFloat=0.001):
        super().__init__()
        key_args = {'Selection': selection, 'Position': position, 'Distance': distance}
        self._establish_links(**key_args)

class ClusterByDistance(BaseNode):
    _bl_idname = 'GeometryNodeClusterByDistance'

    def __init__(self, selection: InputBoolean=None, group_id: InputInteger=None, position: InputVector=None, distance: InputFloat=0.001):
        super().__init__()
        key_args = {'Selection': selection, 'Group ID': group_id, 'Position': position, 'Distance': distance}
        self._establish_links(**key_args)

class CombineBundle(_CombineBundleMixin, BaseNode):
    _bl_idname = 'NodeCombineBundle'

    @property
    def define_signature(self) -> bool:
        return self.node.define_signature

    @define_signature.setter
    def define_signature(self, value: bool) -> None:
        set_property(self.node, 'define_signature', value)

class CombineColor(BaseNode):
    _bl_idname = 'FunctionNodeCombineColor'

    def __init__(self, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0, *, mode: Literal['RGB', 'HSV', 'HSL']='RGB'):
        super().__init__()
        key_args = {'Red': red, 'Green': green, 'Blue': blue, 'Alpha': alpha}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0) -> 'CombineColor':
        return cls(mode='RGB', red=red, green=green, blue=blue, alpha=alpha)

    @classmethod
    def hsv(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0) -> 'CombineColor':
        return cls(mode='HSV', red=red, green=green, blue=blue, alpha=alpha)

    @classmethod
    def hsl(cls, red: InputFloat=0.0, green: InputFloat=0.0, blue: InputFloat=0.0, alpha: InputFloat=1.0) -> 'CombineColor':
        return cls(mode='HSL', red=red, green=green, blue=blue, alpha=alpha)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL']) -> None:
        set_property(self.node, 'mode', value)

class CombineMatrix(BaseNode):
    _bl_idname = 'FunctionNodeCombineMatrix'

    def __init__(self, column_1_row_1: InputFloat=1.0, column_1_row_2: InputFloat=0.0, column_1_row_3: InputFloat=0.0, column_1_row_4: InputFloat=0.0, column_2_row_1: InputFloat=0.0, column_2_row_2: InputFloat=1.0, column_2_row_3: InputFloat=0.0, column_2_row_4: InputFloat=0.0, column_3_row_1: InputFloat=0.0, column_3_row_2: InputFloat=0.0, column_3_row_3: InputFloat=1.0, column_3_row_4: InputFloat=0.0, column_4_row_1: InputFloat=0.0, column_4_row_2: InputFloat=0.0, column_4_row_3: InputFloat=0.0, column_4_row_4: InputFloat=1.0):
        super().__init__()
        key_args = {'Column 1 Row 1': column_1_row_1, 'Column 1 Row 2': column_1_row_2, 'Column 1 Row 3': column_1_row_3, 'Column 1 Row 4': column_1_row_4, 'Column 2 Row 1': column_2_row_1, 'Column 2 Row 2': column_2_row_2, 'Column 2 Row 3': column_2_row_3, 'Column 2 Row 4': column_2_row_4, 'Column 3 Row 1': column_3_row_1, 'Column 3 Row 2': column_3_row_2, 'Column 3 Row 3': column_3_row_3, 'Column 3 Row 4': column_3_row_4, 'Column 4 Row 1': column_4_row_1, 'Column 4 Row 2': column_4_row_2, 'Column 4 Row 3': column_4_row_3, 'Column 4 Row 4': column_4_row_4}
        self._establish_links(**key_args)

class CombineTransform(BaseNode):
    _bl_idname = 'FunctionNodeCombineTransform'

    def __init__(self, translation: InputVector=(0.0, 0.0, 0.0), rotation: InputRotation=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)):
        super().__init__()
        key_args = {'Translation': translation, 'Rotation': rotation, 'Scale': scale}
        self._establish_links(**key_args)

class CombineXYZ(BaseNode):
    _bl_idname = 'ShaderNodeCombineXYZ'

    def __init__(self, x: InputFloat=0.0, y: InputFloat=0.0, z: InputFloat=0.0):
        super().__init__()
        key_args = {'X': x, 'Y': y, 'Z': z}
        self._establish_links(**key_args)

class EulerToRotation(BaseNode):
    _bl_idname = 'FunctionNodeEulerToRotation'

    def __init__(self, euler: InputVector=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Euler': euler}
        self._establish_links(**key_args)

class EvaluateAtIndex(BaseNode):
    _bl_idname = 'GeometryNodeFieldAtIndex'

    def __init__(self, value: InputAny=None, index: InputInteger=0, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT', data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Value': value, 'Index': index}
        self.domain = domain
        self.data_type = data_type
        self._establish_links(**key_args)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    class _EvaluateAtIndexDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None, index: InputInteger=0) -> 'EvaluateAtIndex[FloatSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='FLOAT')

        def integer(self, value: InputInteger=None, index: InputInteger=0) -> 'EvaluateAtIndex[IntegerSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='INT')

        def boolean(self, value: InputBoolean=None, index: InputInteger=0) -> 'EvaluateAtIndex[BooleanSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='BOOLEAN')

        def vector(self, value: InputVector=None, index: InputInteger=0) -> 'EvaluateAtIndex[VectorSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='FLOAT_VECTOR')

        def color(self, value: InputColor=None, index: InputInteger=0) -> 'EvaluateAtIndex[ColorSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='FLOAT_COLOR')

        def quaternion(self, value: InputRotation=None, index: InputInteger=0) -> 'EvaluateAtIndex[RotationSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='QUATERNION')

        def matrix(self, value: InputMatrix=None, index: InputInteger=0) -> 'EvaluateAtIndex[MatrixSocket]':
            return EvaluateAtIndex(value, index, domain=self._domain, data_type='FLOAT4X4')
    point: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('POINT')
    edge: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('EDGE')
    face: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('FACE')
    corner: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('CORNER')
    spline: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('CURVE')
    instance: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('INSTANCE')
    layer: _EvaluateAtIndexDomainFactory = _EvaluateAtIndexDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class EvaluateOnDomain(BaseNode):
    _bl_idname = 'GeometryNodeFieldOnDomain'

    def __init__(self, value: InputAny=0.0, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT', data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Value': value}
        self.domain = domain
        self.data_type = data_type
        self._establish_links(**key_args)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    class _EvaluateOnDomainDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None) -> 'EvaluateOnDomain[FloatSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='FLOAT')

        def integer(self, value: InputInteger=None) -> 'EvaluateOnDomain[IntegerSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='INT')

        def boolean(self, value: InputBoolean=None) -> 'EvaluateOnDomain[BooleanSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='BOOLEAN')

        def vector(self, value: InputVector=None) -> 'EvaluateOnDomain[VectorSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='FLOAT_VECTOR')

        def color(self, value: InputColor=None) -> 'EvaluateOnDomain[ColorSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='FLOAT_COLOR')

        def quaternion(self, value: InputRotation=None) -> 'EvaluateOnDomain[RotationSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='QUATERNION')

        def matrix(self, value: InputMatrix=None) -> 'EvaluateOnDomain[MatrixSocket]':
            return EvaluateOnDomain(value, domain=self._domain, data_type='FLOAT4X4')
    point: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('POINT')
    edge: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('EDGE')
    face: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('FACE')
    corner: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('CORNER')
    spline: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('CURVE')
    instance: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('INSTANCE')
    layer: _EvaluateOnDomainDomainFactory = _EvaluateOnDomainDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FieldAverage(BaseNode):
    _bl_idname = 'GeometryNodeFieldAverage'

    def __init__(self, value: InputAny=0.0, group_index: InputInteger=None, *, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Value': value, 'Group Index': group_index}
        self.data_type = data_type
        self.domain = domain
        self._establish_links(**key_args)

    @property
    def data_type(self) -> Literal['FLOAT', 'FLOAT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'FLOAT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    class _FieldAverageDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None, group_index: InputInteger=0) -> 'FieldAverage[FloatSocket]':
            return FieldAverage(value, group_index, domain=self._domain, data_type='FLOAT')

        def vector(self, value: InputVector=None, group_index: InputInteger=0) -> 'FieldAverage[VectorSocket]':
            return FieldAverage(value, group_index, domain=self._domain, data_type='FLOAT_VECTOR')
    point: _FieldAverageDomainFactory = _FieldAverageDomainFactory('POINT')
    edge: _FieldAverageDomainFactory = _FieldAverageDomainFactory('EDGE')
    face: _FieldAverageDomainFactory = _FieldAverageDomainFactory('FACE')
    corner: _FieldAverageDomainFactory = _FieldAverageDomainFactory('CORNER')
    spline: _FieldAverageDomainFactory = _FieldAverageDomainFactory('CURVE')
    instance: _FieldAverageDomainFactory = _FieldAverageDomainFactory('INSTANCE')
    layer: _FieldAverageDomainFactory = _FieldAverageDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FieldMinAndMax(BaseNode):
    _bl_idname = 'GeometryNodeFieldMinAndMax'

    def __init__(self, value: InputAny=0.0, group_index: InputInteger=None, *, data_type: Literal['FLOAT', 'INT', 'FLOAT_VECTOR']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Value': value, 'Group Index': group_index}
        self.data_type = data_type
        self.domain = domain
        self._establish_links(**key_args)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'FLOAT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'FLOAT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    class _FieldMinAndMaxDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None, group_index: InputInteger=0) -> 'FieldMinAndMax[FloatSocket]':
            return FieldMinAndMax(value, group_index, domain=self._domain, data_type='FLOAT')

        def integer(self, value: InputInteger=None, group_index: InputInteger=0) -> 'FieldMinAndMax[IntegerSocket]':
            return FieldMinAndMax(value, group_index, domain=self._domain, data_type='INT')

        def vector(self, value: InputVector=None, group_index: InputInteger=0) -> 'FieldMinAndMax[VectorSocket]':
            return FieldMinAndMax(value, group_index, domain=self._domain, data_type='FLOAT_VECTOR')
    point: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('POINT')
    edge: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('EDGE')
    face: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('FACE')
    corner: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('CORNER')
    spline: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('CURVE')
    instance: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('INSTANCE')
    layer: _FieldMinAndMaxDomainFactory = _FieldMinAndMaxDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FieldVariance(BaseNode):
    _bl_idname = 'GeometryNodeFieldVariance'

    def __init__(self, value: InputAny=0.0, group_index: InputInteger=None, *, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Value': value, 'Group Index': group_index}
        self.data_type = data_type
        self.domain = domain
        self._establish_links(**key_args)

    @property
    def data_type(self) -> Literal['FLOAT', 'FLOAT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'FLOAT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

    class _FieldVarianceDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, value: InputFloat=None, group_index: InputInteger=0) -> 'FieldVariance[FloatSocket]':
            return FieldVariance(value, group_index, domain=self._domain, data_type='FLOAT')

        def vector(self, value: InputVector=None, group_index: InputInteger=0) -> 'FieldVariance[VectorSocket]':
            return FieldVariance(value, group_index, domain=self._domain, data_type='FLOAT_VECTOR')
    point: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('POINT')
    edge: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('EDGE')
    face: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('FACE')
    corner: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('CORNER')
    spline: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('CURVE')
    instance: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('INSTANCE')
    layer: _FieldVarianceDomainFactory = _FieldVarianceDomainFactory('LAYER')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FieldToList(_FieldToListMixin, BaseNode):
    _bl_idname = 'GeometryNodeFieldToList'

class FilterList(BaseNode):
    _bl_idname = 'GeometryNodeFilterList'

    def __init__(self, list: InputAny=None, selection: InputBoolean=None, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT'):
        super().__init__()
        key_args = {'List': list, 'Selection': selection}
        self.socket_type = socket_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, list: InputFloatList=None, selection: InputBoolean=None) -> 'FilterList[FloatSocketList]':
        return FilterList(socket_type='FLOAT', list=list, selection=selection)

    @classmethod
    def integer(cls, list: InputIntegerList=None, selection: InputBoolean=None) -> 'FilterList[IntegerSocketList]':
        return FilterList(socket_type='INT', list=list, selection=selection)

    @classmethod
    def boolean(cls, list: InputBooleanList=None, selection: InputBoolean=None) -> 'FilterList[BooleanSocketList]':
        return FilterList(socket_type='BOOLEAN', list=list, selection=selection)

    @classmethod
    def vector(cls, list: InputVectorList=None, selection: InputBoolean=None) -> 'FilterList[VectorSocketList]':
        return FilterList(socket_type='VECTOR', list=list, selection=selection)

    @classmethod
    def color(cls, list: InputColorList=None, selection: InputBoolean=None) -> 'FilterList[ColorSocketList]':
        return FilterList(socket_type='RGBA', list=list, selection=selection)

    @classmethod
    def rotation(cls, list: InputRotationList=None, selection: InputBoolean=None) -> 'FilterList[RotationSocketList]':
        return FilterList(socket_type='ROTATION', list=list, selection=selection)

    @classmethod
    def matrix(cls, list: InputMatrixList=None, selection: InputBoolean=None) -> 'FilterList[MatrixSocketList]':
        return FilterList(socket_type='MATRIX', list=list, selection=selection)

    @classmethod
    def string(cls, list: InputStringList=None, selection: InputBoolean=None) -> 'FilterList[StringSocketList]':
        return FilterList(socket_type='STRING', list=list, selection=selection)

    @classmethod
    def menu(cls, list: InputMenuList=None, selection: InputBoolean=None) -> 'FilterList[MenuSocketList]':
        return FilterList(socket_type='MENU', list=list, selection=selection)

    @classmethod
    def object(cls, list: InputObjectList=None, selection: InputBoolean=None) -> 'FilterList[ObjectSocketList]':
        return FilterList(socket_type='OBJECT', list=list, selection=selection)

    @classmethod
    def image(cls, list: InputImageList=None, selection: InputBoolean=None) -> 'FilterList[ImageSocketList]':
        return FilterList(socket_type='IMAGE', list=list, selection=selection)

    @classmethod
    def geometry(cls, list: InputGeometryList=None, selection: InputBoolean=None) -> 'FilterList[GeometrySocketList]':
        return FilterList(socket_type='GEOMETRY', list=list, selection=selection)

    @classmethod
    def collection(cls, list: InputCollectionList=None, selection: InputBoolean=None) -> 'FilterList[CollectionSocketList]':
        return FilterList(socket_type='COLLECTION', list=list, selection=selection)

    @classmethod
    def material(cls, list: InputMaterialList=None, selection: InputBoolean=None) -> 'FilterList[MaterialSocketList]':
        return FilterList(socket_type='MATERIAL', list=list, selection=selection)

    @classmethod
    def bundle(cls, list: InputBundleList=None, selection: InputBoolean=None) -> 'FilterList[BundleSocketList]':
        return FilterList(socket_type='BUNDLE', list=list, selection=selection)

    @classmethod
    def closure(cls, list: InputClosureList=None, selection: InputBoolean=None) -> 'FilterList[ClosureSocketList]':
        return FilterList(socket_type='CLOSURE', list=list, selection=selection)

    @classmethod
    def font(cls, list: InputFontList=None, selection: InputBoolean=None) -> 'FilterList[FontSocketList]':
        return FilterList(socket_type='FONT', list=list, selection=selection)

    @classmethod
    def sound(cls, list: InputSoundList=None, selection: InputBoolean=None) -> 'FilterList[SoundSocketList]':
        return FilterList(socket_type='SOUND', list=list, selection=selection)

    @property
    def socket_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.socket_type

    @socket_type.setter
    def socket_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'socket_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FindInString(BaseNode):
    _bl_idname = 'FunctionNodeFindInString'

    def __init__(self, string: InputString='', search: InputString='', mode: InputMenu | Literal['From Start', 'From End']='From Start'):
        super().__init__()
        key_args = {'String': string, 'Search': search, 'Mode': mode}
        self._establish_links(**key_args)

class FloatToInteger(BaseNode):
    _bl_idname = 'FunctionNodeFloatToInt'

    def __init__(self, float: InputFloat=0.0, *, rounding_mode: Literal['ROUND', 'FLOOR', 'CEILING', 'TRUNCATE']='ROUND'):
        super().__init__()
        key_args = {'Float': float}
        self.rounding_mode = rounding_mode
        self._establish_links(**key_args)

    @property
    def rounding_mode(self) -> Literal['ROUND', 'FLOOR', 'CEILING', 'TRUNCATE']:
        return self.node.rounding_mode

    @rounding_mode.setter
    def rounding_mode(self, value: Literal['ROUND', 'FLOOR', 'CEILING', 'TRUNCATE']) -> None:
        set_property(self.node, 'rounding_mode', value)

class FormatString(_FormatStringMixin, BaseNode):
    _bl_idname = 'FunctionNodeFormatString'

class GetBundleItem(BaseNode):
    _bl_idname = 'NodeGetBundleItem'

    def __init__(self, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT', structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO'):
        super().__init__()
        key_args = {'Bundle': bundle, 'Path': path, 'Remove': remove}
        self.socket_type = socket_type
        self.structure_type = structure_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(socket_type='FLOAT', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def integer(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[IntegerSocket]':
        return GetBundleItem(socket_type='INT', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def boolean(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[BooleanSocket]':
        return GetBundleItem(socket_type='BOOLEAN', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def vector(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[VectorSocket]':
        return GetBundleItem(socket_type='VECTOR', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def color(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[ColorSocket]':
        return GetBundleItem(socket_type='RGBA', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def rotation(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[RotationSocket]':
        return GetBundleItem(socket_type='ROTATION', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def matrix(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[MatrixSocket]':
        return GetBundleItem(socket_type='MATRIX', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def string(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[StringSocket]':
        return GetBundleItem(socket_type='STRING', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def menu(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[MenuSocket]':
        return GetBundleItem(socket_type='MENU', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def object(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[ObjectSocket]':
        return GetBundleItem(socket_type='OBJECT', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def image(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[ImageSocket]':
        return GetBundleItem(socket_type='IMAGE', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def geometry(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[GeometrySocket]':
        return GetBundleItem(socket_type='GEOMETRY', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def collection(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[CollectionSocket]':
        return GetBundleItem(socket_type='COLLECTION', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def material(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[MaterialSocket]':
        return GetBundleItem(socket_type='MATERIAL', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def bundle(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[BundleSocket]':
        return GetBundleItem(socket_type='BUNDLE', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def closure(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[ClosureSocket]':
        return GetBundleItem(socket_type='CLOSURE', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def font(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[FontSocket]':
        return GetBundleItem(socket_type='FONT', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def sound(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetBundleItem[SoundSocket]':
        return GetBundleItem(socket_type='SOUND', bundle=bundle, path=path, remove=remove, structure_type=structure_type)

    @classmethod
    def auto(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='AUTO', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @classmethod
    def dynamic(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='DYNAMIC', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @classmethod
    def field(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='FIELD', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @classmethod
    def grid(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='GRID', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @classmethod
    def list(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='LIST', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @classmethod
    def single(cls, bundle: InputBundle=None, path: InputString='', remove: InputBoolean=False, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetBundleItem[FloatSocket]':
        return GetBundleItem(structure_type='SINGLE', bundle=bundle, path=path, remove=remove, socket_type=socket_type)

    @property
    def socket_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.socket_type

    @socket_type.setter
    def socket_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'socket_type', value)

    @property
    def structure_type(self) -> Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']:
        return self.node.structure_type

    @structure_type.setter
    def structure_type(self, value: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']) -> None:
        set_property(self.node, 'structure_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GetListItem(BaseNode):
    _bl_idname = 'GeometryNodeListGetItem'

    def __init__(self, list: InputAny=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT', structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO'):
        super().__init__()
        key_args = {'List': list, 'Index': index}
        self.socket_type = socket_type
        self.structure_type = structure_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, list: InputFloatList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(socket_type='FLOAT', list=list, index=index, structure_type=structure_type)

    @classmethod
    def integer(cls, list: InputIntegerList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[IntegerSocket, IntegerSocketList]':
        return GetListItem(socket_type='INT', list=list, index=index, structure_type=structure_type)

    @classmethod
    def boolean(cls, list: InputBooleanList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[BooleanSocket, BooleanSocketList]':
        return GetListItem(socket_type='BOOLEAN', list=list, index=index, structure_type=structure_type)

    @classmethod
    def vector(cls, list: InputVectorList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[VectorSocket, VectorSocketList]':
        return GetListItem(socket_type='VECTOR', list=list, index=index, structure_type=structure_type)

    @classmethod
    def color(cls, list: InputColorList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[ColorSocket, ColorSocketList]':
        return GetListItem(socket_type='RGBA', list=list, index=index, structure_type=structure_type)

    @classmethod
    def rotation(cls, list: InputRotationList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[RotationSocket, RotationSocketList]':
        return GetListItem(socket_type='ROTATION', list=list, index=index, structure_type=structure_type)

    @classmethod
    def matrix(cls, list: InputMatrixList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[MatrixSocket, MatrixSocketList]':
        return GetListItem(socket_type='MATRIX', list=list, index=index, structure_type=structure_type)

    @classmethod
    def string(cls, list: InputStringList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[StringSocket, StringSocketList]':
        return GetListItem(socket_type='STRING', list=list, index=index, structure_type=structure_type)

    @classmethod
    def menu(cls, list: InputMenuList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[MenuSocket, MenuSocketList]':
        return GetListItem(socket_type='MENU', list=list, index=index, structure_type=structure_type)

    @classmethod
    def object(cls, list: InputObjectList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[ObjectSocket, ObjectSocketList]':
        return GetListItem(socket_type='OBJECT', list=list, index=index, structure_type=structure_type)

    @classmethod
    def image(cls, list: InputImageList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[ImageSocket, ImageSocketList]':
        return GetListItem(socket_type='IMAGE', list=list, index=index, structure_type=structure_type)

    @classmethod
    def geometry(cls, list: InputGeometryList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[GeometrySocket, GeometrySocketList]':
        return GetListItem(socket_type='GEOMETRY', list=list, index=index, structure_type=structure_type)

    @classmethod
    def collection(cls, list: InputCollectionList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[CollectionSocket, CollectionSocketList]':
        return GetListItem(socket_type='COLLECTION', list=list, index=index, structure_type=structure_type)

    @classmethod
    def material(cls, list: InputMaterialList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[MaterialSocket, MaterialSocketList]':
        return GetListItem(socket_type='MATERIAL', list=list, index=index, structure_type=structure_type)

    @classmethod
    def bundle(cls, list: InputBundleList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[BundleSocket, BundleSocketList]':
        return GetListItem(socket_type='BUNDLE', list=list, index=index, structure_type=structure_type)

    @classmethod
    def closure(cls, list: InputClosureList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[ClosureSocket, ClosureSocketList]':
        return GetListItem(socket_type='CLOSURE', list=list, index=index, structure_type=structure_type)

    @classmethod
    def font(cls, list: InputFontList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[FontSocket, FontSocketList]':
        return GetListItem(socket_type='FONT', list=list, index=index, structure_type=structure_type)

    @classmethod
    def sound(cls, list: InputSoundList=None, index: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'GetListItem[SoundSocket, SoundSocketList]':
        return GetListItem(socket_type='SOUND', list=list, index=index, structure_type=structure_type)

    @classmethod
    def auto(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='AUTO', list=list, index=index, socket_type=socket_type)

    @classmethod
    def dynamic(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='DYNAMIC', list=list, index=index, socket_type=socket_type)

    @classmethod
    def field(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='FIELD', list=list, index=index, socket_type=socket_type)

    @classmethod
    def grid(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='GRID', list=list, index=index, socket_type=socket_type)

    @classmethod
    def list(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='LIST', list=list, index=index, socket_type=socket_type)

    @classmethod
    def single(cls, list: InputFloatList=None, index: InputInteger=0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'GetListItem[FloatSocket, FloatSocketList]':
        return GetListItem(structure_type='SINGLE', list=list, index=index, socket_type=socket_type)

    @property
    def socket_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.socket_type

    @socket_type.setter
    def socket_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'socket_type', value)

    @property
    def structure_type(self) -> Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']:
        return self.node.structure_type

    @structure_type.setter
    def structure_type(self, value: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']) -> None:
        set_property(self.node, 'structure_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GetNestedBundlePaths(BaseNode):
    _bl_idname = 'NodeGetNestedBundlePaths'

    def __init__(self, bundle: InputBundle=None, mode: InputMenu | Literal['All', 'Bundle Type', 'Data Type']='All', pattern_mode: InputMenu | Literal['Exact', 'Wildcard']='Exact', bundle_type: InputString='', data_type: InputMenu | Literal['Float', 'Integer', 'Boolean', 'Vector', 'Color', 'Rotation', 'Matrix', 'String', 'Menu', 'Object', 'Image', 'Geometry', 'Collection', 'Material', 'Bundle', 'Closure', 'Font', 'Sound']='Float'):
        super().__init__()
        key_args = {'Bundle': bundle, 'Mode': mode, 'Pattern Mode': pattern_mode, 'Bundle Type': bundle_type, 'Data Type': data_type}
        self._establish_links(**key_args)

class HashValue(BaseNode):
    _bl_idname = 'FunctionNodeHashValue'

    def __init__(self, value: InputAny=0, seed: InputInteger=0, *, data_type: Literal['FLOAT', 'INT', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING']='INT'):
        super().__init__()
        key_args = {'Value': value, 'Seed': seed}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, value: InputFloat=0.0, seed: InputInteger=0) -> 'HashValue[FloatSocket]':
        return HashValue(data_type='FLOAT', value=value, seed=seed)

    @classmethod
    def integer(cls, value: InputInteger=0, seed: InputInteger=0) -> 'HashValue[IntegerSocket]':
        return HashValue(data_type='INT', value=value, seed=seed)

    @classmethod
    def vector(cls, value: InputVector=(0.0, 0.0, 0.0), seed: InputInteger=0) -> 'HashValue[VectorSocket]':
        return HashValue(data_type='VECTOR', value=value, seed=seed)

    @classmethod
    def color(cls, value: InputColor=(0.8, 0.8, 0.8, 1.0), seed: InputInteger=0) -> 'HashValue[ColorSocket]':
        return HashValue(data_type='RGBA', value=value, seed=seed)

    @classmethod
    def rotation(cls, value: InputRotation=(0.0, 0.0, 0.0), seed: InputInteger=0) -> 'HashValue[RotationSocket]':
        return HashValue(data_type='ROTATION', value=value, seed=seed)

    @classmethod
    def matrix(cls, value: InputMatrix=None, seed: InputInteger=0) -> 'HashValue[MatrixSocket]':
        return HashValue(data_type='MATRIX', value=value, seed=seed)

    @classmethod
    def string(cls, value: InputString='', seed: InputInteger=0) -> 'HashValue[StringSocket]':
        return HashValue(data_type='STRING', value=value, seed=seed)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ImplicitConversion(BaseNode):
    _bl_idname = 'NodeImplicitConversion'

    def __init__(self, value: InputAny=(0.0, 0.0, 0.0, 1.0), *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='RGBA'):
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
    def image(cls, value: InputImage=None) -> 'ImplicitConversion[ImageSocket]':
        return ImplicitConversion(data_type='IMAGE', value=value)

    @classmethod
    def geometry(cls, value: InputGeometry=None) -> 'ImplicitConversion[GeometrySocket]':
        return ImplicitConversion(data_type='GEOMETRY', value=value)

    @classmethod
    def collection(cls, value: InputCollection=None) -> 'ImplicitConversion[CollectionSocket]':
        return ImplicitConversion(data_type='COLLECTION', value=value)

    @classmethod
    def material(cls, value: InputMaterial=None) -> 'ImplicitConversion[MaterialSocket]':
        return ImplicitConversion(data_type='MATERIAL', value=value)

    @classmethod
    def bundle(cls, value: InputBundle=None) -> 'ImplicitConversion[BundleSocket]':
        return ImplicitConversion(data_type='BUNDLE', value=value)

    @classmethod
    def closure(cls, value: InputClosure=None) -> 'ImplicitConversion[ClosureSocket]':
        return ImplicitConversion(data_type='CLOSURE', value=value)

    @classmethod
    def font(cls, value: InputFont=None) -> 'ImplicitConversion[FontSocket]':
        return ImplicitConversion(data_type='FONT', value=value)

    @classmethod
    def sound(cls, value: InputSound=None) -> 'ImplicitConversion[SoundSocket]':
        return ImplicitConversion(data_type='SOUND', value=value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class IndexOfNearest(BaseNode):
    _bl_idname = 'GeometryNodeIndexOfNearest'

    def __init__(self, position: InputVector=None, group_id: InputInteger=None):
        super().__init__()
        key_args = {'Position': position, 'Group ID': group_id}
        self._establish_links(**key_args)

class IntegerMath(BaseNode):
    _bl_idname = 'FunctionNodeIntegerMath'

    def __init__(self, value: InputInteger=0, value_001: InputInteger=0, value_002: InputInteger=0, *, operation: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'ABSOLUTE', 'NEGATE', 'POWER', 'MINIMUM', 'MAXIMUM', 'SIGN', 'DIVIDE_ROUND', 'DIVIDE_FLOOR', 'DIVIDE_CEIL', 'FLOORED_MODULO', 'MODULO', 'GCD', 'LCM']='ADD'):
        super().__init__()
        key_args = {'Value': value, 'Value_001': value_001, 'Value_002': value_002}
        self.operation = operation
        self._establish_links(**key_args)

    @classmethod
    def add(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='ADD', value=value, value_001=value_001)

    @classmethod
    def subtract(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='SUBTRACT', value=value, value_001=value_001)

    @classmethod
    def multiply(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='MULTIPLY', value=value, value_001=value_001)

    @classmethod
    def divide(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='DIVIDE', value=value, value_001=value_001)

    @classmethod
    def multiply_add(cls, value: InputInteger=0, value_001: InputInteger=0, value_002: InputInteger=0) -> 'IntegerMath':
        return cls(operation='MULTIPLY_ADD', value=value, value_001=value_001, value_002=value_002)

    @classmethod
    def absolute(cls, value: InputInteger=0) -> 'IntegerMath':
        return cls(operation='ABSOLUTE', value=value)

    @classmethod
    def negate(cls, value: InputInteger=0) -> 'IntegerMath':
        return cls(operation='NEGATE', value=value)

    @classmethod
    def power(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='POWER', value=value, value_001=value_001)

    @classmethod
    def minimum(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='MINIMUM', value=value, value_001=value_001)

    @classmethod
    def maximum(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='MAXIMUM', value=value, value_001=value_001)

    @classmethod
    def sign(cls, value: InputInteger=0) -> 'IntegerMath':
        return cls(operation='SIGN', value=value)

    @classmethod
    def divide_round(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='DIVIDE_ROUND', value=value, value_001=value_001)

    @classmethod
    def divide_floor(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='DIVIDE_FLOOR', value=value, value_001=value_001)

    @classmethod
    def divide_ceiling(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='DIVIDE_CEIL', value=value, value_001=value_001)

    @classmethod
    def floored_modulo(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='FLOORED_MODULO', value=value, value_001=value_001)

    @classmethod
    def modulo(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='MODULO', value=value, value_001=value_001)

    @classmethod
    def greatest_common_divisor(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='GCD', value=value, value_001=value_001)

    @classmethod
    def least_common_multiple(cls, value: InputInteger=0, value_001: InputInteger=0) -> 'IntegerMath':
        return cls(operation='LCM', value=value, value_001=value_001)

    @property
    def operation(self) -> Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'ABSOLUTE', 'NEGATE', 'POWER', 'MINIMUM', 'MAXIMUM', 'SIGN', 'DIVIDE_ROUND', 'DIVIDE_FLOOR', 'DIVIDE_CEIL', 'FLOORED_MODULO', 'MODULO', 'GCD', 'LCM']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'ABSOLUTE', 'NEGATE', 'POWER', 'MINIMUM', 'MAXIMUM', 'SIGN', 'DIVIDE_ROUND', 'DIVIDE_FLOOR', 'DIVIDE_CEIL', 'FLOORED_MODULO', 'MODULO', 'GCD', 'LCM']) -> None:
        set_property(self.node, 'operation', value)

class InvertMatrix(BaseNode):
    _bl_idname = 'FunctionNodeInvertMatrix'

    def __init__(self, matrix: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix}
        self._establish_links(**key_args)

class InvertRotation(BaseNode):
    _bl_idname = 'FunctionNodeInvertRotation'

    def __init__(self, rotation: InputRotation=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Rotation': rotation}
        self._establish_links(**key_args)

class JoinBundle(BaseNode):
    _bl_idname = 'NodeJoinBundle'

    def __init__(self, bundle: InputBundle=None):
        super().__init__()
        key_args = {'Bundle': bundle}
        self._establish_links(**key_args)

class ListLength(BaseNode):
    _bl_idname = 'GeometryNodeListLength'

    def __init__(self, list: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT'):
        super().__init__()
        key_args = {'List': list}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, list: InputFloatList=None) -> 'ListLength[FloatSocketList]':
        return ListLength(data_type='FLOAT', list=list)

    @classmethod
    def integer(cls, list: InputIntegerList=None) -> 'ListLength[IntegerSocketList]':
        return ListLength(data_type='INT', list=list)

    @classmethod
    def boolean(cls, list: InputBooleanList=None) -> 'ListLength[BooleanSocketList]':
        return ListLength(data_type='BOOLEAN', list=list)

    @classmethod
    def vector(cls, list: InputVectorList=None) -> 'ListLength[VectorSocketList]':
        return ListLength(data_type='VECTOR', list=list)

    @classmethod
    def color(cls, list: InputColorList=None) -> 'ListLength[ColorSocketList]':
        return ListLength(data_type='RGBA', list=list)

    @classmethod
    def rotation(cls, list: InputRotationList=None) -> 'ListLength[RotationSocketList]':
        return ListLength(data_type='ROTATION', list=list)

    @classmethod
    def matrix(cls, list: InputMatrixList=None) -> 'ListLength[MatrixSocketList]':
        return ListLength(data_type='MATRIX', list=list)

    @classmethod
    def string(cls, list: InputStringList=None) -> 'ListLength[StringSocketList]':
        return ListLength(data_type='STRING', list=list)

    @classmethod
    def menu(cls, list: InputMenuList=None) -> 'ListLength[MenuSocketList]':
        return ListLength(data_type='MENU', list=list)

    @classmethod
    def object(cls, list: InputObjectList=None) -> 'ListLength[ObjectSocketList]':
        return ListLength(data_type='OBJECT', list=list)

    @classmethod
    def image(cls, list: InputImageList=None) -> 'ListLength[ImageSocketList]':
        return ListLength(data_type='IMAGE', list=list)

    @classmethod
    def geometry(cls, list: InputGeometryList=None) -> 'ListLength[GeometrySocketList]':
        return ListLength(data_type='GEOMETRY', list=list)

    @classmethod
    def collection(cls, list: InputCollectionList=None) -> 'ListLength[CollectionSocketList]':
        return ListLength(data_type='COLLECTION', list=list)

    @classmethod
    def material(cls, list: InputMaterialList=None) -> 'ListLength[MaterialSocketList]':
        return ListLength(data_type='MATERIAL', list=list)

    @classmethod
    def bundle(cls, list: InputBundleList=None) -> 'ListLength[BundleSocketList]':
        return ListLength(data_type='BUNDLE', list=list)

    @classmethod
    def closure(cls, list: InputClosureList=None) -> 'ListLength[ClosureSocketList]':
        return ListLength(data_type='CLOSURE', list=list)

    @classmethod
    def font(cls, list: InputFontList=None) -> 'ListLength[FontSocketList]':
        return ListLength(data_type='FONT', list=list)

    @classmethod
    def sound(cls, list: InputSoundList=None) -> 'ListLength[SoundSocketList]':
        return ListLength(data_type='SOUND', list=list)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class MapRange(BaseNode):
    _bl_idname = 'ShaderNodeMapRange'

    def __init__(self, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, steps: InputFloat=4.0, vector: InputVector=None, from_min_float3: InputVector=(0.0, 0.0, 0.0), from_max_float3: InputVector=(1.0, 1.0, 1.0), to_min_float3: InputVector=(0.0, 0.0, 0.0), to_max_float3: InputVector=(1.0, 1.0, 1.0), steps_float3: InputVector=(4.0, 4.0, 4.0), *, clamp: bool=False, interpolation_type: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']='LINEAR', data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Value': value, 'From Min': from_min, 'From Max': from_max, 'To Min': to_min, 'To Max': to_max, 'Steps': steps, 'Vector': vector, 'From_Min_FLOAT3': from_min_float3, 'From_Max_FLOAT3': from_max_float3, 'To_Min_FLOAT3': to_min_float3, 'To_Max_FLOAT3': to_max_float3, 'Steps_FLOAT3': steps_float3}
        self.clamp = clamp
        self.interpolation_type = interpolation_type
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def linear(cls, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, *, clamp: bool=False, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT') -> 'MapRange':
        return cls(interpolation_type='LINEAR', value=value, from_min=from_min, from_max=from_max, to_min=to_min, to_max=to_max, clamp=clamp, data_type=data_type)

    @classmethod
    def stepped_linear(cls, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, steps: InputFloat=4.0, *, clamp: bool=False, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT') -> 'MapRange':
        return cls(interpolation_type='STEPPED', value=value, from_min=from_min, from_max=from_max, to_min=to_min, to_max=to_max, steps=steps, clamp=clamp, data_type=data_type)

    @classmethod
    def smooth_step(cls, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, *, clamp: bool=False, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT') -> 'MapRange':
        return cls(interpolation_type='SMOOTHSTEP', value=value, from_min=from_min, from_max=from_max, to_min=to_min, to_max=to_max, clamp=clamp, data_type=data_type)

    @classmethod
    def smoother_step(cls, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, *, clamp: bool=False, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT') -> 'MapRange':
        return cls(interpolation_type='SMOOTHERSTEP', value=value, from_min=from_min, from_max=from_max, to_min=to_min, to_max=to_max, clamp=clamp, data_type=data_type)

    @classmethod
    def float(cls, value: InputFloat=1.0, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, *, clamp: bool=False, interpolation_type: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']='LINEAR') -> 'MapRange':
        return cls(data_type='FLOAT', value=value, from_min=from_min, from_max=from_max, to_min=to_min, to_max=to_max, clamp=clamp, interpolation_type=interpolation_type)

    @classmethod
    def vector(cls, vector: InputVector=None, from_min: InputVector=(0.0, 0.0, 0.0), from_max: InputVector=(1.0, 1.0, 1.0), to_min: InputVector=(0.0, 0.0, 0.0), to_max: InputVector=(1.0, 1.0, 1.0), *, clamp: bool=False, interpolation_type: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']='LINEAR') -> 'MapRange':
        return cls(data_type='FLOAT_VECTOR', vector=vector, from_min_float3=from_min, from_max_float3=from_max, to_min_float3=to_min, to_max_float3=to_max, clamp=clamp, interpolation_type=interpolation_type)

    @property
    def clamp(self) -> bool:
        return self.node.clamp

    @clamp.setter
    def clamp(self, value: bool) -> None:
        set_property(self.node, 'clamp', value)

    @property
    def interpolation_type(self) -> Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']:
        return self.node.interpolation_type

    @interpolation_type.setter
    def interpolation_type(self, value: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']) -> None:
        set_property(self.node, 'interpolation_type', value)

    @property
    def data_type(self) -> Literal['FLOAT', 'FLOAT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'FLOAT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

class MatchString(BaseNode):
    _bl_idname = 'FunctionNodeMatchString'

    def __init__(self, string: InputString='', operation: InputMenu | Literal['Starts With', 'Ends With', 'Contains']='Starts With', key: InputString=''):
        super().__init__()
        key_args = {'String': string, 'Operation': operation, 'Key': key}
        self._establish_links(**key_args)

class Math(BaseNode):
    _bl_idname = 'ShaderNodeMath'

    def __init__(self, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, operation: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE', 'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN', 'GREATER_THAN', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'FLOORED_MODULO', 'WRAP', 'SNAP', 'PINGPONG', 'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES']='ADD', use_clamp: bool=False):
        super().__init__()
        key_args = {'Value': value, 'Value_001': value_001, 'Value_002': value_002}
        self.operation = operation
        self.use_clamp = use_clamp
        self._establish_links(**key_args)

    @classmethod
    def add(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ADD', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def subtract(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SUBTRACT', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def multiply(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='MULTIPLY', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def divide(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='DIVIDE', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def multiply_add(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='MULTIPLY_ADD', value=value, value_001=value_001, value_002=value_002, use_clamp=use_clamp)

    @classmethod
    def power(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='POWER', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def logarithm(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='LOGARITHM', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def square_root(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SQRT', value=value, use_clamp=use_clamp)

    @classmethod
    def inverse_square_root(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='INVERSE_SQRT', value=value, use_clamp=use_clamp)

    @classmethod
    def absolute(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ABSOLUTE', value=value, use_clamp=use_clamp)

    @classmethod
    def exponent(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='EXPONENT', value=value, use_clamp=use_clamp)

    @classmethod
    def minimum(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='MINIMUM', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def maximum(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='MAXIMUM', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def less_than(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='LESS_THAN', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def greater_than(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='GREATER_THAN', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def sign(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SIGN', value=value, use_clamp=use_clamp)

    @classmethod
    def compare(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='COMPARE', value=value, value_001=value_001, value_002=value_002, use_clamp=use_clamp)

    @classmethod
    def smooth_minimum(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SMOOTH_MIN', value=value, value_001=value_001, value_002=value_002, use_clamp=use_clamp)

    @classmethod
    def smooth_maximum(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SMOOTH_MAX', value=value, value_001=value_001, value_002=value_002, use_clamp=use_clamp)

    @classmethod
    def round(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ROUND', value=value, use_clamp=use_clamp)

    @classmethod
    def floor(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='FLOOR', value=value, use_clamp=use_clamp)

    @classmethod
    def ceil(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='CEIL', value=value, use_clamp=use_clamp)

    @classmethod
    def truncate(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='TRUNC', value=value, use_clamp=use_clamp)

    @classmethod
    def fraction(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='FRACT', value=value, use_clamp=use_clamp)

    @classmethod
    def truncated_modulo(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='MODULO', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def floored_modulo(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='FLOORED_MODULO', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def wrap(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, value_002: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='WRAP', value=value, value_001=value_001, value_002=value_002, use_clamp=use_clamp)

    @classmethod
    def snap(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SNAP', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def ping_pong(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='PINGPONG', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def sine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SINE', value=value, use_clamp=use_clamp)

    @classmethod
    def cosine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='COSINE', value=value, use_clamp=use_clamp)

    @classmethod
    def tangent(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='TANGENT', value=value, use_clamp=use_clamp)

    @classmethod
    def arcsine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ARCSINE', value=value, use_clamp=use_clamp)

    @classmethod
    def arccosine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ARCCOSINE', value=value, use_clamp=use_clamp)

    @classmethod
    def arctangent(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ARCTANGENT', value=value, use_clamp=use_clamp)

    @classmethod
    def arctan2(cls, value: InputFloat=0.5, value_001: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='ARCTAN2', value=value, value_001=value_001, use_clamp=use_clamp)

    @classmethod
    def hyperbolic_sine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='SINH', value=value, use_clamp=use_clamp)

    @classmethod
    def hyperbolic_cosine(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='COSH', value=value, use_clamp=use_clamp)

    @classmethod
    def hyperbolic_tangent(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='TANH', value=value, use_clamp=use_clamp)

    @classmethod
    def to_radians(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='RADIANS', value=value, use_clamp=use_clamp)

    @classmethod
    def to_degrees(cls, value: InputFloat=0.5, *, use_clamp: bool=False) -> 'Math':
        return cls(operation='DEGREES', value=value, use_clamp=use_clamp)

    @property
    def operation(self) -> Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE', 'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN', 'GREATER_THAN', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'FLOORED_MODULO', 'WRAP', 'SNAP', 'PINGPONG', 'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE', 'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN', 'GREATER_THAN', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'FLOORED_MODULO', 'WRAP', 'SNAP', 'PINGPONG', 'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES']) -> None:
        set_property(self.node, 'operation', value)

    @property
    def use_clamp(self) -> bool:
        return self.node.use_clamp

    @use_clamp.setter
    def use_clamp(self, value: bool) -> None:
        set_property(self.node, 'use_clamp', value)

class MatrixDeterminant(BaseNode):
    _bl_idname = 'FunctionNodeMatrixDeterminant'

    def __init__(self, matrix: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix}
        self._establish_links(**key_args)

class MatrixSVD(BaseNode):
    _bl_idname = 'FunctionNodeMatrixSVD'

    def __init__(self, matrix: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix}
        self._establish_links(**key_args)

class Mix(BaseNode):
    _bl_idname = 'ShaderNodeMix'

    def __init__(self, factor_float: InputFloat=1.0, factor_vector: InputVector=(0.5, 0.5, 0.5), a_float: InputFloat=0.0, b_float: InputFloat=0.0, a_vector: InputVector=(0.0, 0.0, 0.0), b_vector: InputVector=(0.0, 0.0, 0.0), a_color: InputColor=(0.5, 0.5, 0.5, 1.0), b_color: InputColor=(0.5, 0.5, 0.5, 1.0), a_rotation: InputRotation=(0.0, 0.0, 0.0), b_rotation: InputRotation=(0.0, 0.0, 0.0), *, data_type: Literal['FLOAT', 'VECTOR', 'RGBA', 'ROTATION']='FLOAT', factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False):
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

    @classmethod
    def rotation(cls, factor: InputFloat=1.0, a: InputRotation=(0.0, 0.0, 0.0), b: InputRotation=(0.0, 0.0, 0.0), *, factor_mode: Literal['UNIFORM', 'NON_UNIFORM']='UNIFORM', blend_type: Literal['MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT', 'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE']='MIX', clamp_factor: bool=False, clamp_result: bool=False) -> 'Mix':
        return cls(data_type='ROTATION', factor_float=factor, a_rotation=a, b_rotation=b, factor_mode=factor_mode, blend_type=blend_type, clamp_factor=clamp_factor, clamp_result=clamp_result)

    @property
    def data_type(self) -> Literal['FLOAT', 'VECTOR', 'RGBA', 'ROTATION']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'VECTOR', 'RGBA', 'ROTATION']) -> None:
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

class MultiplyMatrices(BaseNode):
    _bl_idname = 'FunctionNodeMatrixMultiply'

    def __init__(self, matrix: InputMatrix=None, matrix_001: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix, 'Matrix_001': matrix_001}
        self._establish_links(**key_args)

class PackUVIslands(BaseNode):
    _bl_idname = 'GeometryNodeUVPackIslands'

    def __init__(self, uv: InputVector=None, selection: InputBoolean=None, margin: InputFloat=0.001, rotate: InputBoolean=True, method: InputMenu | Literal['Bounding Box', 'Convex Hull', 'Exact Shape']='Bounding Box', bottom_left: InputVector=(0.0, 0.0), top_right: InputVector=(1.0, 1.0)):
        super().__init__()
        key_args = {'UV': uv, 'Selection': selection, 'Margin': margin, 'Rotate': rotate, 'Method': method, 'Bottom Left': bottom_left, 'Top Right': top_right}
        self._establish_links(**key_args)

class ProjectPoint(BaseNode):
    _bl_idname = 'FunctionNodeProjectPoint'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0), transform: InputMatrix=None):
        super().__init__()
        key_args = {'Vector': vector, 'Transform': transform}
        self._establish_links(**key_args)

class QuaternionToRotation(BaseNode):
    _bl_idname = 'FunctionNodeQuaternionToRotation'

    def __init__(self, w: InputFloat=1.0, x: InputFloat=0.0, y: InputFloat=0.0, z: InputFloat=0.0):
        super().__init__()
        key_args = {'W': w, 'X': x, 'Y': y, 'Z': z}
        self._establish_links(**key_args)

class RandomValue(BaseNode):
    _bl_idname = 'FunctionNodeRandomValue'

    def __init__(self, min: InputAny=0.0, max: InputAny=1.0, id: InputInteger=None, seed: InputInteger=0, probability: InputFloat=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR']='FLOAT'):
        super().__init__()
        self.data_type = data_type
        _all_args = {'Min': min, 'Max': max, 'ID': id, 'Seed': seed, 'Probability': probability}
        assert self.node.inputs is not None
        _socket_ids = {s.identifier for s in self.node.inputs}
        key_args = {k: v for k, v in _all_args.items() if k in _socket_ids}
        self._establish_links(**key_args)

    @classmethod
    def float(cls, min: InputFloat=0.0, max: InputFloat=1.0, id: InputInteger=None, seed: InputInteger=0) -> 'RandomValue[FloatSocket]':
        return RandomValue(data_type='FLOAT', min=min, max=max, id=id, seed=seed)

    @classmethod
    def integer(cls, min: InputInteger=0, max: InputInteger=100, id: InputInteger=None, seed: InputInteger=0) -> 'RandomValue[IntegerSocket]':
        return RandomValue(data_type='INT', min=min, max=max, id=id, seed=seed)

    @classmethod
    def boolean(cls, probability: InputFloat=0.5, id: InputInteger=None, seed: InputInteger=0) -> 'RandomValue[BooleanSocket]':
        return RandomValue(data_type='BOOLEAN', probability=probability, id=id, seed=seed)

    @classmethod
    def vector(cls, min: InputVector=(0.0, 0.0, 0.0), max: InputVector=(1.0, 1.0, 1.0), id: InputInteger=None, seed: InputInteger=0) -> 'RandomValue[VectorSocket]':
        return RandomValue(data_type='FLOAT_VECTOR', min=min, max=max, id=id, seed=seed)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ReplaceString(BaseNode):
    _bl_idname = 'FunctionNodeReplaceString'

    def __init__(self, string: InputString='', find: InputString='', replace: InputString=''):
        super().__init__()
        key_args = {'String': string, 'Find': find, 'Replace': replace}
        self._establish_links(**key_args)

class ReverseString(BaseNode):
    _bl_idname = 'FunctionNodeReverseString'

    def __init__(self, string: InputString=''):
        super().__init__()
        key_args = {'String': string}
        self._establish_links(**key_args)

class RotateEuler(BaseNode):
    _bl_idname = 'FunctionNodeRotateEuler'

    def __init__(self, rotation: InputVector=None, rotate_by: InputVector=(0.0, 0.0, 0.0), axis: InputVector=None, angle: InputFloat=None, *, rotation_type: Literal['AXIS_ANGLE', 'EULER']='EULER', space: Literal['OBJECT', 'LOCAL']='OBJECT'):
        super().__init__()
        self.rotation_type = rotation_type
        self.space = space
        _all_args = {'Rotation': rotation, 'Rotate By': rotate_by, 'Axis': axis, 'Angle': angle}
        assert self.node.inputs is not None
        _socket_ids = {s.identifier for s in self.node.inputs}
        key_args = {k: v for k, v in _all_args.items() if k in _socket_ids}
        self._establish_links(**key_args)

    @classmethod
    def axis_angle(cls, rotation: InputVector=None, axis: InputVector=(0.0, 0.0, 1.0), angle: InputFloat=0.0, *, space: Literal['OBJECT', 'LOCAL']='OBJECT') -> 'RotateEuler':
        return cls(rotation_type='AXIS_ANGLE', rotation=rotation, axis=axis, angle=angle, space=space)

    @classmethod
    def euler(cls, rotation: InputVector=None, rotate_by: InputVector=(0.0, 0.0, 0.0), *, space: Literal['OBJECT', 'LOCAL']='OBJECT') -> 'RotateEuler':
        return cls(rotation_type='EULER', rotation=rotation, rotate_by=rotate_by, space=space)

    @property
    def rotation_type(self) -> Literal['AXIS_ANGLE', 'EULER']:
        return self.node.rotation_type

    @rotation_type.setter
    def rotation_type(self, value: Literal['AXIS_ANGLE', 'EULER']) -> None:
        set_property(self.node, 'rotation_type', value)

    @property
    def space(self) -> Literal['OBJECT', 'LOCAL']:
        return self.node.space

    @space.setter
    def space(self, value: Literal['OBJECT', 'LOCAL']) -> None:
        set_property(self.node, 'space', value)

class RotateRotation(BaseNode):
    _bl_idname = 'FunctionNodeRotateRotation'

    def __init__(self, rotation: InputRotation=(0.0, 0.0, 0.0), rotate_by: InputRotation=(0.0, 0.0, 0.0), *, rotation_space: Literal['GLOBAL', 'LOCAL']='GLOBAL'):
        super().__init__()
        key_args = {'Rotation': rotation, 'Rotate By': rotate_by}
        self.rotation_space = rotation_space
        self._establish_links(**key_args)

    @property
    def rotation_space(self) -> Literal['GLOBAL', 'LOCAL']:
        return self.node.rotation_space

    @rotation_space.setter
    def rotation_space(self, value: Literal['GLOBAL', 'LOCAL']) -> None:
        set_property(self.node, 'rotation_space', value)

class RotateVector(BaseNode):
    _bl_idname = 'FunctionNodeRotateVector'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0), rotation: InputRotation=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Vector': vector, 'Rotation': rotation}
        self._establish_links(**key_args)

class RotationToAxisAngle(BaseNode):
    _bl_idname = 'FunctionNodeRotationToAxisAngle'

    def __init__(self, rotation: InputRotation=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Rotation': rotation}
        self._establish_links(**key_args)

class RotationToEuler(BaseNode):
    _bl_idname = 'FunctionNodeRotationToEuler'

    def __init__(self, rotation: InputRotation=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Rotation': rotation}
        self._establish_links(**key_args)

class RotationToQuaternion(BaseNode):
    _bl_idname = 'FunctionNodeRotationToQuaternion'

    def __init__(self, rotation: InputRotation=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Rotation': rotation}
        self._establish_links(**key_args)

class SampleSoundFrequencies(BaseNode):
    _bl_idname = 'GeometryNodeSampleSoundFrequencies'

    def __init__(self, sound: InputSound=None, time: InputFloat=0.0, all_channels: InputBoolean=True, channel: InputInteger=0, low: InputFloat=0.0, high: InputFloat=10000.0, fft_size: InputMenu | Literal['128', '256', '512', '1024', '2048', '4096', '8192', '16384', '32768']='4096', window_function: InputMenu | Literal['Hann', 'Hamming', 'Blackman', 'Rectangular']='Hann'):
        super().__init__()
        key_args = {'Sound': sound, 'Time': time, 'All Channels': all_channels, 'Channel': channel, 'Low': low, 'High': high, 'FFT Size': fft_size, 'Window Function': window_function}
        self._establish_links(**key_args)

class SeparateBundle(_SeparateBundleMixin, BaseNode):
    _bl_idname = 'NodeSeparateBundle'

    @property
    def define_signature(self) -> bool:
        return self.node.define_signature

    @define_signature.setter
    def define_signature(self, value: bool) -> None:
        set_property(self.node, 'define_signature', value)

class SeparateColor(BaseNode):
    _bl_idname = 'FunctionNodeSeparateColor'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), *, mode: Literal['RGB', 'HSV', 'HSL']='RGB'):
        super().__init__()
        key_args = {'Color': color}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def rgb(cls, color: InputColor=(1.0, 1.0, 1.0, 1.0)) -> 'SeparateColor':
        return cls(mode='RGB', color=color)

    @classmethod
    def hsv(cls, color: InputColor=(1.0, 1.0, 1.0, 1.0)) -> 'SeparateColor':
        return cls(mode='HSV', color=color)

    @classmethod
    def hsl(cls, color: InputColor=(1.0, 1.0, 1.0, 1.0)) -> 'SeparateColor':
        return cls(mode='HSL', color=color)

    @property
    def mode(self) -> Literal['RGB', 'HSV', 'HSL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RGB', 'HSV', 'HSL']) -> None:
        set_property(self.node, 'mode', value)

class SeparateMatrix(BaseNode):
    _bl_idname = 'FunctionNodeSeparateMatrix'

    def __init__(self, matrix: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix}
        self._establish_links(**key_args)

class SeparateTransform(BaseNode):
    _bl_idname = 'FunctionNodeSeparateTransform'

    def __init__(self, transform: InputMatrix=None):
        super().__init__()
        key_args = {'Transform': transform}
        self._establish_links(**key_args)

class SeparateXYZ(BaseNode):
    _bl_idname = 'ShaderNodeSeparateXYZ'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Vector': vector}
        self._establish_links(**key_args)

class SetStringCase(BaseNode):
    _bl_idname = 'FunctionNodeSetStringCase'

    def __init__(self, string: InputString='', case: InputMenu | Literal['Uppercase', 'Lowercase']='Uppercase'):
        super().__init__()
        key_args = {'String': string, 'Case': case}
        self._establish_links(**key_args)

class SliceString(BaseNode):
    _bl_idname = 'FunctionNodeSliceString'

    def __init__(self, string: InputString='', position: InputInteger=0, length: InputInteger=10):
        super().__init__()
        key_args = {'String': string, 'Position': position, 'Length': length}
        self._establish_links(**key_args)

class SortList(BaseNode):
    _bl_idname = 'GeometryNodeSortList'

    def __init__(self, list: InputAny=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT'):
        super().__init__()
        key_args = {'List': list, 'Selection': selection, 'Group ID': group_id, 'Sort Weight': sort_weight}
        self.socket_type = socket_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, list: InputFloatList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[FloatSocketList]':
        return SortList(socket_type='FLOAT', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def integer(cls, list: InputIntegerList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[IntegerSocketList]':
        return SortList(socket_type='INT', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def boolean(cls, list: InputBooleanList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[BooleanSocketList]':
        return SortList(socket_type='BOOLEAN', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def vector(cls, list: InputVectorList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[VectorSocketList]':
        return SortList(socket_type='VECTOR', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def color(cls, list: InputColorList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[ColorSocketList]':
        return SortList(socket_type='RGBA', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def rotation(cls, list: InputRotationList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[RotationSocketList]':
        return SortList(socket_type='ROTATION', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def matrix(cls, list: InputMatrixList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[MatrixSocketList]':
        return SortList(socket_type='MATRIX', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def string(cls, list: InputStringList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[StringSocketList]':
        return SortList(socket_type='STRING', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def menu(cls, list: InputMenuList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[MenuSocketList]':
        return SortList(socket_type='MENU', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def object(cls, list: InputObjectList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[ObjectSocketList]':
        return SortList(socket_type='OBJECT', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def image(cls, list: InputImageList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[ImageSocketList]':
        return SortList(socket_type='IMAGE', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def geometry(cls, list: InputGeometryList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[GeometrySocketList]':
        return SortList(socket_type='GEOMETRY', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def collection(cls, list: InputCollectionList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[CollectionSocketList]':
        return SortList(socket_type='COLLECTION', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def material(cls, list: InputMaterialList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[MaterialSocketList]':
        return SortList(socket_type='MATERIAL', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def bundle(cls, list: InputBundleList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[BundleSocketList]':
        return SortList(socket_type='BUNDLE', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def closure(cls, list: InputClosureList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[ClosureSocketList]':
        return SortList(socket_type='CLOSURE', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def font(cls, list: InputFontList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[FontSocketList]':
        return SortList(socket_type='FONT', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def sound(cls, list: InputSoundList=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortList[SoundSocketList]':
        return SortList(socket_type='SOUND', list=list, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @property
    def socket_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.socket_type

    @socket_type.setter
    def socket_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'socket_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SplitString(BaseNode):
    _bl_idname = 'FunctionNodeSplitString'

    def __init__(self, string: InputString='', separator: InputString=''):
        super().__init__()
        key_args = {'String': string, 'Separator': separator}
        self._establish_links(**key_args)

class StoreBundleItem(BaseNode):
    _bl_idname = 'NodeStoreBundleItem'

    def __init__(self, bundle: InputBundle=None, path: InputString='', item: InputAny=0.0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT', structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO'):
        super().__init__()
        key_args = {'Bundle': bundle, 'Path': path, 'Item': item}
        self.socket_type = socket_type
        self.structure_type = structure_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, bundle: InputBundle=None, path: InputString='', item: InputFloat=0.0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(socket_type='FLOAT', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def integer(cls, bundle: InputBundle=None, path: InputString='', item: InputInteger=0, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[IntegerSocket]':
        return StoreBundleItem(socket_type='INT', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def boolean(cls, bundle: InputBundle=None, path: InputString='', item: InputBoolean=False, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[BooleanSocket]':
        return StoreBundleItem(socket_type='BOOLEAN', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def vector(cls, bundle: InputBundle=None, path: InputString='', item: InputVector=(0.0, 0.0, 0.0), *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[VectorSocket]':
        return StoreBundleItem(socket_type='VECTOR', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def color(cls, bundle: InputBundle=None, path: InputString='', item: InputColor=(0.8, 0.8, 0.8, 1.0), *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[ColorSocket]':
        return StoreBundleItem(socket_type='RGBA', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def rotation(cls, bundle: InputBundle=None, path: InputString='', item: InputRotation=(0.0, 0.0, 0.0), *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[RotationSocket]':
        return StoreBundleItem(socket_type='ROTATION', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def matrix(cls, bundle: InputBundle=None, path: InputString='', item: InputMatrix=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[MatrixSocket]':
        return StoreBundleItem(socket_type='MATRIX', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def string(cls, bundle: InputBundle=None, path: InputString='', item: InputString='', *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[StringSocket]':
        return StoreBundleItem(socket_type='STRING', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def menu(cls, bundle: InputBundle=None, path: InputString='', item: InputMenu=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[MenuSocket]':
        return StoreBundleItem(socket_type='MENU', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def object(cls, bundle: InputBundle=None, path: InputString='', item: InputObject=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[ObjectSocket]':
        return StoreBundleItem(socket_type='OBJECT', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def image(cls, bundle: InputBundle=None, path: InputString='', item: InputImage=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[ImageSocket]':
        return StoreBundleItem(socket_type='IMAGE', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def geometry(cls, bundle: InputBundle=None, path: InputString='', item: InputGeometry=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[GeometrySocket]':
        return StoreBundleItem(socket_type='GEOMETRY', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def collection(cls, bundle: InputBundle=None, path: InputString='', item: InputCollection=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[CollectionSocket]':
        return StoreBundleItem(socket_type='COLLECTION', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def material(cls, bundle: InputBundle=None, path: InputString='', item: InputMaterial=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[MaterialSocket]':
        return StoreBundleItem(socket_type='MATERIAL', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def bundle(cls, bundle: InputBundle=None, path: InputString='', item: InputBundle=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[BundleSocket]':
        return StoreBundleItem(socket_type='BUNDLE', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def closure(cls, bundle: InputBundle=None, path: InputString='', item: InputClosure=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[ClosureSocket]':
        return StoreBundleItem(socket_type='CLOSURE', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def font(cls, bundle: InputBundle=None, path: InputString='', item: InputFont=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[FontSocket]':
        return StoreBundleItem(socket_type='FONT', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def sound(cls, bundle: InputBundle=None, path: InputString='', item: InputSound=None, *, structure_type: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']='AUTO') -> 'StoreBundleItem[SoundSocket]':
        return StoreBundleItem(socket_type='SOUND', bundle=bundle, path=path, item=item, structure_type=structure_type)

    @classmethod
    def auto(cls, bundle: InputBundle=None, path: InputString='', item: InputFloat=0.0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='AUTO', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @classmethod
    def dynamic(cls, bundle: InputBundle=None, path: InputString='', item: InputFloat=0.0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='DYNAMIC', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @classmethod
    def field(cls, bundle: InputBundle=None, path: InputString='', item: InputFloat=0.0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='FIELD', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @classmethod
    def grid(cls, bundle: InputBundle=None, path: InputString='', item: InputFloatGrid=None, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='GRID', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @classmethod
    def list(cls, bundle: InputBundle=None, path: InputString='', item: InputFloatList=None, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='LIST', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @classmethod
    def single(cls, bundle: InputBundle=None, path: InputString='', item: InputFloat=0.0, *, socket_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT') -> 'StoreBundleItem[FloatSocket]':
        return StoreBundleItem(structure_type='SINGLE', bundle=bundle, path=path, item=item, socket_type=socket_type)

    @property
    def socket_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.socket_type

    @socket_type.setter
    def socket_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'socket_type', value)

    @property
    def structure_type(self) -> Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']:
        return self.node.structure_type

    @structure_type.setter
    def structure_type(self, value: Literal['AUTO', 'DYNAMIC', 'FIELD', 'GRID', 'LIST', 'SINGLE']) -> None:
        set_property(self.node, 'structure_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class StringLength(BaseNode):
    _bl_idname = 'FunctionNodeStringLength'

    def __init__(self, string: InputString=''):
        super().__init__()
        key_args = {'String': string}
        self._establish_links(**key_args)

class StringToValue(BaseNode):
    _bl_idname = 'FunctionNodeStringToValue'

    def __init__(self, string: InputString='', base: InputInteger=10, *, data_type: Literal['FLOAT', 'INT']='FLOAT'):
        super().__init__()
        key_args = {'String': string, 'Base': base}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, string: InputString='') -> 'StringToValue[FloatSocket]':
        return StringToValue(data_type='FLOAT', string=string)

    @classmethod
    def integer(cls, string: InputString='', base: InputInteger=10) -> 'StringToValue[IntegerSocket]':
        return StringToValue(data_type='INT', string=string, base=base)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class Switch(BaseNode):
    _bl_idname = 'GeometryNodeSwitch'

    def __init__(self, switch: InputBoolean=False, false: InputAny=0.0, true: InputAny=0.0, *, input_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']='FLOAT'):
        super().__init__()
        key_args = {'Switch': switch, 'False': false, 'True': true}
        self.input_type = input_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, switch: InputBoolean=False, false: InputFloat=0.0, true: InputFloat=0.0) -> 'Switch[FloatSocket]':
        return Switch(input_type='FLOAT', switch=switch, false=false, true=true)

    @classmethod
    def integer(cls, switch: InputBoolean=False, false: InputInteger=0, true: InputInteger=0) -> 'Switch[IntegerSocket]':
        return Switch(input_type='INT', switch=switch, false=false, true=true)

    @classmethod
    def boolean(cls, switch: InputBoolean=False, false: InputBoolean=False, true: InputBoolean=False) -> 'Switch[BooleanSocket]':
        return Switch(input_type='BOOLEAN', switch=switch, false=false, true=true)

    @classmethod
    def vector(cls, switch: InputBoolean=False, false: InputVector=(0.0, 0.0, 0.0), true: InputVector=(0.0, 0.0, 0.0)) -> 'Switch[VectorSocket]':
        return Switch(input_type='VECTOR', switch=switch, false=false, true=true)

    @classmethod
    def color(cls, switch: InputBoolean=False, false: InputColor=(0.8, 0.8, 0.8, 1.0), true: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'Switch[ColorSocket]':
        return Switch(input_type='RGBA', switch=switch, false=false, true=true)

    @classmethod
    def rotation(cls, switch: InputBoolean=False, false: InputRotation=(0.0, 0.0, 0.0), true: InputRotation=(0.0, 0.0, 0.0)) -> 'Switch[RotationSocket]':
        return Switch(input_type='ROTATION', switch=switch, false=false, true=true)

    @classmethod
    def matrix(cls, switch: InputBoolean=False, false: InputMatrix=None, true: InputMatrix=None) -> 'Switch[MatrixSocket]':
        return Switch(input_type='MATRIX', switch=switch, false=false, true=true)

    @classmethod
    def string(cls, switch: InputBoolean=False, false: InputString='', true: InputString='') -> 'Switch[StringSocket]':
        return Switch(input_type='STRING', switch=switch, false=false, true=true)

    @classmethod
    def menu(cls, switch: InputBoolean=False, false: InputMenu=None, true: InputMenu=None) -> 'Switch[MenuSocket]':
        return Switch(input_type='MENU', switch=switch, false=false, true=true)

    @classmethod
    def object(cls, switch: InputBoolean=False, false: InputObject=None, true: InputObject=None) -> 'Switch[ObjectSocket]':
        return Switch(input_type='OBJECT', switch=switch, false=false, true=true)

    @classmethod
    def image(cls, switch: InputBoolean=False, false: InputImage=None, true: InputImage=None) -> 'Switch[ImageSocket]':
        return Switch(input_type='IMAGE', switch=switch, false=false, true=true)

    @classmethod
    def geometry(cls, switch: InputBoolean=False, false: InputGeometry=None, true: InputGeometry=None) -> 'Switch[GeometrySocket]':
        return Switch(input_type='GEOMETRY', switch=switch, false=false, true=true)

    @classmethod
    def collection(cls, switch: InputBoolean=False, false: InputCollection=None, true: InputCollection=None) -> 'Switch[CollectionSocket]':
        return Switch(input_type='COLLECTION', switch=switch, false=false, true=true)

    @classmethod
    def material(cls, switch: InputBoolean=False, false: InputMaterial=None, true: InputMaterial=None) -> 'Switch[MaterialSocket]':
        return Switch(input_type='MATERIAL', switch=switch, false=false, true=true)

    @classmethod
    def bundle(cls, switch: InputBoolean=False, false: InputBundle=None, true: InputBundle=None) -> 'Switch[BundleSocket]':
        return Switch(input_type='BUNDLE', switch=switch, false=false, true=true)

    @classmethod
    def closure(cls, switch: InputBoolean=False, false: InputClosure=None, true: InputClosure=None) -> 'Switch[ClosureSocket]':
        return Switch(input_type='CLOSURE', switch=switch, false=false, true=true)

    @classmethod
    def font(cls, switch: InputBoolean=False, false: InputFont=None, true: InputFont=None) -> 'Switch[FontSocket]':
        return Switch(input_type='FONT', switch=switch, false=false, true=true)

    @classmethod
    def sound(cls, switch: InputBoolean=False, false: InputSound=None, true: InputSound=None) -> 'Switch[SoundSocket]':
        return Switch(input_type='SOUND', switch=switch, false=false, true=true)

    @property
    def input_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']:
        return self.node.input_type

    @input_type.setter
    def input_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'IMAGE', 'GEOMETRY', 'COLLECTION', 'MATERIAL', 'BUNDLE', 'CLOSURE', 'FONT', 'SOUND']) -> None:
        set_property(self.node, 'input_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class TagFilter(BaseNode):
    _bl_idname = 'GeometryNodeTagFilter'

    def __init__(self, tag_filter: InputString='', tags: InputStringList=None):
        super().__init__()
        key_args = {'Tag Filter': tag_filter, 'Tags': tags}
        self._establish_links(**key_args)

class TransformDirection(BaseNode):
    _bl_idname = 'FunctionNodeTransformDirection'

    def __init__(self, direction: InputVector=(0.0, 0.0, 0.0), transform: InputMatrix=None):
        super().__init__()
        key_args = {'Direction': direction, 'Transform': transform}
        self._establish_links(**key_args)

class TransformPoint(BaseNode):
    _bl_idname = 'FunctionNodeTransformPoint'

    def __init__(self, vector: InputVector=(0.0, 0.0, 0.0), transform: InputMatrix=None):
        super().__init__()
        key_args = {'Vector': vector, 'Transform': transform}
        self._establish_links(**key_args)

class TransposeMatrix(BaseNode):
    _bl_idname = 'FunctionNodeTransposeMatrix'

    def __init__(self, matrix: InputMatrix=None):
        super().__init__()
        key_args = {'Matrix': matrix}
        self._establish_links(**key_args)

class TrimString(BaseNode):
    _bl_idname = 'FunctionNodeTrimString'

    def __init__(self, string: InputString='', characters: InputString='', whitespace: InputBoolean=True, start: InputBoolean=True, end: InputBoolean=True):
        super().__init__()
        key_args = {'String': string, 'Characters': characters, 'Whitespace': whitespace, 'Start': start, 'End': end}
        self._establish_links(**key_args)

class UVUnwrap(BaseNode):
    _bl_idname = 'GeometryNodeUVUnwrap'

    def __init__(self, selection: InputBoolean=None, seam: InputBoolean=None, margin: InputFloat=0.001, fill_holes: InputBoolean=True, method: InputMenu | Literal['Angle Based', 'Conformal', 'Minimum Stretch']='Angle Based', iterations: InputInteger=10, no_flip: InputBoolean=False):
        super().__init__()
        key_args = {'Selection': selection, 'Seam': seam, 'Margin': margin, 'Fill Holes': fill_holes, 'Method': method, 'Iterations': iterations, 'No Flip': no_flip}
        self._establish_links(**key_args)

class ValueToString(BaseNode):
    _bl_idname = 'FunctionNodeValueToString'

    def __init__(self, value: InputAny=0.0, decimals: InputInteger=0, base: InputInteger=10, padding: InputInteger=0, *, data_type: Literal['FLOAT', 'INT']='FLOAT'):
        super().__init__()
        key_args = {'Value': value, 'Decimals': decimals, 'Base': base, 'Padding': padding}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, value: InputFloat=0.0, decimals: InputInteger=0) -> 'ValueToString[FloatSocket]':
        return ValueToString(data_type='FLOAT', value=value, decimals=decimals)

    @classmethod
    def integer(cls, value: InputInteger=0, base: InputInteger=10, padding: InputInteger=0) -> 'ValueToString[IntegerSocket]':
        return ValueToString(data_type='INT', value=value, base=base, padding=padding)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
