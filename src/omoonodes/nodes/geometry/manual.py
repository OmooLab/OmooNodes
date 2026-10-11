# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
NodeEvaluateClosure = typing.Any
from collections.abc import Iterable, Mapping
from types import TracebackType
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, Self, cast
import bpy
import bpy.types
from bpy.types import ColorRampElements, CurveMapPoints, NodeSocket, NodeSocketString
from ...builder import BaseNode, BooleanSocket, BooleanSocketGrid, BundleSocket, ClosureSocket, CollectionSocket, ColorSocket, FloatSocket, FloatSocketGrid, FontSocket, GeometrySocket, ImageSocket, IntegerSocket, IntegerSocketGrid, IntegerVectorSocket, ItemsMixin, MaterialSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, SocketAccessor, SoundSocket, StringSocket, TreeBuilder, VectorSocket, VectorSocketGrid
from ...builder.items import _ALL_ITEM_TYPES, Item, ItemCollection, MenuItem, _deprecated, _FieldItems, _socket_for_item, _SocketItems, _SocketValueItems, _ValueItems
from ...builder.socket import BaseSocket
from ...builder.tree import _MenuDefault
from ...socket_types import SOCKET_TYPES, Default, InputAny, InputBoolean, InputBooleanGrid, InputBundle, InputClosure, InputCollection, InputColor, InputFloat, InputFloatGrid, InputFont, InputGeometry, InputGrid, InputImage, InputInteger, InputIntegerGrid, InputLinkable, InputMaterial, InputMatrix, InputMenu, InputObject, InputRotation, InputSound, InputString, InputVector, InputVectorGrid, _AttributeDomains, _GridDataTypes
from .zone import ClosureInput, ClosureOutput, ClosureZone, ForEachGeometryElementInput, ForEachGeometryElementOutput, ForEachGeometryElementZone, RepeatInput, RepeatOutput, RepeatZone, SimulationInput, SimulationOutput, SimulationZone, _sync_closure_items
__all__ = ('AttributeStatistic', 'CaptureAttribute', 'ClosureInput', 'ClosureOutput', 'ClosureZone', 'ColorRamp', 'Compare', 'EvaluateClosure', 'FieldToGrid', 'Float', 'FloatCurve', 'ForEachGeometryElementInput', 'ForEachGeometryElementOutput', 'ForEachGeometryElementZone', 'Frame', 'GeometryToInstance', 'IndexSwitch', 'JoinGeometry', 'JoinStrings', 'MenuSwitch', 'MeshBoolean', 'RepeatInput', 'RepeatOutput', 'RepeatZone', 'SDFGridBoolean', 'SimulationInput', 'SimulationOutput', 'SimulationZone', 'StoreNamedAttribute', 'Value')
tree: Final = TreeBuilder.geometry
_ColorRampColorInterpolations = Literal['EASE', 'CARDINAL', 'LINEAR', 'B_SPLINE', 'CONSTANT']
_ColorRampHueInterpolations = Literal['NEAR', 'FAR', 'CW', 'CCW']
_ColorModes = Literal['RGB', 'HSV', 'HSL']
_COLOR_RAMP_DEFAULT_ITEMS = ((0.0, (0.0, 0.0, 0.0, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0)))
_FLOAT_CURVE_DEFAULT_ITEMS = ((0.0, 0.0), (1.0, 1.0))

class ColorRamp(BaseNode):
    _bl_idname = 'ShaderNodeValToRGB'

    def __init__(self, fac: InputFloat=0.5, *, items: Iterable[tuple[float, tuple[float, float, float, float]] | tuple[float, float, float, float, float]]=_COLOR_RAMP_DEFAULT_ITEMS, color_interpolation: _ColorRampColorInterpolations='LINEAR', hue_interpolation: _ColorRampHueInterpolations='NEAR', mode: _ColorModes='RGB'):
        super().__init__()
        key_args = {'Fac': fac}
        stops = sorted(() if items is None else items, key=lambda item: item[0])
        if not stops:
            raise ValueError('ColorRamp requires at least one item')
        els = self.elements
        while len(els) > len(stops):
            els.remove(els[len(els) - 1])
        while len(els) < len(stops):
            els.new(0.0)
        for i in range(len(stops) - 1, -1, -1):
            els[i].position = stops[i][0]
        for i, item in enumerate(stops):
            els[i].color = item[1] if len(item) == 2 else item[1:]
        self._establish_links(**key_args)
        self.color_interpolation = color_interpolation
        self.hue_interpolation = hue_interpolation
        self.mode = mode

    @property
    def _color_ramp(self) -> bpy.types.ColorRamp:
        assert self.node.color_ramp
        return self.node.color_ramp

    @property
    def elements(self) -> ColorRampElements:
        return self._color_ramp.elements

    @property
    def color_interpolation(self) -> _ColorRampColorInterpolations:
        return self._color_ramp.interpolation

    @color_interpolation.setter
    def color_interpolation(self, value: _ColorRampColorInterpolations) -> None:
        self._color_ramp.interpolation = value

    @property
    def hue_interpolation(self) -> _ColorRampHueInterpolations:
        return self._color_ramp.hue_interpolation

    @hue_interpolation.setter
    def hue_interpolation(self, value: _ColorRampHueInterpolations) -> None:
        self._color_ramp.hue_interpolation = value

    @property
    def mode(self) -> _ColorModes:
        return self._color_ramp.color_mode

    @mode.setter
    def mode(self, value: _ColorModes) -> None:
        self._color_ramp.color_mode = value

class FloatCurve(BaseNode):
    _bl_idname = 'ShaderNodeFloatCurve'

    def __init__(self, factor: InputFloat=1.0, value: InputFloat=1.0, *, items: Iterable[tuple[float, float] | tuple[float, float, Literal['AUTO', 'AUTO_CLAMPED', 'VECTOR']]]=_FLOAT_CURVE_DEFAULT_ITEMS):
        super().__init__()
        key_args = {'Factor': factor, 'Value': value}
        items = sorted(() if items is None else items, key=lambda item: item[0])
        if len(items) < 2:
            raise ValueError('FloatCurve requires at least two items')
        points = self.points
        while len(points) < len(items):
            points.new(0.0, 0.0)
        for i, item in enumerate(items):
            points[i].location = item[:2]
            points[i].handle_type = item[2] if len(item) > 2 else 'AUTO'
            points[i].select = False
        mapping = self.node.mapping
        assert mapping
        mapping.update()
        self._establish_links(**key_args)

    @property
    def points(self) -> CurveMapPoints:
        mapping = self.node.mapping
        assert mapping
        return mapping.curves[0].points
_NamedAttributeDataTypes = Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4', 'INT8', 'FLOAT2', 'BYTE_COLOR']

