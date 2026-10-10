# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
BooleanResult = typing.TypeVar('BooleanResult')
FloatResult = typing.TypeVar('FloatResult')
IntegerResult = typing.TypeVar('IntegerResult')
MatrixResult = typing.TypeVar('MatrixResult')
RotationResult = typing.TypeVar('RotationResult')
StringResult = typing.TypeVar('StringResult')
T = typing.TypeVar('T')
TG = typing.TypeVar('TG')
VectorResult = typing.TypeVar('VectorResult')
NodeSocketFont = typing.Any
NodeSocketSound = typing.Any
from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, Self, cast, overload
import bpy
from bpy.types import GeometryNodeTree, Node, NodeLink, NodeSocket, NodeSocketBool, NodeSocketBundle, NodeSocketClosure, NodeSocketCollection, NodeSocketColor, NodeSocketFloat, NodeSocketGeometry, NodeSocketImage, NodeSocketInt, NodeSocketMaterial, NodeSocketMatrix, NodeSocketMenu, NodeSocketObject, NodeSocketRotation, NodeSocketShader, NodeSocketString, NodeSocketVector, NodeTree
from mathutils import Euler
from ..socket_types import SOCKET_TYPES, InputAny, InputBoolean, InputBundle, InputClosure, InputCollection, InputColor, InputFloat, InputFloatGrid, InputFloatList, InputFont, InputGeometry, InputImage, InputInteger, InputIntegerList, InputMaterial, InputMatrix, InputMenu, InputObject, InputRotation, InputSound, InputString, InputVector, InputVectorGrid
from ._registry import _SOCKET_GRID_REGISTRY, _SOCKET_LIST_REGISTRY, _SOCKET_REGISTRY
from ._utils import _deprecated, _NodeLike, _output_socket_type, _SocketLike
from .mixins import LinkingMixin, OperatorMixin
if TYPE_CHECKING:
    from ..nodes import compositor, geometry, shader
    from ..nodes.geometry import BoneInfo, CameraInfo, CombineMatrix, CombineTransform, FieldToGrid, GridInfo, GridToPoints, ImageInfo, IntegerMath, MatchString, Math, MultiplyMatrices, ObjectInfo, Position, Vector, VectorMath
    from .node import BaseNode
    from .tree import TreeBuilder

class ResultQuaternionComponents(NamedTuple):
    w: FloatResult
    x: FloatResult
    y: FloatResult
    z: FloatResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ResultAxisAngle(NamedTuple):
    axis: VectorResult
    angle: FloatResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ResultSpherical(NamedTuple):
    r: FloatResult
    phi: FloatResult
    theta: FloatResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ResultCylindrical(NamedTuple):
    r: FloatResult
    phi: FloatResult
    z: FloatResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ResultCollectionChildren(NamedTuple):
    collections: CollectionSocketList
    objects: ObjectSocketList

class ResultStringFind(NamedTuple):
    first_found: IntegerResult
    count: IntegerResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ResultMatrixSVD(NamedTuple):
    u: MatrixResult
    s: VectorResult
    v: MatrixResult

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class BaseSocket:

    def __init__(self, socket: NodeSocket):
        assert socket.node is not None
        self._tree = None
        self.socket = socket
        self._interface_socket: bpy.types.NodeTreeInterfaceSocket | None = None
        self._interface_identifier: str = ''
        self._builder_node: BaseNode | None = None

    def __bool__(self) -> bool:
        raise TypeError("The truth value of a socket is decided when the tree runs, not in Python, so it can't be used in `if`, `and`/`or`, `max()` or `min()`. Use .max()/.min() or a Switch node.")

    @property
    def node(self) -> Node:
        assert self.socket.node is not None
        return self.socket.node

    @property
    def links(self) -> list[NodeLink]:
        assert self.socket.links is not None
        return [link for link in self.socket.links]

    @property
    def _default_output_socket(self) -> NodeSocket:
        return self.socket

    @property
    def _default_input_socket(self) -> NodeSocket:
        return self.socket

    @property
    def type(self) -> SOCKET_TYPES:
        return self.socket.type

    @property
    def _socket_dtype(self) -> str:
        return self.socket.type.replace('VALUE', 'FLOAT')

    @property
    def name(self) -> str:
        return str(self.socket.name)

    def _assert_output(self, method: str) -> None:
        if hasattr(self, 'socket'):
            socket = self.socket
        else:
            socket = self._socket
        if not socket.is_output:
            raise RuntimeError(f"'{method}' is only available on output sockets, not input socket '{socket.name}'.")

    def _assert_input(self, method: str) -> None:
        if hasattr(self, 'socket'):
            socket = self.socket
        else:
            socket = self._socket
        if socket.is_output:
            raise RuntimeError(f"'{method}' is only available on input sockets, not output socket '{socket.name}'.")

    @property
    def _is_geometry_tree(self) -> bool:
        return self.tree.tree.bl_idname == 'GeometryNodeTree'

    @property
    def _is_shader_tree(self) -> bool:
        return self.tree.tree.bl_idname == 'ShaderNodeTree'

    @property
    def _is_compositor_tree(self) -> bool:
        return self.tree.tree.bl_idname == 'CompositorNodeTree'

    @property
    def tree(self) -> TreeBuilder[Any]:
        if self._tree is None:
            from .tree import TreeBuilder
            self._tree = TreeBuilder(cast(NodeTree, self.node.id_data))
        return self._tree

class Socket(BaseSocket, _SocketLike, OperatorMixin, LinkingMixin):
    if TYPE_CHECKING:

        def __mul__(self, other: Any) -> Self:
            ...

        def __rmul__(self, other: Any) -> Self:
            ...

        def __truediv__(self, other: Any) -> Self:
            ...

        def __rtruediv__(self, other: Any) -> Self:
            ...

        def __add__(self, other: Any) -> Self:
            ...

        def __radd__(self, other: Any) -> Self:
            ...

        def __sub__(self, other: Any) -> Self:
            ...

        def __rsub__(self, other: Any) -> Self:
            ...

        def __pow__(self, other: Any) -> Self:
            ...

        def __rpow__(self, other: Any) -> Self:
            ...

        def __mod__(self, other: Any) -> Self:
            ...

        def __rmod__(self, other: Any) -> Self:
            ...

        def __floordiv__(self, other: Any) -> Self:
            ...

        def __rfloordiv__(self, other: Any) -> Self:
            ...

        def __neg__(self) -> Self:
            ...

        def __abs__(self) -> Self:
            ...

    @property
    def builder_node(self) -> BaseNode:
        assert self._builder_node is not None
        return self._builder_node

    def enable_output(self, enable: InputBoolean=True) -> Self:
        from ..nodes.geometry import EnableOutput
        if self.socket.is_output:
            return EnableOutput(enable, self.socket, data_type=self._socket_dtype).o.value
        else:
            enable = EnableOutput(enable, None, data_type=self._socket_dtype)
            enable >> self.socket
            return enable.i.value

    def _dispatch_math(self, other: Any, operation: str, reverse: bool=False) -> Socket:
        from ..nodes.geometry.converter import Math
        if isinstance(other, (list, tuple)) and len(other) == 3:
            if operation == 'multiply':
                from ..nodes.geometry import VectorMath
                return VectorMath.scale(other, self.socket).o.vector
            return _dispatch_vector_math(self.socket, other, operation, reverse)
        values = (self.socket, other) if not reverse else (other, self.socket)
        math_operation = 'floored_modulo' if operation == 'modulo' else operation
        return getattr(Math, math_operation)(*values).o.value

    def _dispatch_unary(self, operation: str) -> Socket:
        from ..nodes.geometry.converter import Math
        if operation == 'negate':
            return Math.multiply(self.socket, -1).o.value
        elif operation == 'absolute':
            return Math.absolute(self.socket).o.value
        raise ValueError(f'Unknown unary operation: {operation}')

    def _dispatch_floordiv(self, other: Any, reverse: bool=False) -> Socket:
        from ..nodes.geometry.converter import Math
        values = (self.socket, other) if not reverse else (other, self.socket)
        divided = Math.divide(*values)
        return Math.floor(divided).o.value

    def _dispatch_compare(self, other: Any, operation: str) -> FloatSocket | BooleanSocket:
        if isinstance(self.tree.tree, GeometryNodeTree):
            from ..nodes.geometry.manual import Compare
            return cast(Compare, getattr(Compare.float, operation)(self.socket, other)).o.result
        else:
            from ..nodes.geometry.converter import Math
            _MATH_COMPARE_MAP = {'less_than': ('less_than', False), 'greater_than': ('greater_than', False), 'less_equal': ('greater_than', True), 'greater_equal': ('less_than', True), 'equal': ('compare', False), 'not_equal': ('compare', True)}
            math_op, negate = _MATH_COMPARE_MAP[operation]
            result = getattr(Math, math_op)(self.socket, other).o.value
            if operation in ('equal', 'not_equal'):
                result.builder_node.i.value_002.default_value = 1e-05
            if negate:
                result = Math.subtract(1.0, result._default_output_socket).o.value
            return result
    if TYPE_CHECKING:

        def __add__(self, other: Any) -> Self:
            ...

        def __radd__(self, other: Any) -> Self:
            ...

        def __sub__(self, other: Any) -> Self:
            ...

        def __rsub__(self, other: Any) -> Self:
            ...

        def __mul__(self, other: Any) -> Self:
            ...

        def __rmul__(self, other: Any) -> Self:
            ...

        def __div__(self, other: Any) -> Self:
            ...

        def __rdiv__(self, other: Any) -> Self:
            ...

        def __truediv__(self, other: Any) -> Self:
            ...

        def __rtruediv__(self, other: Any) -> Self:
            ...

        def __floordiv__(self, other: Any) -> Self:
            ...

        def __rfloordiv__(self, other: Any) -> Self:
            ...

        def __neg__(self) -> Self:
            ...

        def __abs__(self) -> Self:
            ...

        def __lt__(self, other: Any) -> BooleanSocket:
            ...

        def __gt__(self, other: Any) -> BooleanSocket:
            ...

        def __le__(self, other: Any) -> BooleanSocket:
            ...

        def __ge__(self, other: Any) -> BooleanSocket:
            ...

        def __eq__(self, other: object) -> BooleanSocket:
            ...

        def __ne__(self, other: object) -> BooleanSocket:
            ...

class _GridMeanMixin(Socket):

    def mean(self, width: InputInteger=1, iterations: InputInteger=1) -> Self:
        from ..nodes.geometry import GridMean
        return GridMean(self.socket, width=width, iterations=iterations, data_type=self._socket_dtype).o.grid

    def median(self, width: InputInteger=1, iterations: InputInteger=1) -> Self:
        from ..nodes.geometry import GridMedian
        return GridMedian(self.socket, width=width, iterations=iterations, data_type=self._socket_dtype).o.grid

class _GridAdvectMixin(Socket):

    def advect(self, velocity: InputVectorGrid, time_step: InputFloat=1.0, integration_scheme: InputMenu | Literal['Semi-Lagrangian', 'Midpoint', 'Runge-Kutta 3', 'Runge-Kutta 4', 'MacCormack', 'BFECC']='Runge-Kutta 3', limiter: InputMenu | Literal['None', 'Clamp', 'Revert']='Clamp') -> Self:
        from ..nodes.geometry import AdvectGrid
        return AdvectGrid(self.socket, velocity, time_step, integration_scheme, limiter, data_type=self._socket_dtype).o.grid

