# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
T = typing.TypeVar('T')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, GeometrySocket, IntegerSocket, MenuSocket, StringSocket, StringSocketList, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputColor, InputFloat, InputGeometry, InputInteger, InputMenu, InputString, InputVector

class BlurAttribute(BaseNode):
    _bl_idname = 'GeometryNodeBlurAttribute'

    def __init__(self, value: InputAny=None, iterations: InputInteger=1, weight: InputFloat=1.0, *, data_type: Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR']='FLOAT'):
        super().__init__()
        key_args = {'Value': value, 'Iterations': iterations, 'Weight': weight}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, value: InputFloat=None, iterations: InputInteger=1, weight: InputFloat=1.0) -> 'BlurAttribute[FloatSocket]':
        return BlurAttribute(data_type='FLOAT', value=value, iterations=iterations, weight=weight)

    @classmethod
    def integer(cls, value: InputInteger=None, iterations: InputInteger=1, weight: InputFloat=1.0) -> 'BlurAttribute[IntegerSocket]':
        return BlurAttribute(data_type='INT', value=value, iterations=iterations, weight=weight)

    @classmethod
    def vector(cls, value: InputVector=None, iterations: InputInteger=1, weight: InputFloat=1.0) -> 'BlurAttribute[VectorSocket]':
        return BlurAttribute(data_type='FLOAT_VECTOR', value=value, iterations=iterations, weight=weight)

    @classmethod
    def color(cls, value: InputColor=None, iterations: InputInteger=1, weight: InputFloat=1.0) -> 'BlurAttribute[ColorSocket]':
        return BlurAttribute(data_type='FLOAT_COLOR', value=value, iterations=iterations, weight=weight)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'FLOAT_VECTOR', 'FLOAT_COLOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class DomainSize(BaseNode):
    _bl_idname = 'GeometryNodeAttributeDomainSize'

    def __init__(self, geometry: InputGeometry=None, *, component: Literal['MESH', 'POINTCLOUD', 'CURVE', 'INSTANCES', 'GREASEPENCIL']='MESH'):
        super().__init__()
        key_args = {'Geometry': geometry}
        self.component = component
        self._establish_links(**key_args)

    @property
    def component(self) -> Literal['MESH', 'POINTCLOUD', 'CURVE', 'INSTANCES', 'GREASEPENCIL']:
        return self.node.component

    @component.setter
    def component(self, value: Literal['MESH', 'POINTCLOUD', 'CURVE', 'INSTANCES', 'GREASEPENCIL']) -> None:
        set_property(self.node, 'component', value)

class GetAttributeNames(BaseNode):
    _bl_idname = 'GeometryNodeGetAttributeNames'

    def __init__(self, geometry: InputGeometry=None, filter_data_type: InputBoolean=False, data_type: InputMenu | Literal['Float', 'Integer', 'Boolean', 'Vector', 'Color', 'Quaternion', '4x4 Matrix', 'String', '8-Bit Integer', '2D 16-Bit Integer Vector', '2D Integer Vector', '2D Vector', '4D Vector', 'Byte Color']='Float', filter_domain: InputBoolean=False, domain: InputMenu | Literal['Point', 'Edge', 'Face', 'Face Corner', 'Spline', 'Instance', 'Layer']='Point'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Filter Data Type': filter_data_type, 'Data Type': data_type, 'Filter Domain': filter_domain, 'Domain': domain}
        self._establish_links(**key_args)

class RemoveNamedAttribute(BaseNode):
    _bl_idname = 'GeometryNodeRemoveAttribute'

    def __init__(self, geometry: InputGeometry=None, pattern_mode: InputMenu | Literal['Exact', 'Wildcard']='Exact', name: InputString=''):
        super().__init__()
        key_args = {'Geometry': geometry, 'Pattern Mode': pattern_mode, 'Name': name}
        self._establish_links(**key_args)