class StoreNamedAttribute(BaseNode):
    _bl_idname = 'GeometryNodeStoreNamedAttribute'

    class _StoreNamedAttributeDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputFloat=0.0) -> 'StoreNamedAttribute[FloatSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='FLOAT', domain=self._domain)

        def integer(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputInteger=0) -> 'StoreNamedAttribute[IntegerSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='INT', domain=self._domain)

        def boolean(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputBoolean=False) -> 'StoreNamedAttribute[BooleanSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='BOOLEAN', domain=self._domain)

        def vector(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputVector=None) -> 'StoreNamedAttribute[VectorSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='FLOAT_VECTOR', domain=self._domain)

        def color(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputColor=None) -> 'StoreNamedAttribute[ColorSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='FLOAT_COLOR', domain=self._domain)

        def quaternion(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputRotation=None) -> 'StoreNamedAttribute[RotationSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='QUATERNION', domain=self._domain)

        def matrix(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputMatrix=None) -> 'StoreNamedAttribute[MatrixSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='FLOAT4X4', domain=self._domain)

        def integer_8bit(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputInteger=0) -> 'StoreNamedAttribute[IntegerSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='INT8', domain=self._domain)

        def vector_2d(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputVector=None) -> 'StoreNamedAttribute[VectorSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='FLOAT2', domain=self._domain)

        def byte_color(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputColor=None) -> 'StoreNamedAttribute[ColorSocket]':
            return StoreNamedAttribute(geometry=geometry, selection=selection, name=name, value=value, data_type='BYTE_COLOR', domain=self._domain)
    point: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('POINT')
    edge: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('EDGE')
    face: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('FACE')
    corner: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('CORNER')
    spline: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('CURVE')
    instance: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('INSTANCE')
    layer: _StoreNamedAttributeDomainFactory = _StoreNamedAttributeDomainFactory('LAYER')

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=True, name: InputString='', value: InputAny=0.0, *, data_type: _NamedAttributeDataTypes='FLOAT', domain: _AttributeDomains='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Name': name, 'Value': value}
        self.data_type = data_type
        self.domain = domain
        self._establish_links(**key_args)

    @property
    def data_type(self) -> _NamedAttributeDataTypes:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: _NamedAttributeDataTypes) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> _AttributeDomains:
        return self.node.domain

    @domain.setter
    def domain(self, value: _AttributeDomains) -> None:
        set_property(self.node, 'domain', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _EvaluateClosureInputs(_SocketValueItems):
    _collection = 'input_items'
    _prefix = 'Item_'
    _has_output = False

class _EvaluateClosureOutputs(_SocketItems):
    _collection = 'output_items'
    _prefix = 'Item_'
    _has_input = False

class EvaluateClosure(ItemsMixin, BaseNode):
    _bl_idname = 'NodeEvaluateClosure'
    _items_collection = 'input_items'
    _socket_data_types = _ALL_ITEM_TYPES
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, closure: InputClosure=None, input_items: 'dict[str, InputLinkable | str] | None'=None, output_items: 'dict[str, str] | None'=None, *, active_input_index: int=0, active_output_index: int=0, define_signature: bool=False):
        super().__init__()
        self.define_signature = define_signature
        self.outputs._add_all(output_items)
        self.inputs._add_all(input_items)
        self.active_input_index = active_input_index
        self.active_output_index = active_output_index
        self._establish_links(Closure=closure)

    def _item_socket(self, item, *, output: bool=False) -> NodeSocket:
        return _socket_for_item(self.node, self._items, 'Item_', item, output=output)

    @property
    def define_signature(self) -> bool:
        return self.node.define_signature

    @define_signature.setter
    def define_signature(self, value: bool) -> None:
        set_property(self.node, 'define_signature', value)

    @property
    def active_input_index(self) -> int:
        return cast('int', self.node.active_input_index)

    @active_input_index.setter
    def active_input_index(self, value: int) -> None:
        set_property(self.node, 'active_input_index', value)

    @property
    def active_output_index(self) -> int:
        return cast('int', self.node.active_output_index)

    @active_output_index.setter
    def active_output_index(self, value: int) -> None:
        set_property(self.node, 'active_output_index', value)

    @property
    def inputs(self) -> _EvaluateClosureInputs:
        return _EvaluateClosureInputs(self)

    @property
    def outputs(self) -> _EvaluateClosureOutputs:
        return _EvaluateClosureOutputs(self)

    def sync_signature(self, node: ClosureOutput | ClosureZone) -> None:
        if isinstance(node, ClosureZone):
            node = node.output
        for name in ['input_items', 'output_items']:
            _sync_closure_items(getattr(node.node, name), getattr(self.node, name))

class Frame(BaseNode):
    _bl_idname = 'NodeFrame'

    def __init__(self, label: str | None=None, shrink: bool=True, text: bpy.types.Text | None=None):
        super().__init__()
        self.label = label
        self.shrink = shrink
        self.text = text

    @property
    def label(self) -> str | None:
        return self.node.label

    @label.setter
    def label(self, value: str | None) -> None:
        if value is not None:
            set_property(self.node, 'label', value)

    @property
    def shrink(self) -> bool:
        return self.node.shrink

    @shrink.setter
    def shrink(self, value: bool) -> None:
        set_property(self.node, 'shrink', value)

    @property
    def text(self) -> bpy.types.Text | None:
        return self.node.text

    @text.setter
    def text(self, value: bpy.types.Text | None) -> None:
        if value is not None:
            set_property(self.node, 'text', value)

    def __enter__(self) -> Self:
        TreeBuilder._frame_contexts.append(self.node)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        TreeBuilder._frame_contexts.pop()

class GeometryToInstance(BaseNode):
    _bl_idname = 'GeometryNodeGeometryToInstance'

    def __init__(self, *args: InputGeometry):
        super().__init__()
        for arg in reversed(args):
            self._link_from(arg, 'Geometry')

class Collection(BaseNode):
    _bl_idname = 'GeometryNodeInputCollection'

    def __init__(self, collection: bpy.types.Collection | None=None):
        super().__init__()
        self.collection = collection

    @property
    def collection(self) -> bpy.types.Collection | None:
        return self.node.collection

    @collection.setter
    def collection(self, value: bpy.types.Collection | None) -> None:
        set_property(self.node, 'collection', value)

class Material(BaseNode):
    _bl_idname = 'GeometryNodeInputMaterial'

    def __init__(self, material: bpy.types.Material | None=None):
        super().__init__()
        self.material = material

    @property
    def material(self) -> bpy.types.Material | None:
        return self.node.material

    @material.setter
    def material(self, value: bpy.types.Material | None) -> None:
        set_property(self.node, 'material', value)

class Object(BaseNode):
    _bl_idname = 'GeometryNodeInputObject'

    def __init__(self, object: bpy.types.Object | None=None):
        super().__init__()
        self.object = object

    @property
    def object(self) -> bpy.types.Object | None:
        return self.node.object

    @object.setter
    def object(self, value: bpy.types.Object | None) -> None:
        set_property(self.node, 'object', value)

class Value(BaseNode):
    _bl_idname = 'ShaderNodeValue'

    def __init__(self, value: float=0.0):
        super().__init__()
        self.value = value

    @property
    def value(self) -> float:
        assert self.node.outputs is not None
        return self.node.outputs[0].default_value

    @value.setter
    def value(self, value: float) -> None:
        assert self.node.outputs is not None
        self.node.outputs[0].default_value = value

class Float(Value):
    pass

class Menu(BaseNode):
    _bl_idname = 'FunctionNodeInputMenu'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

    @property
    def value(self) -> str:
        return self.node.value

    @value.setter
    def value(self, value: str) -> None:
        set_property(self.node, 'value', value)