class _FloatGridOperatorMixin(Socket):

    def gradient(self) -> VectorSocketGrid:
        from ..nodes.geometry import GridGradient
        return GridGradient(self.socket).o.gradient

    def laplacian(self) -> FloatSocketGrid:
        from ..nodes.geometry import GridLaplacian
        return GridLaplacian(self.socket).o.laplacian

    def sdf_fillet(self, iterations: InputInteger=1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridFillet
        return SDFGridFillet(self.socket, iterations=iterations).o.grid

    def sdf_laplacian(self, iterations: InputInteger=1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridLaplacian
        return SDFGridLaplacian(self.socket, iterations=iterations).o.grid

    def sdf_mean(self, width: InputInteger=1, iterations: InputInteger=1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridMean
        return SDFGridMean(self.socket, width=width, iterations=iterations).o.grid

    def sdf_mean_curvature(self, iterations: InputInteger=1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridMeanCurvature
        return SDFGridMeanCurvature(self.socket, iterations=iterations).o.grid

    def sdf_median(self, width: InputInteger=1, iterations: InputInteger=1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridMedian
        return SDFGridMedian(self.socket, width=width, iterations=iterations).o.grid

    def sdf_offset(self, distance: InputFloat=0.1) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridOffset
        return SDFGridOffset(self.socket, distance=distance).o.grid

    def sdf_union(self, *others: InputFloatGrid) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridBoolean
        return SDFGridBoolean.union([self.socket, *others]).o.grid

    def sdf_intersect(self, *others: InputFloatGrid) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridBoolean
        return SDFGridBoolean.intersect([self.socket, *others]).o.grid

    def sdf_difference(self, *others: InputFloatGrid) -> FloatSocketGrid:
        from ..nodes.geometry import SDFGridBoolean
        return SDFGridBoolean.difference(self.socket, others).o.grid

    def to_mesh(self, threshold: InputFloat=0.1, adaptivity: InputFloat=0.0) -> GeometrySocket:
        from ..nodes.geometry import GridToMesh
        return GridToMesh(self.socket, threshold=threshold, adaptivity=adaptivity).o.mesh

class _VectorGridOperatorMixin(Socket):

    def curl(self) -> VectorSocketGrid:
        from ..nodes.geometry import GridCurl
        return GridCurl(self.socket).o.curl

    def divergence(self) -> FloatSocketGrid:
        from ..nodes.geometry import GridDivergence
        return GridDivergence(self.socket).o.divergence

class _GridSocketMixin(Socket):

    def _info(self) -> GridInfo[T, TG]:
        from ..nodes.geometry import GridInfo
        self._assert_output('transform / background_value')
        for link in self.socket.links or ():
            assert link.to_node
            if link.to_node.bl_idname == GridInfo._bl_idname:
                return GridInfo._from_node(link.to_node)
        dtype = self.socket.type.replace('VALUE', 'FLOAT')
        return GridInfo(self.socket, data_type=dtype)

    @property
    def transform(self) -> MatrixSocket:
        return self._info().o.transform

    @property
    def background_value(self) -> T:
        return self._info().o.background_value

    def set_background(self, background: InputAny, update_inactive: InputBoolean=False) -> Self:
        from ..nodes.geometry import SetGridBackground
        return SetGridBackground(self.socket, background, update_inactive, data_type=self._socket_dtype).o.grid

    def set_transform(self, matrix: InputMatrix) -> Self:
        from ..nodes.geometry import SetGridTransform
        return SetGridTransform(self.socket, matrix, data_type=self._socket_dtype).o.grid

    def sample(self, position: InputVector=None, interpolation: Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear') -> T:
        from ..nodes.geometry import SampleGrid
        return SampleGrid(grid=self.socket, position=position, interpolation=interpolation, data_type=self._socket_dtype).o.value

    def sample_index(self, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0) -> T:
        from ..nodes.geometry import SampleGridIndex
        return SampleGridIndex(grid=self.socket, x=x, y=y, z=z, data_type=self._socket_dtype).o.value

    def field_to_grid(self) -> FieldToGrid[TG]:
        from ..nodes.geometry import FieldToGrid
        return FieldToGrid(topology=self.socket, data_type=self._socket_dtype)

    def clip(self, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32) -> Self:
        from ..nodes.geometry import ClipGrid
        return ClipGrid(grid=self.socket, min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, data_type=self._socket_dtype).o.grid

    def dilate_erode(self, steps: InputInteger=1, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve') -> Self:
        from ..nodes.geometry import GridDilateErode
        return GridDilateErode(grid=self.socket, connectivity=connectivity, tiles=tiles, steps=steps, data_type=self._socket_dtype).o.grid

    def prune(self, threshold: InputFloat=0.1, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']=None) -> Self:
        from ..nodes.geometry import PruneGrid
        return PruneGrid(grid=self.socket, threshold=threshold, mode=mode, data_type=self._socket_dtype).o.grid

    def voxelize(self) -> Self:
        from ..nodes.geometry import VoxelizeGrid
        return VoxelizeGrid(grid=self.socket, data_type=self._socket_dtype).o.grid

    def to_points(self) -> GridToPoints[T, TG]:
        from ..nodes.geometry import GridToPoints
        return GridToPoints(grid=self.socket, data_type=self._socket_dtype)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _EvaluateField(Socket):

    def __init__(self, socket: NodeSocket, dtype: str, domain: str) -> None:
        self._socket = socket
        self._assert_output('Domain-specific evaluation')
        self._dtype = dtype
        self._domain = domain

    def evaluate(self) -> T:
        from ..nodes.geometry import EvaluateOnDomain
        return getattr(getattr(EvaluateOnDomain, self._domain), self._dtype)(self._socket).o.value

    def at(self, index: InputInteger=0) -> T:
        from ..nodes.geometry import EvaluateAtIndex
        return getattr(getattr(EvaluateAtIndex, self._domain), self._dtype)(self._socket, index).o.value

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _AccumulateField(_EvaluateField):

    def _accumulate(self, output: Literal['leading', 'trailing', 'total'], group_index: InputInteger) -> T:
        from ..nodes.geometry import AccumulateField
        node = getattr(getattr(AccumulateField, self._domain), self._dtype.replace('matrix', 'transform'))(self._socket, group_index)
        return getattr(node.o, output)

    def leading(self, group_index: InputInteger=None) -> T:
        return self._accumulate('leading', group_index)

    def trailing(self, group_index: InputInteger=None) -> T:
        return self._accumulate('trailing', group_index)

    def total(self, group_index: InputInteger=None) -> T:
        return self._accumulate('total', group_index)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _MinMaxField(_AccumulateField):

    def _minmax(self, output: str, group_index: InputInteger) -> T:
        from ..nodes.geometry import FieldMinAndMax
        node = getattr(getattr(FieldMinAndMax, self._domain), self._dtype)(self._socket, group_index)
        return getattr(node.o, output)

    def min(self, group_index: InputInteger=None) -> T:
        return self._minmax('min', group_index)

    def max(self, group_index: InputInteger=None) -> T:
        return self._minmax('max', group_index)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _StatsField(_MinMaxField):

    def mean(self, group_index: InputInteger=None) -> T:
        from ..nodes.geometry import FieldAverage
        node = getattr(getattr(FieldAverage, self._domain), self._dtype)(self._socket, group_index)
        return node.o.mean

    def median(self, group_index: InputInteger=None) -> T:
        from ..nodes.geometry import FieldAverage
        node = getattr(getattr(FieldAverage, self._domain), self._dtype)(self._socket, group_index)
        return node.o.median

    def std_dev(self, group_index: InputInteger=None) -> T:
        from ..nodes.geometry import FieldVariance
        node = getattr(getattr(FieldVariance, self._domain), self._dtype)(self._socket, group_index)
        return node.o.standard_deviation

    def variance(self, group_index: InputInteger=None) -> T:
        from ..nodes.geometry import FieldVariance
        node = getattr(getattr(FieldVariance, self._domain), self._dtype)(self._socket, group_index)
        return node.o.variance

    @classmethod
    def __class_getitem__(cls, item):
        return cls

def _dispatch_vector_math(socket: NodeSocket, other: Any, operation: str, reverse: bool=False) -> VectorSocket:
    from ..nodes.geometry import VectorMath
    values = (socket, other) if not reverse else (other, socket)
    if operation == 'multiply':
        if isinstance(other, (int, float)):
            return VectorMath.scale(socket, other).o.vector
        if _output_socket_type(other) in ('VALUE', 'FLOAT', 'INT'):
            scale_by = other if isinstance(other, NodeSocket) else other._default_output_socket
            return VectorMath.scale(socket, scale_by).o.vector
        if isinstance(other, (list, tuple)) and len(other) == 3:
            return VectorMath.multiply(*values).o.vector
        if isinstance(other, (_SocketLike, _NodeLike, NodeSocket)):
            return VectorMath.multiply(*values).o.vector
        raise TypeError(f'Unsupported operand for multiply with a vector/colour socket: {type(other)}')
    method = getattr(VectorMath, operation)
    if isinstance(other, (int, float)):
        scalar_vector = (other, other, other)
        node = method(socket, scalar_vector) if not reverse else method(scalar_vector, socket)
        return node.o.vector
    if isinstance(other, (list, tuple)) and len(other) == 3 or isinstance(other, (_SocketLike, _NodeLike, NodeSocket)):
        return method(*values).o.vector
    raise TypeError(f'Unsupported operand for {operation} with a vector/colour socket: {type(other)}')

def _dispatch_vector_unary(socket: NodeSocket, operation: str) -> VectorSocket:
    from ..nodes.geometry import VectorMath
    if operation == 'negate':
        return VectorMath.scale(socket, -1).o.vector
    if operation == 'absolute':
        return VectorMath.absolute(socket).o.vector
    raise ValueError(f'Unknown unary operation: {operation}')

def _dispatch_vector_floordiv(socket: NodeSocket, other: Any, reverse: bool=False) -> VectorSocket:
    from ..nodes.geometry import VectorMath
    divided = _dispatch_vector_math(socket, other, 'divide', reverse)
    return VectorMath.floor(divided).o.vector

def _dispatch_vector_compare(self: BaseSocket, other: Any, operation: str) -> BooleanSocket | FloatSocket:
    if self._is_geometry_tree:
        from ..nodes.geometry import Compare
        return getattr(Compare.vector, operation)(self.socket, other).o.result
    return Socket._dispatch_compare(cast('Socket', self), other, operation)

class _HashMixin(BaseSocket):

    def hash(self, seed: InputInteger=0) -> IntegerSocket:
        self._assert_output('hash')
        from ..nodes.geometry import HashValue
        return HashValue(self.socket, seed, data_type=self._socket_dtype).o.hash
_BLUR_DATA_TYPES = {'VALUE': 'FLOAT', 'INT': 'INT', 'VECTOR': 'FLOAT_VECTOR', 'RGBA': 'FLOAT_COLOR'}

class _BlurMixin(BaseSocket):

    def blur(self, iterations: InputInteger=1, weight: InputFloat=1.0) -> Self:
        self._assert_output('blur')
        from ..nodes.geometry import BlurAttribute
        return BlurAttribute(self.socket, iterations, weight, data_type=_BLUR_DATA_TYPES[self.socket.type]).o.value

class _VectorMixin(_HashMixin, _BlurMixin, BaseSocket):
    socket: NodeSocketVector
    _tree: TreeBuilder[Any]

    @property
    def _vmath(self) -> type[VectorMath]:
        from ..nodes.geometry import VectorMath
        return VectorMath

    def _separate(self) -> geometry.SeparateXYZ:
        from ..nodes.geometry import SeparateXYZ
        return SeparateXYZ._find_or_create_linked(self.socket)

    def _combine(self) -> geometry.CombineXYZ:
        from ..nodes.geometry import CombineXYZ
        return CombineXYZ._find_or_create_linked(self.socket)

    @property
    def x(self) -> FloatResult:
        if self.socket.is_output:
            return self._separate().o.x
        else:
            return self._combine().i.x

    @property
    def y(self) -> FloatResult:
        if self.socket.is_output:
            return self._separate().o.y
        else:
            return self._combine().i.y

    @property
    def z(self) -> FloatResult:
        if self.socket.is_output:
            return self._separate().o.z
        else:
            return self._combine().i.z

    def dot(self, vector: InputVector=(0.0, 0.0, 1.0)) -> FloatResult:
        self._assert_output('dot')
        return self._vmath.dot_product(self.socket, vector).o.value

    def scale(self, scale: InputFloat) -> VectorResult:
        self._assert_output('scale')
        return self._vmath.scale(self.socket, scale).o.vector

    def mul_add(self, multiplier: InputVector, addend: InputVector) -> VectorResult:
        self._assert_output('mul_add')
        return self._vmath.multiply_add(self.socket, multiplier, addend).o.vector

    def min(self, value: InputVector) -> VectorResult:
        self._assert_output('min')
        return self._vmath.minimum(self.socket, value).o.vector

    def max(self, value: InputVector) -> VectorResult:
        self._assert_output('max')
        return self._vmath.maximum(self.socket, value).o.vector

    def floor(self) -> VectorResult:
        self._assert_output('floor')
        return self._vmath.floor(self.socket).o.vector

    def ceil(self) -> VectorResult:
        self._assert_output('ceil')
        return self._vmath.ceil(self.socket).o.vector

    def round(self) -> VectorResult:
        self._assert_output('round')
        return self._vmath.round(self.socket).o.vector

    def fraction(self) -> VectorResult:
        self._assert_output('fraction')
        return self._vmath.fraction(self.socket).o.vector

    def sign(self) -> VectorResult:
        self._assert_output('sign')
        return self._vmath.sign(self.socket).o.vector

    def snap(self, increment: InputVector) -> VectorResult:
        self._assert_output('snap')
        return self._vmath.snap(self.socket, increment).o.vector

    def wrap(self, min: InputVector, max: InputVector) -> VectorResult:
        self._assert_output('wrap')
        return self._vmath.wrap(self.socket, vector_001=max, vector_002=min).o.vector

    def sin(self) -> VectorResult:
        self._assert_output('sin')
        return self._vmath.sine(self.socket).o.vector

    def cos(self) -> VectorResult:
        self._assert_output('cos')
        return self._vmath.cosine(self.socket).o.vector

    def tan(self) -> VectorResult:
        self._assert_output('tan')
        return self._vmath.tangent(self.socket).o.vector

    def faceforward(self, incident: InputVector, reference: InputVector) -> VectorResult:
        self._assert_output('faceforward')
        return self._vmath.faceforward(self.socket, incident, reference).o.vector

    def refract(self, normal: InputVector, ior: InputFloat) -> VectorResult:
        self._assert_output('refract')
        return self._vmath.refract(self.socket, normal, ior).o.vector

    def to_spherical(self) -> ResultSpherical[FloatResult]:
        self._assert_output('to_spherical')
        from ..nodes.geometry import SeparateSpherical
        node = SeparateSpherical(self.socket)
        return ResultSpherical(node.o.r, node.o.phi, node.o.theta)

    def to_cylindrical(self) -> ResultCylindrical[FloatResult]:
        self._assert_output('to_cylindrical')
        from ..nodes.geometry import SeparateCylindrical
        node = SeparateCylindrical(self.socket)
        return ResultCylindrical(node.o.r, node.o.phi, node.o.z)

    def project_point(self, matrix: InputMatrix) -> VectorResult:
        self._assert_output('project_point')
        from ..nodes.geometry import ProjectPoint
        return ProjectPoint(self.socket, matrix).o.vector

    def euler_to_rotation(self) -> RotationResult:
        self._assert_output('euler_to_rotation')
        from ..nodes.geometry import EulerToRotation
        return EulerToRotation(self.socket).o.rotation

    def length(self) -> FloatResult:
        self._assert_output('length')
        return self._vmath.length(self.socket).o.value

    def normalize(self) -> VectorResult:
        self._assert_output('normalize')
        return self._vmath.normalize(self.socket).o.vector

    def cross(self, other: InputVector=(0.0, 0.0, 1.0)) -> VectorResult:
        self._assert_output('cross')
        return self._vmath.cross_product(self.socket, other).o.vector

    def distance(self, other: InputVector=(0.0, 0.0, 0.0)) -> FloatResult:
        self._assert_output('distance')
        return self._vmath.distance(self.socket, other).o.value

    def project(self, other: InputVector=(0.0, 0.0, 0.0)) -> VectorResult:
        self._assert_output('project')
        return self._vmath.project(self.socket, other).o.vector

    def reflect(self, normal: InputVector=(0.0, 0.0, 1.0)) -> VectorResult:
        self._assert_output('reflect')
        return self._vmath.reflect(self.socket, normal).o.vector

    def map_range(self, from_min: InputVector=(0.0, 0.0, 0.0), from_max: InputVector=(1.0, 1.0, 1.0), to_min: InputVector=(0.0, 0.0, 0.0), to_max: InputVector=(1.0, 1.0, 1.0), *, clamp: bool=True, interpolation_type: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']='LINEAR', steps: InputVector=(4.0, 4.0, 4.0)) -> VectorResult:
        self._assert_output('map_range')
        from ..nodes.geometry import MapRange
        node = MapRange.vector(self.socket, from_min, from_max, to_min, to_max)
        node.clamp = clamp
        node.interpolation_type = interpolation_type
        if interpolation_type == 'STEPPED':
            kwargs = {'Steps_FLOAT3': steps}
            node._establish_links(**kwargs)
        return node.o.vector

    def align_rotation(self, rotation: InputRotation=None, factor: InputFloat=1.0, *, axis: Literal['X', 'Y', 'Z']='Z', pivot_axis: Literal['AUTO', 'X', 'Y', 'Z']='AUTO') -> RotationResult:
        from ..nodes.geometry import AlignRotationToVector
        return AlignRotationToVector(rotation=rotation, factor=factor, vector=self.socket, axis=axis, pivot_axis=pivot_axis).o.rotation

    def rotate(self, rotation: InputRotation) -> VectorResult:
        self._assert_output('rotate')
        from ..nodes.geometry import RotateVector
        return RotateVector(self.socket, rotation).o.vector

    def transform(self, matrix: InputMatrix) -> VectorResult:
        self._assert_output('transform')
        from ..nodes.geometry import TransformPoint
        return TransformPoint(self.socket, matrix).o.vector

    def transform_direction(self, matrix: InputMatrix) -> VectorResult:
        self._assert_output('transform_direction')
        from ..nodes.geometry import TransformDirection
        return TransformDirection(self.socket, matrix).o.direction

    @overload
    def __rmatmul__(self, other: CombineTransform) -> VectorResult:
        ...

    @overload
    def __rmatmul__(self, other: MultiplyMatrices) -> VectorResult:
        ...

    @overload
    def __rmatmul__(self, other: CombineMatrix) -> VectorResult:
        ...

    @overload
    def __rmatmul__(self, other: MatrixSocket) -> VectorResult:
        ...

    def __rmatmul__(self, other: CombineTransform | MultiplyMatrices | CombineMatrix | MatrixSocket) -> VectorResult:
        from ..nodes.geometry import TransformPoint
        return TransformPoint(self.socket, other).o.vector

    @overload
    def __getitem__(self, key: slice) -> list[FloatResult]:
        ...

    @overload
    def __getitem__(self, key: int) -> FloatResult:
        ...

    def __getitem__(self, key: int | slice) -> FloatResult | list[FloatResult]:
        if self.socket.is_output:
            node = self._separate()
            return [node.o.x, node.o.y, node.o.z][key]
        else:
            node = self._combine()
            return [node.i.x, node.i.y, node.i.z][key]

    def __iter__(self) -> Iterator[FloatResult]:
        if self.socket.is_output:
            node = self._separate()
            yield node.o.x
            yield node.o.y
            yield node.o.z
        else:
            node = self._combine()
            yield node.i.x
            yield node.i.y
            yield node.i.z

    def __len__(self) -> int:
        return 3

    def _dispatch_unary(self, operation: str) -> VectorResult:
        return _dispatch_vector_unary(self.socket, operation)

    def _dispatch_math(self, other: Any, operation: str, reverse: bool=False) -> VectorResult:
        return _dispatch_vector_math(self.socket, other, operation, reverse)

    def _dispatch_floordiv(self, other: Any, reverse: bool=False) -> VectorResult:
        return _dispatch_vector_floordiv(self.socket, other, reverse)

    def _dispatch_compare(self, other: Any, operation: str) -> BooleanSocket | FloatSocket:
        return _dispatch_vector_compare(self, other, operation)
    if TYPE_CHECKING:

        def scale(self, scale: InputFloat) -> Self:
            ...

        def mul_add(self, multiplier: InputVector, addend: InputVector) -> Self:
            ...

        def min(self, value: InputVector) -> Self:
            ...

        def max(self, value: InputVector) -> Self:
            ...

        def floor(self) -> Self:
            ...

        def ceil(self) -> Self:
            ...

        def round(self) -> Self:
            ...

        def fraction(self) -> Self:
            ...

        def sign(self) -> Self:
            ...

        def snap(self, increment: InputVector) -> Self:
            ...

        def wrap(self, min: InputVector, max: InputVector) -> Self:
            ...

        def sin(self) -> Self:
            ...

        def cos(self) -> Self:
            ...

        def tan(self) -> Self:
            ...

        def faceforward(self, incident: InputVector, reference: InputVector) -> Self:
            ...

        def refract(self, normal: InputVector, ior: InputFloat) -> Self:
            ...

        def project_point(self, matrix: InputMatrix) -> Self:
            ...

        def normalize(self) -> Self:
            ...

        def cross(self, other: InputVector) -> Self:
            ...

        def project(self, other: InputVector) -> Self:
            ...

        def reflect(self, normal: InputVector) -> Self:
            ...

        def map_range(self, *args: Any, **kwargs: Any) -> Self:
            ...

        def rotate(self, rotation: InputRotation) -> Self:
            ...

        def transform(self, matrix: InputMatrix) -> Self:
            ...

        def transform_direction(self, matrix: InputMatrix) -> Self:
            ...

        def _dispatch_unary(self, operation: str) -> Self:
            ...

        def _dispatch_math(self, other: Any, operation: str, reverse: bool=...) -> Self:
            ...

        def _dispatch_floordiv(self, other: Any, reverse: bool=...) -> Self:
            ...

        def __add__(self, other: Any) -> Self:
            ...

        def __radd__(self, other: Any) -> Self:
            ...

        def __sub__(self, other: Any) -> Self:
            ...

        def __rsub__(self, other: Any) -> Self:
            ...

        def __mul__(self, other: Any) -> Self:
            ...

        def __rmul__(self, other: Any) -> Self:
            ...

        def __truediv__(self, other: Any) -> Self:
            ...

        def __rtruediv__(self, other: Any) -> Self:
            ...

        def __floordiv__(self, other: Any) -> Self:
            ...

        def __rfloordiv__(self, other: Any) -> Self:
            ...

        def __neg__(self) -> Self:
            ...

        def __abs__(self) -> Self:
            ...

        def __lt__(self, other: Any) -> BooleanSocket:
            ...

        def __gt__(self, other: Any) -> BooleanSocket:
            ...

        def __le__(self, other: Any) -> BooleanSocket:
            ...

        def __ge__(self, other: Any) -> BooleanSocket:
            ...

    @classmethod
    def __class_getitem__(cls, item):
        return cls
_COLOR_BLEND_TYPES: dict[str, Literal['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']] = {'add': 'ADD', 'subtract': 'SUBTRACT', 'multiply': 'MULTIPLY', 'divide': 'DIVIDE'}

class _ColorMixin(_HashMixin, _BlurMixin, BaseSocket):
    socket: NodeSocketColor

    def _separated_channel(self) -> geometry.SeparateColor | shader.SeparateColor | compositor.SeparateColor:
        assert self.socket.links is not None
        tree_type = self.tree.tree.bl_idname
        if tree_type == 'ShaderNodeTree':
            from ..nodes.shader import SeparateColor
            sep = SeparateColor._find_or_create_linked(self.socket)
        elif tree_type == 'CompositorNodeTree':
            from ..nodes.compositor import SeparateColor
            sep = SeparateColor._find_or_create_linked(self.socket)
        else:
            from ..nodes.geometry import SeparateColor
            sep = SeparateColor._find_or_create_linked(self.socket)
        return sep

    def _combine_color(self) -> shader.CombineColor | compositor.CombineColor | geometry.CombineColor:
        if self.tree.tree.bl_idname == 'CompositorNodeTree':
            from ..nodes.compositor import CombineColor
            combine = CombineColor._find_or_create_linked(self.socket)
        elif self.tree.tree.bl_idname == 'ShaderNodeTree':
            from ..nodes.shader import CombineColor
            combine = CombineColor._find_or_create_linked(self.socket)
        else:
            from ..nodes.geometry import CombineColor
            combine = CombineColor._find_or_create_linked(self.socket)
        assert combine.node.outputs is not None
        self.tree.link(combine.node.outputs[0], self.socket)
        return combine

    @property
    def r(self) -> FloatSocket:
        if self.socket.is_output:
            return self._separated_channel().o.red
        else:
            return self._combine_color().i.red

    @property
    def g(self) -> FloatSocket:
        if self.socket.is_output:
            return self._separated_channel().o.green
        else:
            return self._combine_color().i.green

    @property
    def b(self) -> FloatSocket:
        if self.socket.is_output:
            return self._separated_channel().o.blue
        else:
            return self._combine_color().i.blue

    @property
    def a(self) -> FloatSocket:
        from ..nodes import shader
        if self.socket.is_output:
            node = self._separated_channel()
            if isinstance(node, shader.SeparateColor):
                raise TypeError("Shader SeparateColor node doesn't have an alpha output")
            return node.o.alpha
        else:
            node = self._combine_color()
            if isinstance(node, shader.CombineColor):
                raise TypeError("Shader CombineColor node doesn't have an alpha input")
            return node.i.alpha

    @property
    def default_value(self) -> list[float]:
        return list(self.socket.default_value)

    @default_value.setter
    def default_value(self, value: list[float]) -> None:
        self.socket.default_value = value

    @property
    def point(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'point')

    @property
    def edge(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'edge')

    @property
    def face(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'face')

    @property
    def corner(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'corner')

    @property
    def spline(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'spline')

    @property
    def instance(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'instance')

    @property
    def layer(self) -> _EvaluateField[ColorSocket]:
        return _EvaluateField(self.socket, 'color', 'layer')

    @overload
    def __getitem__(self, key: slice) -> list[FloatSocket]:
        ...

    @overload
    def __getitem__(self, key: int) -> FloatSocket:
        ...

    def __getitem__(self, key: int | slice) -> FloatSocket | list[FloatSocket]:
        if self._is_shader_tree:
            return [self.r, self.g, self.b][key]
        else:
            return [self.r, self.g, self.b, self.a][key]

    def __iter__(self) -> Iterator[FloatSocket]:
        yield self.r
        yield self.g
        yield self.b
        if not self._is_shader_tree:
            yield self.a

    def __len__(self) -> int:
        if self._is_shader_tree:
            return 3
        else:
            return 4

    def gamma(self, gamma: InputFloat) -> ColorSocket:
        self._assert_output('gamma')
        from ..nodes.geometry import Gamma
        return Gamma(self.socket, gamma).o.color

    def _dispatch_math(self, other: Any, operation: str, reverse: bool=False) -> ColorSocket | VectorSocket:
        blend_type = _COLOR_BLEND_TYPES.get(operation)
        is_color = _output_socket_type(other) == 'RGBA' or (isinstance(other, (list, tuple)) and len(other) == 4)
        if blend_type is None or not is_color:
            return _dispatch_vector_math(self.socket, other, operation, reverse)
        from ..nodes.geometry import Mix
        a, b = (other, self.socket) if reverse else (self.socket, other)
        return Mix(1.0, a_color=a, b_color=b, data_type='RGBA', blend_type=blend_type).o.result_color

    def _dispatch_unary(self, operation: str) -> VectorSocket:
        return _dispatch_vector_unary(self.socket, operation)

    def _dispatch_floordiv(self, other: Any, reverse: bool=False) -> VectorSocket:
        return _dispatch_vector_floordiv(self.socket, other, reverse)

    def _dispatch_compare(self, other: Any, operation: str) -> BooleanSocket | FloatSocket:
        return _dispatch_vector_compare(self, other, operation)

class _BooleanSwitchSocketFactory:

    def __init__(self, socket: NodeSocketBool):
        self._socket = socket
        from ..nodes.geometry import Switch
        self._switch = Switch

    def float(self, false: InputFloat=None, true: InputFloat=None) -> FloatSocket:
        return self._switch.float(self._socket, false, true).o.output

    def integer(self, false: InputInteger=None, true: InputInteger=None) -> IntegerSocket:
        return self._switch.integer(self._socket, false, true).o.output

    def boolean(self, false: InputBoolean=None, true: InputBoolean=None) -> BooleanSocket:
        return self._switch.boolean(self._socket, false, true).o.output

    def vector(self, false: InputVector=None, true: InputVector=None) -> VectorSocket:
        return self._switch.vector(self._socket, false, true).o.output

    def color(self, false: InputColor=None, true: InputColor=None) -> ColorSocket:
        return self._switch.color(self._socket, false, true).o.output

    def rotation(self, false: InputRotation=None, true: InputRotation=None) -> RotationSocket:
        return self._switch.rotation(self._socket, false, true).o.output

    def matrix(self, false: InputMatrix=None, true: InputMatrix=None) -> MatrixSocket:
        return self._switch.matrix(self._socket, false, true).o.output

    def string(self, false: InputString=None, true: InputString=None) -> StringSocket:
        return self._switch.string(self._socket, false, true).o.output

    def menu(self, false: InputMenu=None, true: InputMenu=None) -> MenuSocket:
        return self._switch.menu(self._socket, false, true).o.output

    def object(self, false: InputObject=None, true: InputObject=None) -> ObjectSocket:
        return self._switch.object(self._socket, false, true).o.output

    def image(self, false: InputImage=None, true: InputImage=None) -> ImageSocket:
        return self._switch.image(self._socket, false, true).o.output

    def geometry(self, false: InputGeometry=None, true: InputGeometry=None) -> GeometrySocket:
        return self._switch.geometry(self._socket, false, true).o.output

    def collection(self, false: InputCollection=None, true: InputCollection=None) -> CollectionSocket:
        return self._switch.collection(self._socket, false, true).o.output

    def material(self, false: InputMaterial=None, true: InputMaterial=None) -> MaterialSocket:
        return self._switch.material(self._socket, false, true).o.output

    def bundle(self, false: InputBundle=None, true: InputBundle=None) -> BundleSocket:
        return self._switch.bundle(self._socket, false, true).o.output

    def closure(self, false: InputClosure=None, true: InputClosure=None) -> ClosureSocket:
        return self._switch.closure(self._socket, false, true).o.output

    def font(self, false: InputFont=None, true: InputFont=None) -> FontSocket:
        return self._switch.font(self._socket, false, true).o.output

    def sound(self, false: InputSound=None, true: InputSound=None) -> SoundSocket:
        return self._switch.sound(self._socket, false, true).o.output

class _BooleanMixin(BaseSocket):
    socket: NodeSocketBool

    def __or__(self, other: Any) -> Self:
        self._assert_output('|')
        from ..nodes.geometry.converter import BooleanMath
        return BooleanMath.l_or(self.socket, other).o.boolean

    def __and__(self, other: Any) -> Self:
        self._assert_output('&')
        from ..nodes.geometry.converter import BooleanMath
        return BooleanMath.l_and(self.socket, other).o.boolean

    def __xor__(self, other: Any) -> Self:
        self._assert_output('^')
        from ..nodes.geometry.converter import BooleanMath
        return BooleanMath.not_equal(self.socket, other).o.boolean

    def __invert__(self) -> Self:
        self._assert_output('~')
        from ..nodes.geometry.converter import BooleanMath
        return BooleanMath.l_not(self.socket).o.boolean

    @property
    def switch(self) -> _BooleanSwitchSocketFactory:
        self._assert_output('switch')
        return _BooleanSwitchSocketFactory(self.socket)

class _RotationMixin(_HashMixin, BaseSocket):
    socket: NodeSocketRotation

    def invert(self) -> Self:
        self._assert_output('invert')
        from ..nodes.geometry import InvertRotation
        return InvertRotation._find_or_create_linked(self.socket).o.rotation

    def rotate(self, rotation: InputRotation, rotation_space: Literal['GLOBAL', 'LOCAL']='GLOBAL') -> Self:
        self._assert_output('rotate')
        from ..nodes.geometry import RotateRotation
        return RotateRotation(self.socket, rotation, rotation_space=rotation_space).o.rotation

    def to_euler(self) -> VectorResult:
        self._assert_output('to_euler')
        from ..nodes.geometry.converter import RotationToEuler
        return RotationToEuler._find_or_create_linked(self.socket).o.euler

    def to_quaternion(self) -> ResultQuaternionComponents[FloatResult]:
        self._assert_output('to_quaternion')
        from ..nodes.geometry import RotationToQuaternion
        o = RotationToQuaternion._find_or_create_linked(self.socket).o
        return ResultQuaternionComponents(o.w, o.x, o.y, o.z)

    def to_axis_angle(self) -> ResultAxisAngle[FloatResult, VectorResult]:
        self._assert_output('to_axis_angle')
        from ..nodes.geometry import RotationToAxisAngle
        o = RotationToAxisAngle(self.socket).o
        return ResultAxisAngle(o.axis, o.angle)

    def align_to_vector(self, vector: InputVector=(0.0, 0.0, 1.0), factor: InputFloat=1.0, *, axis: Literal['X', 'Y', 'Z']='Z', pivot_axis: Literal['AUTO', 'X', 'Y', 'Z']='AUTO') -> Self:
        self._assert_output('align_to_vector')
        from ..nodes.geometry import AlignRotationToVector
        return AlignRotationToVector(rotation=self.socket, factor=factor, vector=vector, axis=axis, pivot_axis=pivot_axis).o.rotation

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _FloatMixDataTypeFactory:

    def __init__(self, socket: NodeSocket):
        self._socket = socket
        from ..nodes.geometry import Mix
        self._mix = Mix

    def float(self, a: InputFloat, b: InputFloat) -> FloatSocket:
        return self._mix.float(self._socket, a, b).o.result_float

    def vector(self, a: InputVector, b: InputVector) -> VectorSocket:
        return self._mix.vector(self._socket, a, b).o.result_vector

    def color(self, a: InputColor, b: InputColor) -> ColorSocket:
        return self._mix.color(self._socket, a, b).o.result_color

    def rotation(self, a: InputRotation, b: InputRotation) -> RotationSocket:
        return self._mix.rotation(self._socket, a, b).o.result_rotation

class _FloatMixin(_HashMixin, _BlurMixin, BaseSocket):
    socket: NodeSocketFloat

    @property
    def _math(self) -> type[Math]:
        from ..nodes.geometry import Math
        return Math

    @property
    def mix(self) -> _FloatMixDataTypeFactory:
        self._assert_output('mix')
        return _FloatMixDataTypeFactory(self.socket)

    def map_range(self, from_min: InputFloat=0.0, from_max: InputFloat=1.0, to_min: InputFloat=0.0, to_max: InputFloat=1.0, *, clamp: bool=True, interpolation_type: Literal['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']='LINEAR', steps: InputFloat=4.0) -> Self:
        self._assert_output('map_range')
        from ..nodes.geometry import MapRange
        node = MapRange.float(self.socket, from_min, from_max, to_min, to_max)
        node.clamp = clamp
        node.interpolation_type = interpolation_type
        if interpolation_type == 'STEPPED':
            node._establish_links(steps=steps)
        return node.o.result

    def clamp(self, min: InputFloat=0.0, max: InputFloat=1.0) -> Self:
        self._assert_output('clamp')
        from ..nodes.geometry import Clamp
        return Clamp.min_max(self.socket, min, max).o.result

    def min(self, value: InputFloat) -> Self:
        self._assert_output('min')
        return self._math.minimum(self.socket, value).o.value

    def max(self, value: InputFloat) -> Self:
        self._assert_output('max')
        return self._math.maximum(self.socket, value).o.value

    def smooth_min(self, value: InputFloat, distance: InputFloat) -> Self:
        self._assert_output('smooth_min')
        return self._math.smooth_minimum(self.socket, value, distance).o.value

    def smooth_max(self, value: InputFloat, distance: InputFloat) -> Self:
        self._assert_output('smooth_max')
        return self._math.smooth_maximum(self.socket, value, distance).o.value

    def inverse_sqrt(self) -> Self:
        self._assert_output('inverse_sqrt')
        return self._math.inverse_square_root(self.socket).o.value

    def is_close(self, other: InputFloat, epsilon: InputFloat=0.0001) -> BooleanSocket:
        self._assert_output('is_close')
        from ..nodes.geometry import Compare
        return Compare.float.equal(self.socket, other, epsilon=epsilon).o.result

    def sin(self) -> Self:
        self._assert_output('sin')
        return self._math.sine(self.socket).o.value

    def cos(self) -> Self:
        self._assert_output('cos')
        return self._math.cosine(self.socket).o.value

    def tan(self) -> Self:
        self._assert_output('tan')
        return self._math.tangent(self.socket).o.value

    def asin(self) -> Self:
        self._assert_output('asin')
        return self._math.arcsine(self.socket).o.value

    def acos(self) -> Self:
        self._assert_output('acos')
        return self._math.arccosine(self.socket).o.value

    def atan(self) -> Self:
        self._assert_output('atan')
        return self._math.arctangent(self.socket).o.value

    def sinh(self) -> Self:
        self._assert_output('sinh')
        return self._math.hyperbolic_sine(self.socket).o.value

    def cosh(self) -> Self:
        self._assert_output('cosh')
        return self._math.hyperbolic_cosine(self.socket).o.value

    def tanh(self) -> Self:
        self._assert_output('tanh')
        return self._math.hyperbolic_tangent(self.socket).o.value

    def exp(self) -> Self:
        self._assert_output('exp')
        return self._math.exponent(self.socket).o.value

    def snap(self, increment: InputFloat=0.5) -> Self:
        self._assert_output('snap')
        return self._math.snap(self.socket, increment).o.value

    def atan2(self, value: InputFloat=0.5) -> Self:
        self._assert_output('atan2')
        return self._math.arctan2(self.socket, value).o.value

    def sqrt(self) -> Self:
        self._assert_output('sqrt')
        return self._math.square_root(self.socket).o.value

    def power(self, exponent: InputFloat=2.0) -> Self:
        self._assert_output('power')
        return self._math.power(self.socket, exponent).o.value

    def log(self, base: InputFloat=2.0) -> Self:
        self._assert_output('log')
        return self._math.logarithm(self.socket, base).o.value

    def floor(self) -> Self:
        self._assert_output('floor')
        return self._math.floor(self.socket).o.value

    def ceil(self) -> Self:
        self._assert_output('ceil')
        return self._math.ceil(self.socket).o.value

    def truncate(self) -> Self:
        self._assert_output('truncate')
        return self._math.truncate(self.socket).o.value

    def fraction(self) -> Self:
        self._assert_output('fraction')
        return self._math.fraction(self.socket).o.value

    def round(self) -> Self:
        self._assert_output('round')
        return self._math.round(self.socket).o.value

    def ping_pong(self, value: InputFloat=1.0) -> Self:
        self._assert_output('ping_pong')
        return self._math.ping_pong(self.socket, value).o.value

    def modulo(self, divisor: InputFloat) -> Self:
        self._assert_output('modulo')
        return self._math.floored_modulo(self.socket, divisor).o.value

    def abs(self) -> Self:
        self._assert_output('abs')
        return self._math.absolute(self.socket).o.value

    def wrap(self, min: InputFloat=0.0, max: InputFloat=1.0) -> Self:
        self._assert_output('wrap')
        return self._math.wrap(self.socket, value_001=max, value_002=min).o.value

    def mul_add(self, multiplier: InputFloat=0.5, addend: InputFloat=0.5) -> Self:
        self._assert_output('mul_add')
        return self._math.multiply_add(self.socket, multiplier, addend).o.value

    def to_radians(self) -> Self:
        self._assert_output('to_radians')
        return self._math.to_radians(self.socket).o.value

    def to_degrees(self) -> Self:
        self._assert_output('to_degrees')
        return self._math.to_degrees(self.socket).o.value

    def sign(self) -> Self:
        self._assert_output('sign')
        return self._math.sign(self.socket).o.value

    def negate(self) -> Self:
        self._assert_output('negate')
        return self._math.multiply(self.socket, -1).o.value

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _IntegerMixin(_HashMixin, _BlurMixin, BaseSocket):
    socket: NodeSocketInt
    tree: TreeBuilder[Any]
    _tree: TreeBuilder[Any]

    @property
    def _imath(self) -> type[IntegerMath]:
        from ..nodes.geometry import IntegerMath
        return IntegerMath

    def clamp(self, min: InputInteger=0, max: InputInteger=1) -> Self:
        self._assert_output('clamp')
        return self.max(min).min(max)

    def min(self, value: InputInteger) -> Self:
        self._assert_output('min')
        return self._imath.minimum(self.socket, value).o.value

    def max(self, value: InputInteger) -> Self:
        self._assert_output('max')
        return self._imath.maximum(self.socket, value).o.value

    def divide_round(self, divisor: InputInteger) -> Self:
        self._assert_output('divide_round')
        return self._imath.divide_round(self.socket, divisor).o.value

    def divide_ceiling(self, divisor: InputInteger) -> Self:
        self._assert_output('divide_ceiling')
        return self._imath.divide_ceiling(self.socket, divisor).o.value

    def gcd(self, value: InputInteger) -> Self:
        self._assert_output('gcd')
        return self._imath.greatest_common_divisor(self.socket, value).o.value

    def lcm(self, value: InputInteger) -> Self:
        self._assert_output('lcm')
        return self._imath.least_common_multiple(self.socket, value).o.value

    def shift(self, amount: InputInteger) -> Self:
        self._assert_output('shift')
        from ..nodes.geometry import BitMath
        return BitMath.shift(self.socket, amount).o.value

    def rotate(self, amount: InputInteger) -> Self:
        self._assert_output('rotate')
        from ..nodes.geometry import BitMath
        return BitMath.rotate(self.socket, amount).o.value

    def to_float(self) -> FloatResult:
        self._assert_output('to_float')
        from ..nodes.geometry import ImplicitConversion
        return ImplicitConversion.float(self.socket).o.value

    def modulo(self, divisor: InputInteger) -> Self:
        self._assert_output('modulo')
        return self._imath.floored_modulo(self.socket, divisor).o.value

    def abs(self) -> Self:
        self._assert_output('abs')
        return self._imath.absolute(self.socket).o.value

    def sign(self) -> Self:
        self._assert_output('sign')
        return self._imath.sign(self.socket).o.value

    def negate(self) -> Self:
        self._assert_output('negate')
        return self._imath.negate(self.socket).o.value

    def mul_add(self, multiplier: InputInteger=0, addend: InputInteger=0) -> Self:
        self._assert_output('mul_add')
        return self._imath.multiply_add(self.socket, multiplier, addend).o.value

    def power(self, exponent: InputInteger=2) -> Self:
        self._assert_output('power')
        return self._imath.power(self.socket, exponent).o.value

    @staticmethod
    def _is_integer_socket(value: Any) -> bool:
        socket = getattr(value, 'socket', getattr(value, '_default_output_socket', None))
        return isinstance(socket, NodeSocket) and socket.type == 'INT'

    def _other_is_integer(self, other: Any) -> bool:
        return isinstance(other, int) or self._is_integer_socket(other)

    def _dispatch_math(self, other: Any, operation: str, reverse: bool=False) -> Self | FloatResult:
        if self._is_geometry_tree and self._other_is_integer(other) and (operation != 'divide'):
            from ..nodes.geometry.converter import IntegerMath
            values = (self.socket, other) if not reverse else (other, self.socket)
            if operation == 'modulo':
                operation = 'floored_modulo'
            return getattr(IntegerMath, operation)(*values).o.value
        return Socket._dispatch_math(cast('Socket', self), other, operation, reverse)

    def _dispatch_unary(self, operation: str) -> Self | FloatResult:
        if self._is_geometry_tree:
            from ..nodes.geometry.converter import IntegerMath
            if operation == 'negate':
                return IntegerMath.negate(self.socket).o.value
            elif operation == 'absolute':
                return IntegerMath.absolute(self.socket).o.value
        return Socket._dispatch_unary(cast('Socket', self), operation)

    def _dispatch_floordiv(self, other: Any, reverse: bool=False) -> Self | FloatResult:
        if self._is_geometry_tree and self._other_is_integer(other):
            from ..nodes.geometry.converter import IntegerMath
            values = (self.socket, other) if not reverse else (other, self.socket)
            return IntegerMath.divide_floor(*values).o.value
        return Socket._dispatch_floordiv(cast('Socket', self), other, reverse)

    def _dispatch_compare(self, other: Any, operation: str) -> BooleanSocket | FloatSocket:
        if self._is_geometry_tree:
            from ..nodes.geometry.manual import Compare
            return getattr(Compare.integer, operation)(self.socket, other).o.result
        return Socket._dispatch_compare(cast('Socket', self), other, operation)
    if TYPE_CHECKING:

        def __add__(self, other: Any) -> Self:
            ...

        def __radd__(self, other: Any) -> Self:
            ...

        def __sub__(self, other: Any) -> Self:
            ...

        def __rsub__(self, other: Any) -> Self:
            ...

        def __mul__(self, other: Any) -> Self:
            ...

        def __rmul__(self, other: Any) -> Self:
            ...

        def __truediv__(self, other: Any) -> Self:
            ...

        def __rtruediv__(self, other: Any) -> Self:
            ...

        def __floordiv__(self, other: Any) -> Self:
            ...

        def __rfloordiv__(self, other: Any) -> Self:
            ...

        def __neg__(self) -> Self:
            ...

        def __abs__(self) -> Self:
            ...

        def __lt__(self, other: Any) -> BooleanSocket:
            ...

        def __gt__(self, other: Any) -> BooleanSocket:
            ...

        def __le__(self, other: Any) -> BooleanSocket:
            ...

        def __ge__(self, other: Any) -> BooleanSocket:
            ...

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _StringMixin(_HashMixin, BaseSocket):
    socket: NodeSocketString

    @property
    def _match(self) -> type[MatchString]:
        from ..nodes.geometry import MatchString
        return MatchString

    def starts_with(self, search: InputString) -> BooleanResult:
        self._assert_output('starts_with')
        return self._match(self.socket, 'Starts With', search).o.result

    def ends_with(self, search: InputString) -> BooleanResult:
        self._assert_output('ends_with')
        return self._match(self.socket, 'Ends With', search).o.result

    def contains(self, search: InputString) -> BooleanResult:
        self._assert_output('contains')
        return self._match(self.socket, 'Contains', search).o.result

    def slice(self, position: InputInteger=0, length: InputInteger=0) -> StringResult:
        self._assert_output('slice')
        from ..nodes.geometry import SliceString
        return SliceString(self.socket, position, length).o.string

    def format(self, items: Mapping[str, InputString | InputInteger | InputFloat]) -> StringResult:
        self._assert_output('format')
        from ..nodes.geometry import FormatString
        return FormatString(self.socket, items).o.string

    def replace(self, find: InputString, replace: InputString) -> StringResult:
        self._assert_output('replace')
        from ..nodes.geometry import ReplaceString
        return ReplaceString(self.socket, find, replace).o.string

    def reverse(self) -> StringResult:
        self._assert_output('reverse')
        from ..nodes.geometry import ReverseString
        return ReverseString(self.socket).o.string

    def length(self) -> IntegerResult:
        self._assert_output('length')
        from ..nodes.geometry import StringLength
        return StringLength(self.socket).o.length

    def find(self, search: InputString) -> ResultStringFind[IntegerResult]:
        self._assert_output('find')
        from ..nodes.geometry import FindInString
        o = FindInString(self.socket, search).o
        return ResultStringFind(o.first_found, o.count)

    def uppercase(self) -> StringResult:
        self._assert_output('uppercase')
        from ..nodes.geometry import SetStringCase
        return SetStringCase(self.socket, case='Uppercase').o.string

    def lowercase(self) -> StringResult:
        self._assert_output('lowercase')
        from ..nodes.geometry import SetStringCase
        return SetStringCase(self.socket, case='Lowercase').o.string

    def trim(self, characters: InputString='', whitespace: InputBoolean=True, start: InputBoolean=True, end: InputBoolean=True) -> StringResult:
        self._assert_output('trim')
        from ..nodes.geometry import TrimString
        return TrimString(self.socket, characters=characters, whitespace=whitespace, start=start, end=end).o.string

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _MatrixMixin(_HashMixin, BaseSocket):
    socket: NodeSocketMatrix

    @property
    def translation(self) -> VectorResult:
        self._assert_output('translation')
        from ..nodes.geometry.converter import SeparateTransform
        return SeparateTransform._find_or_create_linked(self.socket).o.translation

    @property
    def rotation(self) -> RotationResult:
        self._assert_output('rotation')
        from ..nodes.geometry.converter import SeparateTransform
        return SeparateTransform._find_or_create_linked(self.socket).o.rotation

    @property
    def scale(self) -> VectorResult:
        self._assert_output('scale')
        from ..nodes.geometry.converter import SeparateTransform
        return SeparateTransform._find_or_create_linked(self.socket).o.scale

    def determinant(self) -> FloatResult:
        self._assert_output('determinant')
        from ..nodes.geometry import MatrixDeterminant
        return MatrixDeterminant._find_or_create_linked(self.socket).o.determinant

    def invert(self) -> Self:
        self._assert_output('invert')
        from ..nodes.geometry import InvertMatrix
        return InvertMatrix._find_or_create_linked(self.socket).o.matrix

    def transpose(self) -> Self:
        self._assert_output('transpose')
        from ..nodes.geometry import TransposeMatrix
        return TransposeMatrix._find_or_create_linked(self.socket).o.matrix

    def svd(self) -> ResultMatrixSVD[MatrixResult, VectorResult]:
        self._assert_output('svd')
        from ..nodes.geometry import MatrixSVD
        o = MatrixSVD(self.socket).o
        return ResultMatrixSVD(o.u, o.s, o.v)

    def transform_direction(self, direction: InputVector) -> VectorResult:
        _deprecated('MatrixSocket.transform_direction(direction)', 'VectorSocket.transform_direction(matrix)')
        self._assert_output('transform_direction')
        from ..nodes.geometry import TransformDirection
        return TransformDirection(direction, self.socket).o.direction

    @staticmethod
    def _cast_to_matrix(value) -> MatrixSocket:
        from ..nodes.geometry.converter import CombineMatrix
        if hasattr(value, 'shape') and value.shape == (4, 4):
            return CombineMatrix(*value.ravel()).o.matrix
        else:
            return value

    @overload
    def __matmul__(self, other: MatrixSocket) -> MatrixResult:
        ...

    @overload
    def __matmul__(self, other: CombineTransform) -> MatrixResult:
        ...

    @overload
    def __matmul__(self, other: RotationSocket) -> RotationResult:
        ...

    @overload
    def __matmul__(self, other: Position) -> VectorResult:
        ...

    @overload
    def __matmul__(self, other: VectorSocket) -> VectorResult:
        ...

    @overload
    def __matmul__(self, other: Vector) -> VectorResult:
        ...

    def __matmul__(self, other: Any) -> Self | VectorResult:
        from ..nodes.geometry.converter import MultiplyMatrices, TransformPoint
        other = self._cast_to_matrix(other)
        socket = self._default_output_socket
        if socket.type == 'MATRIX' and _output_socket_type(other) == 'VECTOR':
            return TransformPoint(other, socket).o.vector
        return MultiplyMatrices(socket, other).o.matrix

    def __rmatmul__(self, other: Any) -> Self:
        from ..nodes.geometry.converter import MultiplyMatrices, TransformPoint
        other = self._cast_to_matrix(other)
        socket = self._default_output_socket
        if socket.type == 'VECTOR' and _output_socket_type(other) == 'MATRIX':
            return TransformPoint(socket, other).o.vector
        return MultiplyMatrices(other, socket).o.matrix

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _ListMixin(Socket):

    def list_length(self) -> IntegerSocket:
        from ..nodes.geometry import ListLength
        return ListLength(self.socket, data_type=self._socket_dtype).o.length

    @overload
    def get(self, index: InputIntegerList) -> Self:
        ...

    @overload
    def get(self, index: InputInteger) -> T:
        ...

    def get(self, index: InputInteger | InputIntegerList) -> T | Self:
        from ..nodes.geometry import GetListItem
        return GetListItem(list=self.socket, index=index, socket_type=self._socket_dtype).o.value

    def filter(self, selection: InputBoolean | BooleanSocketList=True) -> Self:
        from ..nodes.geometry import FilterList
        return FilterList(self.socket, selection=selection, socket_type=self._socket_dtype).o.selection

    def sort(self, sort_weight: InputFloat | InputFloatList, group_id: InputInteger | IntegerSocket=None, selection: InputBoolean | BooleanSocketList=None) -> Self:
        from ..nodes.geometry import SortList
        return SortList(self.socket, selection=selection, group_id=group_id, sort_weight=sort_weight, socket_type=self._socket_dtype).o.list

    def reverse(self) -> Self:
        from ..nodes.geometry import Index, SortList
        return SortList(list=self.socket, sort_weight=Index().o.index.negate(), socket_type=self._socket_dtype).o.list

    def list_slice(self, start: InputInteger=0, stop: InputInteger=None, step: InputInteger=1) -> Self:
        from ..nodes.geometry.converter import GetListItem
        from ..nodes.geometry.groups import SliceToIndices
        if stop is None:
            stop = self.list_length()
        elif isinstance(stop, int) and stop < 0:
            stop = self.list_length() + stop
        if start is None:
            start = 0
        elif isinstance(start, int) and start < 0:
            start = self.list_length() + start
        if step is None:
            step = 1
        indices = SliceToIndices(start=start, stop=stop, step=step).o.indices
        return GetListItem(self.socket, indices, socket_type=self._socket_dtype).o.value

    @overload
    def __getitem__(self, key: int) -> T:
        ...

    @overload
    def __getitem__(self, key: IntegerSocketList) -> Self:
        ...

    @overload
    def __getitem__(self, key: slice) -> Self:
        ...

    def __getitem__(self, key: int | IntegerSocketList | slice) -> T:
        from ..nodes.geometry.converter import GetListItem
        if isinstance(key, slice):
            return self.list_slice(key.start, key.stop, key.step)
        return GetListItem(self.socket, index=key, socket_type=self._socket_dtype).o.value

    def __len__(self) -> IntegerSocket:
        from ..nodes.geometry.converter import ListLength
        return ListLength(self.socket, data_type=self._socket_dtype).o.length

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _DefaultValueMixin(BaseSocket):

    @property
    def default_value(self) -> T:
        self._assert_input('default_value')
        return self.socket.default_value

    @default_value.setter
    def default_value(self, value: T) -> None:
        self._assert_input('default_value')
        self.socket.default_value = value

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _ToListMixin(BaseSocket):

    def to_list(self, count: InputInteger=10) -> T:
        from ..nodes.geometry import FieldToList
        return FieldToList(count, {self.name: self}).o[0]

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _FloatConvertDatatypeMixin(BaseSocket):

    def to_string(self, decimals: InputInteger=0) -> StringResult:
        self._assert_output('to_string')
        from ..nodes.geometry import ValueToString
        return ValueToString.float(self.socket, decimals).o.string

    def to_integer(self, rounding_mode: Literal['ROUND', 'FLOOR', 'CEILING', 'TRUNCATE']='ROUND') -> IntegerResult:
        self._assert_output('to_integer')
        from ..nodes.geometry import FloatToInteger
        return FloatToInteger(self.socket, rounding_mode=rounding_mode).o.integer

    def __round__(self, ndigits: None=None) -> IntegerResult:
        if ndigits is not None:
            raise TypeError('round() on a socket does not take ndigits; use .snap()')
        return self.to_integer('ROUND')

    def __floor__(self) -> IntegerResult:
        return self.to_integer('FLOOR')

    def __ceil__(self) -> IntegerResult:
        return self.to_integer('CEILING')

    def __trunc__(self) -> IntegerResult:
        return self.to_integer('TRUNCATE')

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class _IntegerConvertDatatypeMixin(Socket):

    def to_string(self, base: InputInteger=10, padding: InputInteger=0) -> StringResult:
        self._assert_output('to_string')
        from ..nodes.geometry import ValueToString
        return ValueToString.integer(self.socket, base, padding).o.string

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class FloatSocket(_FloatMixin, _ToListMixin, _FloatConvertDatatypeMixin, _DefaultValueMixin, Socket):

    @property
    def point(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'point')

    @property
    def edge(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'edge')

    @property
    def face(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'face')

    @property
    def corner(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'corner')

    @property
    def spline(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'spline')

    @property
    def instance(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'instance')

    @property
    def layer(self) -> _StatsField[FloatSocket]:
        return _StatsField(self.socket, 'float', 'layer')

class FloatSocketList(_FloatMixin, _FloatConvertDatatypeMixin, _ListMixin):
    pass

class FloatSocketGrid(_FloatMixin, _GridSocketMixin, _FloatGridOperatorMixin, _GridMeanMixin, _GridAdvectMixin):
    pass

class VectorSocket(_VectorMixin, _ToListMixin, Socket):

    @property
    def default_value(self) -> list[float]:
        return list(self.socket.default_value)

    @default_value.setter
    def default_value(self, value: list[float] | tuple[float, float, float]) -> None:
        self.socket.default_value = value

    @property
    def point(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'point')

    @property
    def edge(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'edge')

    @property
    def face(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'face')

    @property
    def corner(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'corner')

    @property
    def spline(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'spline')

    @property
    def instance(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'instance')

    @property
    def layer(self) -> _StatsField[VectorSocket]:
        return _StatsField(self.socket, 'vector', 'layer')

class VectorSocketList(_VectorMixin, _ListMixin):
    if TYPE_CHECKING:

        @overload
        def __getitem__(self, key: slice) -> list[FloatSocketList]:
            ...

        @overload
        def __getitem__(self, key: int) -> FloatSocketList:
            ...

        def __getitem__(self, key: int | slice) -> FloatSocketList | list[FloatSocketList]:
            ...

        def __len__(self) -> int:
            ...

class VectorSocketGrid(_VectorMixin, _GridSocketMixin, _VectorGridOperatorMixin, _GridMeanMixin, _GridAdvectMixin):
    pass

class ColorSocket(_ColorMixin, _ToListMixin, Socket):
    pass

class ColorSocketList(ColorSocket, _ListMixin):

    @overload
    def __getitem__(self, key: slice) -> list[FloatSocket]:
        ...

    @overload
    def __getitem__(self, key: int) -> FloatSocket:
        ...

    def __getitem__(self, key: int | slice) -> FloatSocket | list[FloatSocket]:
        return _ColorMixin.__getitem__(self, key)

    def __len__(self) -> int:
        return _ColorMixin.__len__(self)

class IntegerSocket(_IntegerMixin, _ToListMixin, _IntegerConvertDatatypeMixin, _DefaultValueMixin, Socket):

    @property
    def point(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'point')

    @property
    def edge(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'edge')

    @property
    def face(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'face')

    @property
    def corner(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'corner')

    @property
    def spline(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'spline')

    @property
    def instance(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'instance')

    @property
    def layer(self) -> _MinMaxField[IntegerSocket]:
        return _MinMaxField(self.socket, 'integer', 'layer')

class IntegerSocketList(_IntegerMixin, _IntegerConvertDatatypeMixin, _ListMixin):
    pass

class IntegerVectorSocket(_IntegerMixin, _DefaultValueMixin, Socket):
    pass

class IntegerSocketGrid(_IntegerMixin, _GridSocketMixin, _GridMeanMixin, _GridAdvectMixin):
    pass

class BooleanSocket(_BooleanMixin, _ToListMixin, _DefaultValueMixin, Socket):

    @property
    def point(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'point')

    @property
    def edge(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'edge')

    @property
    def face(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'face')

    @property
    def corner(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'corner')

    @property
    def spline(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'spline')

    @property
    def instance(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'instance')

    @property
    def layer(self) -> _EvaluateField[BooleanSocket]:
        return _EvaluateField(self.socket, 'boolean', 'layer')

class BooleanSocketList(_BooleanMixin, _ListMixin):
    pass

class BooleanSocketGrid(_BooleanMixin, _GridSocketMixin):
    pass

class RotationSocket(_RotationMixin, _ToListMixin, _DefaultValueMixin, Socket):

    @property
    def point(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'point')

    @property
    def edge(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'edge')

    @property
    def face(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'face')

    @property
    def corner(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'corner')

    @property
    def spline(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'spline')

    @property
    def instance(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'instance')

    @property
    def layer(self) -> _EvaluateField[RotationSocket]:
        return _EvaluateField(self.socket, 'quaternion', 'layer')

class RotationSocketList(_RotationMixin, _ListMixin):
    pass

class MatrixSocket(_MatrixMixin, _ToListMixin, Socket):

    @property
    def point(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'point')

    @property
    def edge(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'edge')

    @property
    def face(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'face')

    @property
    def corner(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'corner')

    @property
    def spline(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'spline')

    @property
    def instance(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'instance')

    @property
    def layer(self) -> _AccumulateField[MatrixSocket]:
        return _AccumulateField(self.socket, 'matrix', 'layer')

    @overload
    def __getitem__(self, key: slice) -> list[FloatSocket]:
        ...

    @overload
    def __getitem__(self, key: int) -> FloatSocket:
        ...

    def __getitem__(self, key: int | slice) -> FloatSocket | list[FloatSocket]:
        from ..nodes.geometry import CombineMatrix, SeparateMatrix
        if self.socket.is_output:
            node = SeparateMatrix._find_or_create_linked(self.socket)
            if isinstance(key, slice):
                return [cast(FloatSocket, node.o[i]) for i in range(*key.indices(len(node.o)))]
            return cast(FloatSocket, node.o[key])
        else:
            node = CombineMatrix._find_or_create_linked(self.socket)
            if isinstance(key, slice):
                return [cast(FloatSocket, node.i[i]) for i in range(*key.indices(len(node.i)))]
        return cast(FloatSocket, node.i[key])

    def __iter__(self) -> Iterator[FloatSocket]:
        from ..nodes.geometry import CombineMatrix, SeparateMatrix
        if self.socket.is_output:
            node = SeparateMatrix._find_or_create_linked(self.socket)
            for i in node.o:
                yield cast(FloatSocket, i)
        else:
            node = CombineMatrix._find_or_create_linked(self.socket)
            for i in node.i:
                yield cast(FloatSocket, i)

    def __len__(self) -> int:
        return 16

class MatrixSocketList(_MatrixMixin, _ListMixin):
    pass

class StringSocket(_StringMixin, _ToListMixin, _DefaultValueMixin, Socket):

    def split(self, separator: InputString='') -> StringSocketList:
        from ..nodes.geometry import SplitString
        return SplitString(self.socket, separator=separator).o.list

    def to_float(self) -> FloatSocket:
        self._assert_output('to_float')
        from ..nodes.geometry import StringToValue
        return StringToValue.float(self.socket).o.value

    def to_integer(self, base: InputInteger=10) -> IntegerSocket:
        self._assert_output('to_integer')
        from ..nodes.geometry import StringToValue
        return StringToValue.integer(self.socket, base).o.value

    def join(self, strings: Iterable[str | StringSocket | NodeSocketString | BaseNode]) -> StringSocket:
        self._assert_output('join')
        from ..nodes.geometry import JoinStrings
        return JoinStrings(strings, self.socket).o.string

    def __add__(self, other: StringSocket | str) -> StringSocket:
        self._assert_output('+')
        from ..nodes.geometry import JoinStrings, String
        if isinstance(other, str):
            other = String(other).o.string
        return JoinStrings((self.socket, other)).o.string

    def __radd__(self, other: str | StringSocket) -> StringSocket:
        self._assert_output('+')
        from ..nodes.geometry import JoinStrings, String
        if isinstance(other, str):
            other = String(other).o.string
        return JoinStrings((other, self.socket)).o.string

class StringSocketList(_StringMixin, _ListMixin):
    pass

class _MenuSocketMixin(Socket):
    socket: NodeSocketMenu

class MenuSocket(_MenuSocketMixin, _ToListMixin):

    @property
    def default_value(self) -> str:
        tree = getattr(self, '_tree', None)
        identifier = getattr(self, '_interface_identifier', '')
        if tree is not None and identifier:
            for pending in reversed(tree._menu_defaults):
                if pending.identifier == identifier:
                    return pending.default
            interface = tree.tree.interface
            if interface is not None:
                item = next((item for item in interface.items_tree if getattr(item, 'identifier', None) == identifier), None)
                if item is not None:
                    return item.default_value
        return self.socket.default_value

    @default_value.setter
    def default_value(self, value: str) -> None:
        interface_socket = getattr(self, '_interface_socket', None)
        tree = getattr(self, '_tree', None)
        if interface_socket is not None and tree is not None:
            from .tree import _MenuDefault
            tree._menu_defaults.append(_MenuDefault(interface_socket, value, identifier=getattr(self, '_interface_identifier', '')))
            if tree._exited:
                tree._apply_input_defaults()
                tree._menu_defaults.clear()
            return
        self.socket.default_value = value

class MenuSocketList(_MenuSocketMixin, _ListMixin):
    pass

class GeometrySocket(Socket):
    socket: NodeSocketGeometry

    def bundle(self) -> BundleSocket:
        self._assert_output('bundle')
        from ..nodes.geometry import GetGeometryBundle
        return GetGeometryBundle(self.socket).o.bundle

    def set_bundle(self, bundle: InputBundle) -> GeometrySocket:
        self._assert_output('set_bundle')
        from ..nodes.geometry import SetGeometryBundle
        return SetGeometryBundle(self.socket, bundle).o.geometry

    def realize_instances(self, selection: InputBoolean=True, realize_all: InputBoolean=False, depth: InputInteger=0) -> GeometrySocket:
        from ..nodes.geometry import RealizeInstances
        return RealizeInstances(self.socket, selection=selection, realize_all=realize_all, depth=depth).o.geometry

class GeometrySocketList(GeometrySocket, _ListMixin):
    pass

class _ObjectMixin(Socket):
    socket: NodeSocketObject

class ObjectSocket(_ObjectMixin, _DefaultValueMixin):

    def camera_info(self) -> CameraInfo:
        self._assert_output('camera_info')
        from ..nodes.geometry import CameraInfo
        return CameraInfo(self.socket)

    def bone_info(self, bone_name: InputString, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> BoneInfo:
        self._assert_output('bone_info')
        from ..nodes.geometry import BoneInfo
        return BoneInfo(self.socket, bone_name, transform_space=transform_space)

    @property
    def _info(self) -> type[ObjectInfo]:
        from ..nodes.geometry import ObjectInfo
        return ObjectInfo

    def matrix(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> MatrixSocket:
        return self._info(self.socket, transform_space=transform_space).o.transform

    def transform(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> MatrixSocket:
        _deprecated('ObjectSocket.transform()', 'ObjectSocket.matrix()')
        return self.matrix(transform_space)

    def location(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> VectorSocket:
        return self._info(self.socket, transform_space=transform_space).o.location

    def rotation(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> RotationSocket:
        return self._info(self.socket, transform_space=transform_space).o.rotation

    def scale(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL') -> VectorSocket:
        return self._info(self.socket, transform_space=transform_space).o.scale

    def geometry(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL', as_instance: InputBoolean=False) -> GeometrySocket:
        return self._info(self.socket, as_instance=as_instance, transform_space=transform_space).o.geometry

class ObjectSocketList(_ObjectMixin, _ListMixin):
    pass

class _MaterialSocketMixin(Socket):
    socket: NodeSocketMaterial

class MaterialSocket(_MaterialSocketMixin, _DefaultValueMixin):

    def selection(self) -> BooleanSocket:
        self._assert_output('selection')
        from ..nodes.geometry import MaterialSelection
        return MaterialSelection(self.socket).o.selection

class MaterialSocketList(_MaterialSocketMixin, _ListMixin):
    pass

class _ImageSocketMixin(Socket):
    socket: NodeSocketImage

class ImageSocket(_ImageSocketMixin, _DefaultValueMixin):

    def info(self, frame: InputInteger=0) -> ImageInfo:
        self._assert_output('info')
        from ..nodes.geometry import ImageInfo
        return ImageInfo(self.socket, frame)

class ImageSocketList(_ImageSocketMixin, _ListMixin):
    pass

class _CollectionSocketMixin(Socket):
    socket: NodeSocketCollection

class CollectionSocket(_CollectionSocketMixin, _DefaultValueMixin):

    def instances(self, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL', separate_children: InputBoolean=False, reset_children: InputBoolean=False) -> GeometrySocket:
        from ..nodes.geometry import CollectionInfo
        return CollectionInfo(self.socket, separate_children, reset_children, transform_space=transform_space).o.instances

    def children(self, recursive: InputBoolean=False) -> ResultCollectionChildren:
        self._assert_output('children')
        from ..nodes.geometry import CollectionChildren
        node = CollectionChildren(self.socket, recursive)
        return ResultCollectionChildren(node.o.collections, node.o.objects)

class CollectionSocketList(_CollectionSocketMixin, _ListMixin):
    pass

class _BundleGetFactory:

    def __init__(self, socket: NodeSocketBundle):
        self._socket = socket

    def _get(self, socket_type: str, path: InputString) -> Any:
        from ..nodes.geometry import GetBundleItem
        return getattr(GetBundleItem, socket_type)(self._socket, path).o.item

    def float(self, path: InputString) -> FloatSocket:
        return self._get('float', path)

    def integer(self, path: InputString) -> IntegerSocket:
        return self._get('integer', path)

    def boolean(self, path: InputString) -> BooleanSocket:
        return self._get('boolean', path)

    def vector(self, path: InputString) -> VectorSocket:
        return self._get('vector', path)

    def color(self, path: InputString) -> ColorSocket:
        return self._get('color', path)

    def rotation(self, path: InputString) -> RotationSocket:
        return self._get('rotation', path)

    def matrix(self, path: InputString) -> MatrixSocket:
        return self._get('matrix', path)

    def string(self, path: InputString) -> StringSocket:
        return self._get('string', path)

    def menu(self, path: InputString) -> MenuSocket:
        return self._get('menu', path)

    def object(self, path: InputString) -> ObjectSocket:
        return self._get('object', path)

    def image(self, path: InputString) -> ImageSocket:
        return self._get('image', path)

    def geometry(self, path: InputString) -> GeometrySocket:
        return self._get('geometry', path)

    def collection(self, path: InputString) -> CollectionSocket:
        return self._get('collection', path)

    def material(self, path: InputString) -> MaterialSocket:
        return self._get('material', path)

    def bundle(self, path: InputString) -> BundleSocket:
        return self._get('bundle', path)

    def closure(self, path: InputString) -> ClosureSocket:
        return self._get('closure', path)

    def font(self, path: InputString) -> FontSocket:
        return self._get('font', path)

    def sound(self, path: InputString) -> SoundSocket:
        return self._get('sound', path)

class _BundleSocketMixin(Socket):
    socket: NodeSocketBundle

class BundleSocket(_BundleSocketMixin):

    @property
    def get(self) -> _BundleGetFactory:
        self._assert_output('get')
        return _BundleGetFactory(self.socket)

    def has(self, path: InputString) -> BooleanSocket:
        self._assert_output('has')
        from ..nodes.geometry import GetBundleItem
        return GetBundleItem(self.socket, path).o.exists

    def store(self, path: InputString, value: InputAny) -> BundleSocket:
        self._assert_output('store')
        from ..nodes.geometry import StoreBundleItem
        from .items import _infer_value_type
        from .node import _value_socket_type
        socket_type = _value_socket_type(value) or _infer_value_type(value)
        if socket_type is None:
            raise TypeError(f'Cannot infer a bundle item type from {value!r}')
        return StoreBundleItem(self.socket, path, value, socket_type=socket_type.replace('VALUE', 'FLOAT')).o.bundle

    def join(self, *others: BundleSocket | BaseNode | NodeSocketBundle) -> BundleSocket:
        self._assert_output('join')
        from ..nodes.geometry import JoinBundle
        node = JoinBundle()
        for bundle in (self.socket, *others):
            node._link_from(*node._find_best_socket_pair(bundle, node.i['Bundle']))
        return node.o.bundle

    def __or__(self, other: Any) -> BundleSocket:
        return self.join(other)

    def paths(self, mode: InputMenu | Literal['All', 'Bundle Type', 'Data Type']='All', pattern_mode: InputMenu | Literal['Exact', 'Wildcard']='Exact', bundle_type: InputString='', data_type: InputMenu='Float') -> StringSocketList:
        self._assert_output('paths')
        from ..nodes.geometry import GetNestedBundlePaths
        return GetNestedBundlePaths(self.socket, mode, pattern_mode, bundle_type, data_type).o.paths

class BundleSocketList(_BundleSocketMixin, _ListMixin):
    pass

class _ClosureSocketMixin(Socket):
    socket: NodeSocketClosure

class ClosureSocket(_ClosureSocketMixin):
    pass

class ClosureSocketList(_ClosureSocketMixin, _ListMixin):
    pass

class _ShaderSocketMixin(Socket):
    socket: NodeSocketShader

class ShaderSocket(_ShaderSocketMixin):
    pass

class ShaderSocketList(_ShaderSocketMixin, _ListMixin):
    pass

class _FontSocketMixin(Socket):
    socket: NodeSocketFont

class FontSocket(_FontSocketMixin):
    pass

class FontSocketList(_FontSocketMixin, _ListMixin):
    pass

class _SoundSocketMixin(Socket):
    socket: NodeSocketSound

class SoundSocket(_SoundSocketMixin):
    pass

class SoundSocketList(_SoundSocketMixin, _ListMixin):
    pass
_SOCKET_REGISTRY['NodeSocketFloat'] = FloatSocket
_SOCKET_REGISTRY['NodeSocketVector'] = VectorSocket
_SOCKET_REGISTRY['NodeSocketColor'] = ColorSocket
_SOCKET_REGISTRY['NodeSocketInt'] = IntegerSocket
_SOCKET_REGISTRY['NodeSocketIntVector3D'] = IntegerVectorSocket
_SOCKET_REGISTRY['NodeSocketBool'] = BooleanSocket
_SOCKET_REGISTRY['NodeSocketRotation'] = RotationSocket
_SOCKET_REGISTRY['NodeSocketMatrix'] = MatrixSocket
_SOCKET_REGISTRY['NodeSocketString'] = StringSocket
_SOCKET_REGISTRY['NodeSocketMenu'] = MenuSocket
_SOCKET_REGISTRY['NodeSocketGeometry'] = GeometrySocket
_SOCKET_REGISTRY['NodeSocketObject'] = ObjectSocket
_SOCKET_REGISTRY['NodeSocketMaterial'] = MaterialSocket
_SOCKET_REGISTRY['NodeSocketImage'] = ImageSocket
_SOCKET_REGISTRY['NodeSocketSound'] = SoundSocket
_SOCKET_REGISTRY['NodeSocketFont'] = FontSocket
_SOCKET_REGISTRY['NodeSocketCollection'] = CollectionSocket
_SOCKET_REGISTRY['NodeSocketBundle'] = BundleSocket
_SOCKET_REGISTRY['NodeSocketClosure'] = ClosureSocket
_SOCKET_REGISTRY['NodeSocketShader'] = ShaderSocket
_SOCKET_LIST_REGISTRY['NodeSocketFloat'] = FloatSocketList
_SOCKET_LIST_REGISTRY['NodeSocketVector'] = VectorSocketList
_SOCKET_LIST_REGISTRY['NodeSocketColor'] = ColorSocketList
_SOCKET_LIST_REGISTRY['NodeSocketInt'] = IntegerSocketList
_SOCKET_LIST_REGISTRY['NodeSocketBool'] = BooleanSocketList
_SOCKET_LIST_REGISTRY['NodeSocketRotation'] = RotationSocketList
_SOCKET_LIST_REGISTRY['NodeSocketMatrix'] = MatrixSocketList
_SOCKET_LIST_REGISTRY['NodeSocketString'] = StringSocketList
_SOCKET_LIST_REGISTRY['NodeSocketMenu'] = MenuSocketList
_SOCKET_LIST_REGISTRY['NodeSocketGeometry'] = GeometrySocketList
_SOCKET_LIST_REGISTRY['NodeSocketObject'] = ObjectSocketList
_SOCKET_LIST_REGISTRY['NodeSocketImage'] = ImageSocketList
_SOCKET_LIST_REGISTRY['NodeSocketCollection'] = CollectionSocketList
_SOCKET_LIST_REGISTRY['NodeSocketBundle'] = BundleSocketList
_SOCKET_LIST_REGISTRY['NodeSocketShader'] = ShaderSocketList
_SOCKET_LIST_REGISTRY['NodeSocketFont'] = FontSocketList
_SOCKET_LIST_REGISTRY['NodeSocketSound'] = SoundSocketList
_SOCKET_GRID_REGISTRY['NodeSocketFloat'] = FloatSocketGrid
_SOCKET_GRID_REGISTRY['NodeSocketVector'] = VectorSocketGrid
_SOCKET_GRID_REGISTRY['NodeSocketInt'] = IntegerSocketGrid
_SOCKET_GRID_REGISTRY['NodeSocketBool'] = BooleanSocketGrid