class IntegerVector(BaseNode):
    _bl_idname = 'FunctionNodeInputIntVector'

    def __init__(self, vector: tuple[int, int, int] | list[int]=(0, 0, 0), vector_dimensions: Literal[2, 3]=3):
        super().__init__()
        key_args = {}
        self.vector = vector
        self.vector_dimensions = vector_dimensions
        self._establish_links(**key_args)

    @property
    def vector(self) -> list[int]:
        return list(self.node.vector)

    @vector.setter
    def vector(self, value: tuple[int, int, int] | list[int]) -> None:
        set_property(self.node, 'vector', value)

    @property
    def vector_dimensions(self) -> int:
        return self.node.vector_dimensions

    @vector_dimensions.setter
    def vector_dimensions(self, value: Literal[2, 3]) -> None:
        set_property(self.node, 'vector_dimensions', value)

class JoinStrings(BaseNode):
    _bl_idname = 'GeometryNodeStringJoin'

    def __init__(self, strings: Iterable[str | StringSocket | NodeSocketString | BaseNode]=(), delimiter: InputString=''):
        super().__init__()
        self._establish_links(Delimiter=delimiter)
        for string in reversed(list(strings)):
            if isinstance(string, str):
                from . import String
                string = String(string)
            self._link_from(string, 'Strings')

class MeshBoolean(BaseNode):
    _bl_idname = 'GeometryNodeMeshBoolean'

    def __init__(self, mesh_1: InputGeometry=None, mesh_2: Iterable[InputGeometry]=(), *, self_intersection: InputBoolean=False, hole_tolerant: InputBoolean=False, operation: Literal['INTERSECT', 'UNION', 'DIFFERENCE']='DIFFERENCE', solver: Literal['EXACT', 'FLOAT', 'MANIFOLD']='FLOAT'):
        super().__init__()
        key_args = {'Mesh 1': mesh_1, 'Self Intersection': self_intersection, 'Hole Tolerant': hole_tolerant}
        for arg in mesh_2:
            self._link_from(arg, 'Mesh 2')
        self.operation = operation
        self.solver = solver
        self._establish_links(**key_args)

    @classmethod
    def intersect(cls, items: Iterable[InputGeometry]=(), self_intersection: InputBoolean=False, hole_tolerant: InputBoolean=False, *, solver: Literal['EXACT', 'FLOAT', 'MANIFOLD']='FLOAT') -> 'MeshBoolean':
        if solver == 'EXACT':
            return cls(mesh_2=items, self_intersection=self_intersection, hole_tolerant=hole_tolerant, solver=solver, operation='INTERSECT')
        else:
            return cls(mesh_2=items, solver=solver, operation='INTERSECT')

    @classmethod
    def union(cls, items: Iterable[InputGeometry]=(), self_intersection: InputBoolean=False, hole_tolerant: InputBoolean=False, *, solver: Literal['EXACT', 'FLOAT', 'MANIFOLD']='FLOAT') -> 'MeshBoolean':
        if solver == 'EXACT':
            return cls(mesh_2=items, self_intersection=self_intersection, hole_tolerant=hole_tolerant, solver=solver, operation='UNION')
        else:
            return cls(mesh_2=items, solver=solver, operation='UNION')

    @classmethod
    def difference(cls, mesh_1: InputGeometry=None, items: Iterable[InputGeometry]=(), self_intersection: InputBoolean=False, hole_tolerant: InputBoolean=False, *, solver: Literal['EXACT', 'FLOAT', 'MANIFOLD']='FLOAT') -> 'MeshBoolean':
        if solver == 'EXACT':
            return cls(mesh_1=mesh_1, mesh_2=items, self_intersection=self_intersection, hole_tolerant=hole_tolerant, solver=solver, operation='DIFFERENCE')
        else:
            return cls(mesh_1=mesh_1, mesh_2=items, solver=solver, operation='DIFFERENCE')

    @property
    def operation(self) -> Literal['INTERSECT', 'UNION', 'DIFFERENCE']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['INTERSECT', 'UNION', 'DIFFERENCE']) -> None:
        set_property(self.node, 'operation', value)

    @property
    def solver(self) -> Literal['EXACT', 'FLOAT', 'MANIFOLD']:
        return self.node.solver

    @solver.setter
    def solver(self, value: Literal['EXACT', 'FLOAT', 'MANIFOLD']) -> None:
        set_property(self.node, 'solver', value)

class JoinGeometry(BaseNode):
    _bl_idname = 'GeometryNodeJoinGeometry'

    def __init__(self, geometry: Iterable[InputGeometry]=()):
        super().__init__()
        for source in reversed(list(geometry)):
            assert source is not None
            if isinstance(source, Default):
                continue
            self._link(*self._find_best_socket_pair(source, self))

class _IndexSwitchItems(ItemCollection):
    _has_output = False

    def new(self, value: InputAny=None) -> 'Item[T]':
        return self._declare(value, '', self._owner.data_type)

    def _add_all(self, items: Mapping[str, Any] | Iterable[Any] | None) -> None:
        for value in items or ():
            self.new(value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class IndexSwitch(ItemsMixin, BaseNode):
    _bl_idname = 'GeometryNodeIndexSwitch'
    _items_collection = 'index_switch_items'

    @classmethod
    def float(cls, index: InputInteger=0, items: Iterable[InputFloat]=()) -> 'IndexSwitch[FloatSocket]':
        return IndexSwitch(index=index, items=items, data_type='FLOAT')

    @classmethod
    def integer(cls, index: InputInteger=0, items: Iterable[InputInteger]=()) -> 'IndexSwitch[IntegerSocket]':
        return IndexSwitch(index=index, items=items, data_type='INT')

    @classmethod
    def boolean(cls, index: InputInteger=0, items: Iterable[InputBoolean]=()) -> 'IndexSwitch[BooleanSocket]':
        return IndexSwitch(index=index, items=items, data_type='BOOLEAN')

    @classmethod
    def vector(cls, index: InputInteger=0, items: Iterable[InputVector]=()) -> 'IndexSwitch[VectorSocket]':
        return IndexSwitch(index=index, items=items, data_type='VECTOR')

    @classmethod
    def color(cls, index: InputInteger=0, items: Iterable[InputColor]=()) -> 'IndexSwitch[ColorSocket]':
        return IndexSwitch(index=index, items=items, data_type='RGBA')

    @classmethod
    def rotation(cls, index: InputInteger=0, items: Iterable[InputRotation]=()) -> 'IndexSwitch[RotationSocket]':
        return IndexSwitch(index=index, items=items, data_type='ROTATION')

    @classmethod
    def matrix(cls, index: InputInteger=0, items: Iterable[InputMatrix]=()) -> 'IndexSwitch[MatrixSocket]':
        return IndexSwitch(index=index, items=items, data_type='MATRIX')

    @classmethod
    def string(cls, index: InputInteger=0, items: Iterable[InputString]=()) -> 'IndexSwitch[StringSocket]':
        return IndexSwitch(index=index, items=items, data_type='STRING')

    @classmethod
    def menu(cls, index: InputInteger=0, items: Iterable[InputMenu]=()) -> 'IndexSwitch[MenuSocket]':
        return IndexSwitch(index=index, items=items, data_type='MENU')

    @classmethod
    def object(cls, index: InputInteger=0, items: Iterable[InputObject]=()) -> 'IndexSwitch[ObjectSocket]':
        return IndexSwitch(index=index, items=items, data_type='OBJECT')

    @classmethod
    def geometry(cls, index: InputInteger=0, items: Iterable[InputGeometry]=()) -> 'IndexSwitch[GeometrySocket]':
        return IndexSwitch(index=index, items=items, data_type='GEOMETRY')

    @classmethod
    def collection(cls, index: InputInteger=0, items: Iterable[InputCollection]=()) -> 'IndexSwitch[CollectionSocket]':
        return IndexSwitch(index=index, items=items, data_type='COLLECTION')

    @classmethod
    def image(cls, index: InputInteger=0, items: Iterable[InputImage]=()) -> 'IndexSwitch[ImageSocket]':
        return IndexSwitch(index=index, items=items, data_type='IMAGE')

    @classmethod
    def material(cls, index: InputInteger=0, items: Iterable[InputMaterial]=()) -> 'IndexSwitch[MaterialSocket]':
        return IndexSwitch(index=index, items=items, data_type='MATERIAL')

    @classmethod
    def bundle(cls, index: InputInteger=0, items: Iterable[InputBundle]=()) -> 'IndexSwitch[BundleSocket]':
        return IndexSwitch(index=index, items=items, data_type='BUNDLE')

    @classmethod
    def closure(cls, index: InputInteger=0, items: Iterable[InputClosure]=()) -> 'IndexSwitch[ClosureSocket]':
        return IndexSwitch(index=index, items=items, data_type='CLOSURE')

    @classmethod
    def font(cls, index: InputInteger=0, items: Iterable[InputFont]=()) -> 'IndexSwitch[FontSocket]':
        return IndexSwitch(index=index, items=items, data_type='FONT')

    @classmethod
    def sound(cls, index: InputInteger=0, items: Iterable[InputSound]=()) -> 'IndexSwitch[SoundSocket]':
        return IndexSwitch(index=index, items=items, data_type='SOUND')

    def __init__(self, index: InputInteger=0, items: Iterable[InputAny]=(), data_type: SOCKET_TYPES='FLOAT'):
        super().__init__()
        self.data_type = data_type
        self.node.index_switch_items.clear()
        self.items._add_all(items)
        self._establish_links(Index=index)

    @property
    def items(self) -> '_IndexSwitchItems[T]':
        return _IndexSwitchItems(self)

    @property
    def _socket_data_types(self) -> tuple[str, ...]:
        return ('VALUE' if self.data_type == 'FLOAT' else self.data_type,)

    def _new_item(self, name: str, type: str) -> bpy.types.IndexSwitchItem:
        return self._items.new()

    def _item_socket(self, item: bpy.types.IndexSwitchItem, *, output: bool=False) -> NodeSocket:
        if output:
            raise ValueError('Index switch items do not have output sockets')
        identifier = f'Item_{item.identifier}'
        assert self.node.inputs is not None
        for socket in self.node.inputs:
            if socket.identifier == identifier:
                return socket
        raise KeyError(f'No input socket for index switch item {item.identifier}')

    @property
    def data_type(self) -> SOCKET_TYPES:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: SOCKET_TYPES) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
MenuItems = typing.Any

def _split_menu_item(value: InputAny | tuple[InputAny, str]) -> tuple[InputAny, str | None]:
    if isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], str):
        return (value[0], value[1])
    return (cast('InputAny', value), None)

class _MenuSwitchItems(ItemCollection):
    _handle_type = MenuItem

    def new(self, value: InputAny | tuple[InputAny, str]=None, name: str | None=None, *, description: str | None=None) -> 'MenuItem[T]':
        value, pair_description = _split_menu_item(value)
        handle = self._declare(value, name, self._owner.data_type, description=description or pair_description or '')
        if len(self._bpy) == 1 and (not self._owner._explicit_selection):
            self._owner._default_selection_to_first()
        return handle

    def _default_name(self, type: str) -> str:
        return 'Item'

    def _add_all(self, items: Mapping[str, Any] | Iterable[Any] | None) -> None:
        if isinstance(items, Mapping):
            for name, value in items.items():
                self.new(value, name)
        else:
            for value in items or ():
                self.new(value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _MenuSwitchBase(ItemsMixin, BaseNode):
    _bl_idname = 'GeometryNodeMenuSwitch'
    _items_collection = 'enum_items'

    def __init__(self, menu: InputMenu=None, items: MenuItems[InputAny] | None=None, *, data_type: SOCKET_TYPES='FLOAT'):
        super().__init__()
        self.data_type = data_type
        # Reuse Blender's first items so modifier menu values keep their IDs.
        self._initial_items = list(self.node.enum_items)
        self._explicit_selection = isinstance(menu, str)
        self.items._add_all(items)
        for item in self._initial_items:
            self.node.enum_items.remove(item)
        self._initial_items.clear()
        if self.node.enum_items and not self._explicit_selection:
            self._default_selection_to_first()
        if isinstance(menu, str) and (not self.node.enum_items):
            assert self.node.inputs is not None
            self.tree._menu_defaults.append(_MenuDefault(self.node.inputs['Menu'], menu))
        else:
            self._establish_links(Menu=menu)

    @property
    def items(self) -> '_MenuSwitchItems[T]':
        return _MenuSwitchItems(self)

    def _default_selection_to_first(self) -> None:
        assert self.node.inputs is not None
        try:
            menu_socket = self.node.inputs['Menu']
            menu_socket.default_value = self.node.enum_items[0].name
        except TypeError:
            self.tree._menu_defaults.append(_MenuDefault(self.node.inputs['Menu'], self.node.enum_items[0].name))

    @property
    def _socket_data_types(self) -> tuple[str, ...]:
        return ('VALUE' if self.data_type == 'FLOAT' else self.data_type,)

    def _new_item(self, name: str, type: str) -> bpy.types.NodeEnumItem:
        if self._initial_items:
            item = self._initial_items.pop(0)
            item.name = name
            return item
        return self._items.new(name)

    def item(self, name: str, value: InputAny | tuple[InputAny, str]=None, *, description: str | None=None) -> MenuItem[T]:
        _deprecated('item(name, value)', 'items.new(value, name)')
        return self.items.new(value, name, description=description)

    def is_selected(self, name: str) -> BooleanSocket:
        assert name != 'Output'
        return cast(BooleanSocket, self.o[name])

    @property
    def data_type(self) -> SOCKET_TYPES:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: SOCKET_TYPES) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class MenuSwitch(_MenuSwitchBase):

    @classmethod
    def float(cls, menu: InputMenu=None, items: MenuItems[InputFloat] | None=None) -> 'MenuSwitch[FloatSocket]':
        return MenuSwitch(menu, items, data_type='FLOAT')

    @classmethod
    def integer(cls, menu: InputMenu=None, items: MenuItems[InputInteger] | None=None) -> 'MenuSwitch[IntegerSocket]':
        return MenuSwitch(menu, items, data_type='INT')

    @classmethod
    def boolean(cls, menu: InputMenu=None, items: MenuItems[InputBoolean] | None=None) -> 'MenuSwitch[BooleanSocket]':
        return MenuSwitch(menu, items, data_type='BOOLEAN')

    @classmethod
    def vector(cls, menu: InputMenu=None, items: MenuItems[InputVector] | None=None) -> 'MenuSwitch[VectorSocket]':
        return MenuSwitch(menu, items, data_type='VECTOR')

    @classmethod
    def color(cls, menu: InputMenu=None, items: MenuItems[InputColor] | None=None) -> 'MenuSwitch[ColorSocket]':
        return MenuSwitch(menu, items, data_type='RGBA')

    @classmethod
    def rotation(cls, menu: InputMenu=None, items: MenuItems[InputRotation] | None=None) -> 'MenuSwitch[RotationSocket]':
        return MenuSwitch(menu, items, data_type='ROTATION')

    @classmethod
    def matrix(cls, menu: InputMenu=None, items: MenuItems[InputMatrix] | None=None) -> 'MenuSwitch[MatrixSocket]':
        return MenuSwitch(menu, items, data_type='MATRIX')

    @classmethod
    def string(cls, menu: InputMenu=None, items: MenuItems[InputString] | None=None) -> 'MenuSwitch[StringSocket]':
        return MenuSwitch(menu, items, data_type='STRING')

    @classmethod
    def menu(cls, menu: InputMenu=None, items: MenuItems[InputMenu] | None=None) -> 'MenuSwitch[MenuSocket]':
        return MenuSwitch(menu, items, data_type='MENU')

    @classmethod
    def object(cls, menu: InputMenu=None, items: MenuItems[InputObject] | None=None) -> 'MenuSwitch[ObjectSocket]':
        return MenuSwitch(menu, items, data_type='OBJECT')

    @classmethod
    def geometry(cls, menu: InputMenu=None, items: MenuItems[InputGeometry] | None=None) -> 'MenuSwitch[GeometrySocket]':
        return MenuSwitch(menu, items, data_type='GEOMETRY')

    @classmethod
    def collection(cls, menu: InputMenu=None, items: MenuItems[InputCollection] | None=None) -> 'MenuSwitch[CollectionSocket]':
        return MenuSwitch(menu, items, data_type='COLLECTION')

    @classmethod
    def image(cls, menu: InputMenu=None, items: MenuItems[InputImage] | None=None) -> 'MenuSwitch[ImageSocket]':
        return MenuSwitch(menu, items, data_type='IMAGE')

    @classmethod
    def material(cls, menu: InputMenu=None, items: MenuItems[InputMaterial] | None=None) -> 'MenuSwitch[MaterialSocket]':
        return MenuSwitch(menu, items, data_type='MATERIAL')

    @classmethod
    def bundle(cls, menu: InputMenu=None, items: MenuItems[InputBundle] | None=None) -> 'MenuSwitch[BundleSocket]':
        return MenuSwitch(menu, items, data_type='BUNDLE')

    @classmethod
    def closure(cls, menu: InputMenu=None, items: MenuItems[InputClosure] | None=None) -> 'MenuSwitch[ClosureSocket]':
        return MenuSwitch(menu, items, data_type='CLOSURE')

    @classmethod
    def font(cls, menu: InputMenu=None, items: dict[str, InputFont] | None=None) -> 'MenuSwitch[FontSocket]':
        return MenuSwitch(menu, items, data_type='FONT')

    @classmethod
    def sound(cls, menu: InputMenu=None, items: dict[str, InputSound] | None=None) -> 'MenuSwitch[SoundSocket]':
        return MenuSwitch(menu, items, data_type='SOUND')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class CaptureAttribute(ItemsMixin, BaseNode):
    _bl_idname = 'GeometryNodeCaptureAttribute'
    _items_collection = 'capture_items'
    _socket_data_types = ('VALUE', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX')
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    class _DomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def __call__(self, geometry: InputGeometry=None, selection: InputBoolean=True, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None) -> 'CaptureAttribute':
            return CaptureAttribute(geometry=geometry, selection=selection, domain=self._domain, items=items)
    point: _DomainFactory = _DomainFactory('POINT')
    edge: _DomainFactory = _DomainFactory('EDGE')
    face: _DomainFactory = _DomainFactory('FACE')
    corner: _DomainFactory = _DomainFactory('CORNER')
    curve: _DomainFactory = _DomainFactory('CURVE')
    instance: _DomainFactory = _DomainFactory('INSTANCE')
    layer: _DomainFactory = _DomainFactory('LAYER')

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=True, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None, *, domain: _AttributeDomains='POINT'):
        super().__init__()
        self.domain = domain
        self.items._add_all(items)
        self._establish_links(Geometry=geometry, Selection=selection)

    @property
    def items(self) -> _FieldItems:
        return _FieldItems(self)

    @property
    def domain(self) -> _AttributeDomains:
        return self.node.domain

    @domain.setter
    def domain(self, value: _AttributeDomains) -> None:
        set_property(self.node, 'domain', value)

class _FieldToGridItems(_ValueItems):

    def float(self, value: InputFloat=None, name: str | None=None) -> 'Item[FloatSocket, FloatSocketGrid]':
        return self._typed(value, name, 'FLOAT')

    def integer(self, value: InputInteger=None, name: str | None=None) -> 'Item[IntegerSocket, IntegerSocketGrid]':
        return self._typed(value, name, 'INT')

    def vector(self, value: InputVector=None, name: str | None=None) -> 'Item[VectorSocket, VectorSocketGrid]':
        return self._typed(value, name, 'VECTOR')

    def boolean(self, value: InputBoolean=None, name: str | None=None) -> 'Item[BooleanSocket, BooleanSocketGrid]':
        return self._typed(value, name, 'BOOLEAN')

class FieldToGrid(ItemsMixin, BaseNode):
    _bl_idname = 'GeometryNodeFieldToGrid'
    _items_collection = 'grid_items'
    _socket_data_types = ('VALUE', 'INT', 'VECTOR', 'BOOLEAN')
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}
    _default_input_id = 'Topology'

    def __init__(self, topology: InputGrid=None, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None, *, data_type: _GridDataTypes='FLOAT'):
        super().__init__()
        self.data_type = data_type
        self.items._add_all(items)
        self._establish_links(Topology=topology)

    @classmethod
    def float(cls, topology: InputFloatGrid=None, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None) -> 'FieldToGrid[FloatSocketGrid]':
        return FieldToGrid(topology, items, data_type='FLOAT')

    @classmethod
    def integer(cls, topology: InputIntegerGrid=None, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None) -> 'FieldToGrid[IntegerSocketGrid]':
        return FieldToGrid(topology, items, data_type='INT')

    @classmethod
    def vector(cls, topology: InputVectorGrid=None, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None) -> 'FieldToGrid[VectorSocketGrid]':
        return FieldToGrid(topology, items, data_type='VECTOR')

    @classmethod
    def boolean(cls, topology: InputBooleanGrid=None, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None) -> 'FieldToGrid[BooleanSocketGrid]':
        return FieldToGrid(topology, items, data_type='BOOLEAN')

    @property
    def items(self) -> _FieldToGridItems:
        return _FieldToGridItems(self)

    @property
    def data_type(self) -> _GridDataTypes:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: _GridDataTypes) -> None:
        set_property(self.node, 'data_type', value)

    def _grid_item(self, type: str, field: Any, name: str | None) -> Any:
        _deprecated(f'capture_{type.lower()}(field, name)', 'items.<type>(field, name).output')
        return self.items._declare(field, name, type).output

    def capture_float(self, field: InputFloat=None, name: str | None=None) -> FloatSocketGrid:
        return self._grid_item('FLOAT', field, name)

    def capture_boolean(self, field: InputBoolean=None, name: str | None=None) -> BooleanSocketGrid:
        return self._grid_item('BOOLEAN', field, name)

    def capture_vector(self, field: InputVector=None, name: str | None=None) -> VectorSocketGrid:
        return self._grid_item('VECTOR', field, name)

    def capture_integer(self, field: InputInteger=None, name: str | None=None) -> IntegerSocketGrid:
        return self._grid_item('INT', field, name)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SDFGridBoolean(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridBoolean'

    def __init__(self, grid_1: InputFloatGrid=None, grid_2: Iterable[InputFloatGrid]=(), *, operation: Literal['INTERSECT', 'UNION', 'DIFFERENCE']='DIFFERENCE'):
        super().__init__()
        self.operation = operation
        if grid_1 is not None and (not isinstance(grid_1, Default)):
            self._link_from(*self._find_best_socket_pair(grid_1, self.i['Grid 1']))
        for grid in reversed(list(grid_2)):
            assert grid is not None
            self._link_from(*self._find_best_socket_pair(grid, self.i['Grid 2']))

    @classmethod
    def intersect(cls, grids: Iterable[InputFloatGrid]=()) -> 'SDFGridBoolean':
        return cls(grid_2=grids, operation='INTERSECT')

    @classmethod
    def union(cls, grids: Iterable[InputFloatGrid]=()) -> 'SDFGridBoolean':
        return cls(grid_2=grids, operation='UNION')

    @classmethod
    def difference(cls, grid_1: InputFloatGrid=None, grids: Iterable[InputFloatGrid]=()) -> 'SDFGridBoolean':
        return cls(grid_1, grids, operation='DIFFERENCE')

    @property
    def operation(self) -> Literal['INTERSECT', 'UNION', 'DIFFERENCE']:
        return self.node.operation

    @operation.setter
    def operation(self, value: Literal['INTERSECT', 'UNION', 'DIFFERENCE']) -> None:
        set_property(self.node, 'operation', value)
_CompareOperations = Literal['LESS_THAN', 'LESS_EQUAL', 'GREATER_THAN', 'GREATER_EQUAL', 'EQUAL', 'NOT_EQUAL', 'BRIGHTER', 'DARKER']
_CompareDataTypes = Literal['FLOAT', 'INT', 'VECTOR', 'RGBA', 'STRING', 'OBJECT', 'IMAGE', 'COLLECTION', 'MATERIAL', 'FONT', 'SOUND']
_CompareVectorModes = Literal['ELEMENT', 'LENGTH', 'AVERAGE', 'DOT_PRODUCT', 'DIRECTION']

class Compare(BaseNode):
    _bl_idname = 'FunctionNodeCompare'

    class _FloatFactory:

        @staticmethod
        def less_than(a: InputFloat=0.0, b: InputFloat=0.0) -> 'Compare[FloatSocket]':
            return Compare(operation='LESS_THAN', data_type='FLOAT', A=a, B=b)

        @staticmethod
        def less_equal(a: InputFloat=0.0, b: InputFloat=0.0) -> 'Compare[FloatSocket]':
            return Compare(operation='LESS_EQUAL', data_type='FLOAT', A=a, B=b)

        @staticmethod
        def greater_than(a: InputFloat=0.0, b: InputFloat=0.0) -> 'Compare[FloatSocket]':
            return Compare(operation='GREATER_THAN', data_type='FLOAT', A=a, B=b)

        @staticmethod
        def greater_equal(a: InputFloat=0.0, b: InputFloat=0.0) -> 'Compare[FloatSocket]':
            return Compare(operation='GREATER_EQUAL', data_type='FLOAT', A=a, B=b)

        @staticmethod
        def equal(a: InputFloat=0.0, b: InputFloat=0.0, epsilon: InputFloat=0.0001) -> 'Compare[FloatSocket]':
            return Compare(operation='EQUAL', data_type='FLOAT', A=a, B=b, Epsilon=epsilon)

        @staticmethod
        def not_equal(a: InputFloat=0.0, b: InputFloat=0.0, epsilon: InputFloat=0.0001) -> 'Compare[FloatSocket]':
            return Compare(operation='NOT_EQUAL', data_type='FLOAT', A=a, B=b, Epsilon=epsilon)

    class _IntegerFactory:

        @staticmethod
        def less_than(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='LESS_THAN', data_type='INT', A=a, B=b)

        @staticmethod
        def less_equal(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='LESS_EQUAL', data_type='INT', A=a, B=b)

        @staticmethod
        def greater_than(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='GREATER_THAN', data_type='INT', A=a, B=b)

        @staticmethod
        def greater_equal(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='GREATER_EQUAL', data_type='INT', A=a, B=b)

        @staticmethod
        def equal(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='EQUAL', data_type='INT', A=a, B=b)

        @staticmethod
        def not_equal(a: InputInteger=0, b: InputInteger=0) -> 'Compare[IntegerSocket]':
            return Compare(operation='NOT_EQUAL', data_type='INT', A=a, B=b)

    class _VectorFactory:

        @staticmethod
        def _make(operation: _CompareOperations, a: InputVector, b: InputVector, mode: _CompareVectorModes, c: InputFloat, angle: InputFloat, epsilon: InputFloat) -> 'Compare[VectorSocket]':
            kwargs: dict = {'operation': operation, 'data_type': 'VECTOR', 'mode': mode, 'A': a, 'B': b}
            if operation in ('EQUAL', 'NOT_EQUAL') and epsilon is not None:
                kwargs['Epsilon'] = epsilon
            if mode == 'DIRECTION' and angle is not None:
                kwargs['Angle'] = angle
            elif mode == 'DOT_PRODUCT' and c is not None:
                kwargs['C'] = c
            return Compare(**kwargs)

        @staticmethod
        def less_than(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('LESS_THAN', a, b, mode, c, angle, None)

        @staticmethod
        def less_equal(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('LESS_EQUAL', a, b, mode, c, angle, None)

        @staticmethod
        def greater_than(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('GREATER_THAN', a, b, mode, c, angle, None)

        @staticmethod
        def greater_equal(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('GREATER_EQUAL', a, b, mode, c, angle, None)

        @staticmethod
        def equal(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None, epsilon: InputFloat=0.0001) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('EQUAL', a, b, mode, c, angle, epsilon)

        @staticmethod
        def not_equal(a: InputVector=(0.0, 0.0, 0.0), b: InputVector=(0.0, 0.0, 0.0), *, mode: _CompareVectorModes='ELEMENT', c: InputFloat=None, angle: InputFloat=None, epsilon: InputFloat=0.0001) -> 'Compare[VectorSocket]':
            return Compare._VectorFactory._make('NOT_EQUAL', a, b, mode, c, angle, epsilon)

    class _ColorFactory:

        @staticmethod
        def brighter(a: InputColor=None, b: InputColor=None) -> 'Compare[ColorSocket]':
            return Compare(operation='BRIGHTER', data_type='RGBA', A=a, B=b)

        @staticmethod
        def darker(a: InputColor=None, b: InputColor=None) -> 'Compare[ColorSocket]':
            return Compare(operation='DARKER', data_type='RGBA', A=a, B=b)

        @staticmethod
        def equal(a: InputColor=None, b: InputColor=None, epsilon: InputFloat=0.0001) -> 'Compare[ColorSocket]':
            return Compare(operation='EQUAL', data_type='RGBA', A=a, B=b, Epsilon=epsilon)

        @staticmethod
        def not_equal(a: InputColor=None, b: InputColor=None, epsilon: InputFloat=0.0001) -> 'Compare[ColorSocket]':
            return Compare(operation='NOT_EQUAL', data_type='RGBA', A=a, B=b, Epsilon=epsilon)

    class _StringFactory:

        @staticmethod
        def equal(a: InputString='', b: InputString='') -> 'Compare[StringSocket]':
            return Compare(operation='EQUAL', data_type='STRING', A=a, B=b)

        @staticmethod
        def not_equal(a: InputString='', b: InputString='') -> 'Compare[StringSocket]':
            return Compare(operation='NOT_EQUAL', data_type='STRING', A=a, B=b)

    class _ObjectFactory:

        @staticmethod
        def equal(a: InputObject=None, b: InputObject=None) -> 'Compare[ObjectSocket]':
            return Compare(operation='EQUAL', data_type='OBJECT', A=a, B=b)

        @staticmethod
        def not_equal(a: InputObject=None, b: InputObject=None) -> 'Compare[ObjectSocket]':
            return Compare(operation='NOT_EQUAL', data_type='OBJECT', A=a, B=b)

    class _ImageFactory:

        @staticmethod
        def equal(a: InputImage=None, b: InputImage=None) -> 'Compare[ImageSocket]':
            return Compare(operation='EQUAL', data_type='IMAGE', A=a, B=b)

        @staticmethod
        def not_equal(a: InputImage=None, b: InputImage=None) -> 'Compare[ImageSocket]':
            return Compare(operation='NOT_EQUAL', data_type='IMAGE', A=a, B=b)

    class _CollectionFactory:

        @staticmethod
        def equal(a: InputCollection=None, b: InputCollection=None) -> 'Compare[CollectionSocket]':
            return Compare(operation='EQUAL', data_type='COLLECTION', A=a, B=b)

        @staticmethod
        def not_equal(a: InputCollection=None, b: InputCollection=None) -> 'Compare[CollectionSocket]':
            return Compare(operation='NOT_EQUAL', data_type='COLLECTION', A=a, B=b)

    class _MaterialFactory:

        @staticmethod
        def equal(a: InputMaterial=None, b: InputMaterial=None) -> 'Compare[MaterialSocket]':
            return Compare(operation='EQUAL', data_type='MATERIAL', A=a, B=b)

        @staticmethod
        def not_equal(a: InputMaterial=None, b: InputMaterial=None) -> 'Compare[MaterialSocket]':
            return Compare(operation='NOT_EQUAL', data_type='MATERIAL', A=a, B=b)

    class _FontFactory:

        @staticmethod
        def equal(a: InputFont=None, b: InputFont=None) -> 'Compare[FontSocket]':
            return Compare(operation='EQUAL', data_type='FONT', A=a, B=b)

        @staticmethod
        def not_equal(a: InputFont=None, b: InputFont=None) -> 'Compare[FontSocket]':
            return Compare(operation='NOT_EQUAL', data_type='FONT', A=a, B=b)

    class _SoundFactory:

        @staticmethod
        def equal(a: InputSound=None, b: InputSound=None) -> 'Compare[SoundSocket]':
            return Compare(operation='EQUAL', data_type='SOUND', A=a, B=b)

        @staticmethod
        def not_equal(a: InputSound=None, b: InputSound=None) -> 'Compare[SoundSocket]':
            return Compare(operation='NOT_EQUAL', data_type='SOUND', A=a, B=b)
    float: _FloatFactory = _FloatFactory()
    integer: _IntegerFactory = _IntegerFactory()
    vector: _VectorFactory = _VectorFactory()
    color: _ColorFactory = _ColorFactory()
    string: _StringFactory = _StringFactory()
    object: _ObjectFactory = _ObjectFactory()
    image: _ImageFactory = _ImageFactory()
    collection: _CollectionFactory = _CollectionFactory()
    material: _MaterialFactory = _MaterialFactory()
    font: _FontFactory = _FontFactory()
    sound: _SoundFactory = _SoundFactory()

    def __init__(self, operation: _CompareOperations='GREATER_THAN', data_type: _CompareDataTypes='FLOAT', **kwargs: Any):
        super().__init__()
        self.data_type = data_type
        self.operation = operation
        if self.data_type == 'VECTOR':
            self.mode = kwargs.pop('mode')
        self._establish_links(**kwargs)

    @property
    def operation(self) -> _CompareOperations:
        return self.node.operation

    @operation.setter
    def operation(self, value: _CompareOperations) -> None:
        set_property(self.node, 'operation', value)

    @property
    def data_type(self) -> _CompareDataTypes:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: _CompareDataTypes) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def mode(self) -> _CompareVectorModes:
        return self.node.mode

    @mode.setter
    def mode(self, value: _CompareVectorModes) -> None:
        set_property(self.node, 'mode', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class AttributeStatistic(BaseNode):
    _bl_idname = 'GeometryNodeAttributeStatistic'

    class _AttributeStatisticDomainFactor:

        def __init__(self, domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']):
            self._domain = domain

        def float(self, geometry: InputGeometry=None, selection: InputBoolean=None, attribute: InputFloat=None) -> 'AttributeStatistic[FloatSocket]':
            return AttributeStatistic(geometry, selection, attribute, data_type='FLOAT', domain=self._domain)

        def vector(self, geometry: InputGeometry=None, selection: InputBoolean=None, attribute: InputVector=None) -> 'AttributeStatistic[VectorSocket]':
            return AttributeStatistic(geometry, selection, attribute, data_type='FLOAT_VECTOR', domain=self._domain)
    point: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('POINT')
    edge: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('EDGE')
    face: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('FACE')
    corner: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('CORNER')
    spline: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('CURVE')
    instance: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('INSTANCE')
    layer: _AttributeStatisticDomainFactor = _AttributeStatisticDomainFactor('LAYER')

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=True, attribute: InputFloat | InputVector=None, *, data_type: Literal['FLOAT', 'FLOAT_VECTOR']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT', **kwargs: InputAny):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Attribute': attribute}
        key_args.update(kwargs)
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
    def domain(self) -> _AttributeDomains:
        return self.node.domain

    @domain.setter
    def domain(self, value: _AttributeDomains) -> None:
        set_property(self.node, 'domain', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
_SampleCurveDataTypes = Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']

class SampleCurve(BaseNode):

    class _SampleCurveFactorFactory:

        def float(self, curves: InputGeometry=None, value: InputFloat=0.0, factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[FloatSocket]':
            return SampleCurve(data_type='FLOAT', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def integer(self, curves: InputGeometry=None, value: InputInteger=0, factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[IntegerSocket]':
            return SampleCurve(data_type='INT', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def boolean(self, curves: InputGeometry=None, value: InputBoolean=False, factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[BooleanSocket]':
            return SampleCurve(data_type='BOOLEAN', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def vector(self, curves: InputGeometry=None, value: InputVector=(0.0, 0.0, 0.0), factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[VectorSocket]':
            return SampleCurve(data_type='FLOAT_VECTOR', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def color(self, curves: InputGeometry=None, value: InputColor=(0.0, 0.0, 0.0, 0.0), factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[VectorSocket]':
            return SampleCurve(data_type='FLOAT_COLOR', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def quaternion(self, curves: InputGeometry=None, value: InputRotation=(0.0, 0.0, 0.0), factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[RotationSocket]':
            return SampleCurve(data_type='QUATERNION', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

        def matrix(self, curves: InputGeometry=None, value: InputMatrix=None, factor: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[MatrixSocket]':
            return SampleCurve(data_type='FLOAT4X4', curves=curves, value=value, factor=factor, curve_index=curve_index, mode='FACTOR', use_all_curves=use_all_curves)

    class _SampleCurveLengthFactory:

        def float(self, curves: InputGeometry=None, value: InputFloat=0.0, length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[FloatSocket]':
            return SampleCurve(data_type='FLOAT', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def integer(self, curves: InputGeometry=None, value: InputInteger=0, length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[IntegerSocket]':
            return SampleCurve(data_type='INT', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def boolean(self, curves: InputGeometry=None, value: InputBoolean=False, length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[BooleanSocket]':
            return SampleCurve(data_type='BOOLEAN', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def vector(self, curves: InputGeometry=None, value: InputVector=(0.0, 0.0, 0.0), length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[VectorSocket]':
            return SampleCurve(data_type='FLOAT_VECTOR', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def color(self, curves: InputGeometry=None, value: InputColor=(0.0, 0.0, 0.0, 0.0), length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[VectorSocket]':
            return SampleCurve(data_type='FLOAT_COLOR', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def quaternion(self, curves: InputGeometry=None, value: InputRotation=(0.0, 0.0, 0.0), length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[RotationSocket]':
            return SampleCurve(data_type='QUATERNION', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)

        def matrix(self, curves: InputGeometry=None, value: InputMatrix=None, length: InputFloat=0.0, curve_index: InputInteger=0, *, use_all_curves: bool=False) -> 'SampleCurve[MatrixSocket]':
            return SampleCurve(data_type='FLOAT4X4', curves=curves, value=value, length=length, curve_index=curve_index, mode='LENGTH', use_all_curves=use_all_curves)
    length: _SampleCurveLengthFactory = _SampleCurveLengthFactory()
    factor: _SampleCurveFactorFactory = _SampleCurveFactorFactory()
    _bl_idname = 'GeometryNodeSampleCurve'

    def __init__(self, curves: InputGeometry=None, value: InputAny=0.0, factor: InputFloat=0.0, length: InputFloat=0.0, curve_index: InputInteger=0, *, mode: Literal['FACTOR', 'LENGTH']='FACTOR', use_all_curves: bool=False, data_type: _SampleCurveDataTypes='FLOAT'):
        super().__init__()
        key_args = {'Curves': curves, 'Value': value, 'Factor': factor, 'Length': length, 'Curve Index': curve_index}
        self.mode = mode
        self.use_all_curves = use_all_curves
        self.data_type = data_type
        self._establish_links(**key_args)

    @property
    def mode(self) -> Literal['FACTOR', 'LENGTH']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['FACTOR', 'LENGTH']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def use_all_curves(self) -> bool:
        return self.node.use_all_curves

    @use_all_curves.setter
    def use_all_curves(self, value: bool) -> None:
        set_property(self.node, 'use_all_curves', value)

    @property
    def data_type(self) -> _SampleCurveDataTypes:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: _SampleCurveDataTypes) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SampleIndex(BaseNode):

    class _SampleIndexDomainFactory:

        def __init__(self, domain: _AttributeDomains):
            self._domain = domain

        def float(self, geometry: InputGeometry=None, value: InputFloat=0.0, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[FloatSocket]':
            return SampleIndex(data_type='FLOAT', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def integer(self, geometry: InputGeometry=None, value: InputInteger=0, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[IntegerSocket]':
            return SampleIndex(data_type='INT', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def boolean(self, geometry: InputGeometry=None, value: InputBoolean=False, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[BooleanSocket]':
            return SampleIndex(data_type='BOOLEAN', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def vector(self, geometry: InputGeometry=None, value: InputVector=None, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[VectorSocket]':
            return SampleIndex(data_type='FLOAT_VECTOR', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def color(self, geometry: InputGeometry=None, value: InputColor=None, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[ColorSocket]':
            return SampleIndex(data_type='FLOAT_COLOR', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def quaternion(self, geometry: InputGeometry=None, value: InputRotation=None, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[RotationSocket]':
            return SampleIndex(data_type='QUATERNION', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)

        def matrix(self, geometry: InputGeometry=None, value: InputMatrix=None, index: InputInteger=0, *, clamp: bool=False) -> 'SampleIndex[MatrixSocket]':
            return SampleIndex(data_type='FLOAT4X4', geometry=geometry, value=value, index=index, domain=self._domain, clamp=clamp)
    point: _SampleIndexDomainFactory = _SampleIndexDomainFactory('POINT')
    edge: _SampleIndexDomainFactory = _SampleIndexDomainFactory('EDGE')
    face: _SampleIndexDomainFactory = _SampleIndexDomainFactory('FACE')
    face_corner: _SampleIndexDomainFactory = _SampleIndexDomainFactory('CORNER')
    spline: _SampleIndexDomainFactory = _SampleIndexDomainFactory('CURVE')
    instance: _SampleIndexDomainFactory = _SampleIndexDomainFactory('INSTANCE')
    layer: _SampleIndexDomainFactory = _SampleIndexDomainFactory('LAYER')
    _bl_idname = 'GeometryNodeSampleIndex'

    def __init__(self, geometry: InputGeometry=None, value: InputAny=0.0, index: InputInteger=0, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT', domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER']='POINT', clamp: bool=False):
        super().__init__()
        key_args = {'Geometry': geometry, 'Value': value, 'Index': index}
        self.data_type = data_type
        self.domain = domain
        self.clamp = clamp
        self._establish_links(**key_args)

    @property
    def data_type(self) -> _SampleCurveDataTypes:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: _SampleCurveDataTypes) -> None:
        set_property(self.node, 'data_type', value)

    @property
    def domain(self) -> _AttributeDomains:
        return self.node.domain

    @domain.setter
    def domain(self, value: _AttributeDomains) -> None:
        set_property(self.node, 'domain', value)

    @property
    def clamp(self) -> bool:
        return self.node.clamp

    @clamp.setter
    def clamp(self, value: bool) -> None:
        set_property(self.node, 'clamp', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
