# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
import math
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, BundleSocket, ColorSocket, FloatSocket, FontSocket, GeometrySocket, IntegerSocket, MaterialSocket, MatrixSocket, MenuSocket, RotationSocket, StringSocket, StringSocketList, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputBundle, InputColor, InputFloat, InputFont, InputGeometry, InputInteger, InputMaterial, InputMatrix, InputMenu, InputRotation, InputString, InputStringList, InputVector
from .._mixins import _BakeMixin, _HandleModeMixin

class Arc(BaseNode):
    _bl_idname = 'GeometryNodeCurveArc'

    def __init__(self, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), middle: InputVector=(0.0, 2.0, 0.0), end: InputVector=(1.0, 0.0, 0.0), radius: InputFloat=1.0, start_angle: InputFloat=0.0, sweep_angle: InputFloat=7 * math.pi / 4, offset_angle: InputFloat=0.0, connect_center: InputBoolean=False, invert_arc: InputBoolean=False, *, mode: Literal['POINTS', 'RADIUS']='RADIUS'):
        super().__init__()
        key_args = {'Resolution': resolution, 'Start': start, 'Middle': middle, 'End': end, 'Radius': radius, 'Start Angle': start_angle, 'Sweep Angle': sweep_angle, 'Offset Angle': offset_angle, 'Connect Center': connect_center, 'Invert Arc': invert_arc}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def points(cls, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), middle: InputVector=(0.0, 2.0, 0.0), end: InputVector=(1.0, 0.0, 0.0), offset_angle: InputFloat=0.0, connect_center: InputBoolean=False, invert_arc: InputBoolean=False) -> 'Arc':
        return cls(mode='POINTS', resolution=resolution, start=start, middle=middle, end=end, offset_angle=offset_angle, connect_center=connect_center, invert_arc=invert_arc)

    @classmethod
    def radius(cls, resolution: InputInteger=16, radius: InputFloat=1.0, start_angle: InputFloat=0.0, sweep_angle: InputFloat=7 * math.pi / 4, connect_center: InputBoolean=False, invert_arc: InputBoolean=False) -> 'Arc':
        return cls(mode='RADIUS', resolution=resolution, radius=radius, start_angle=start_angle, sweep_angle=sweep_angle, connect_center=connect_center, invert_arc=invert_arc)

    @property
    def mode(self) -> Literal['POINTS', 'RADIUS']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['POINTS', 'RADIUS']) -> None:
        set_property(self.node, 'mode', value)

class Bake(_BakeMixin, BaseNode):
    _bl_idname = 'GeometryNodeBake'

class BoundingBox(BaseNode):
    _bl_idname = 'GeometryNodeBoundBox'

    def __init__(self, geometry: InputGeometry=None, use_radius: InputBoolean=True):
        super().__init__()
        key_args = {'Geometry': geometry, 'Use Radius': use_radius}
        self._establish_links(**key_args)

class BezierSegment(BaseNode):
    _bl_idname = 'GeometryNodeCurvePrimitiveBezierSegment'

    def __init__(self, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), start_handle: InputVector=(-0.5, 0.5, 0.0), end_handle: InputVector=(0.0, 0.0, 0.0), end: InputVector=(1.0, 0.0, 0.0), *, mode: Literal['POSITION', 'OFFSET']='POSITION'):
        super().__init__()
        key_args = {'Resolution': resolution, 'Start': start, 'Start Handle': start_handle, 'End Handle': end_handle, 'End': end}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def position(cls, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), start_handle: InputVector=(-0.5, 0.5, 0.0), end_handle: InputVector=(0.0, 0.0, 0.0), end: InputVector=(1.0, 0.0, 0.0)) -> 'BezierSegment':
        return cls(mode='POSITION', resolution=resolution, start=start, start_handle=start_handle, end_handle=end_handle, end=end)

    @classmethod
    def offset(cls, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), start_handle: InputVector=(-0.5, 0.5, 0.0), end_handle: InputVector=(0.0, 0.0, 0.0), end: InputVector=(1.0, 0.0, 0.0)) -> 'BezierSegment':
        return cls(mode='OFFSET', resolution=resolution, start=start, start_handle=start_handle, end_handle=end_handle, end=end)

    @property
    def mode(self) -> Literal['POSITION', 'OFFSET']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['POSITION', 'OFFSET']) -> None:
        set_property(self.node, 'mode', value)

class Cone(BaseNode):
    _bl_idname = 'GeometryNodeMeshCone'

    def __init__(self, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius_top: InputFloat=0.0, radius_bottom: InputFloat=1.0, depth: InputFloat=2.0, *, fill_type: Literal['NONE', 'NGON', 'TRIANGLE_FAN']='NGON'):
        super().__init__()
        key_args = {'Vertices': vertices, 'Side Segments': side_segments, 'Fill Segments': fill_segments, 'Radius Top': radius_top, 'Radius Bottom': radius_bottom, 'Depth': depth}
        self.fill_type = fill_type
        self._establish_links(**key_args)

    @classmethod
    def none(cls, vertices: InputInteger=32, side_segments: InputInteger=1, radius_top: InputFloat=0.0, radius_bottom: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cone':
        return cls(fill_type='NONE', vertices=vertices, side_segments=side_segments, radius_top=radius_top, radius_bottom=radius_bottom, depth=depth)

    @classmethod
    def n_gon(cls, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius_top: InputFloat=0.0, radius_bottom: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cone':
        return cls(fill_type='NGON', vertices=vertices, side_segments=side_segments, fill_segments=fill_segments, radius_top=radius_top, radius_bottom=radius_bottom, depth=depth)

    @classmethod
    def triangles(cls, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius_top: InputFloat=0.0, radius_bottom: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cone':
        return cls(fill_type='TRIANGLE_FAN', vertices=vertices, side_segments=side_segments, fill_segments=fill_segments, radius_top=radius_top, radius_bottom=radius_bottom, depth=depth)

    @property
    def fill_type(self) -> Literal['NONE', 'NGON', 'TRIANGLE_FAN']:
        return self.node.fill_type

    @fill_type.setter
    def fill_type(self, value: Literal['NONE', 'NGON', 'TRIANGLE_FAN']) -> None:
        set_property(self.node, 'fill_type', value)

class ConvexHull(BaseNode):
    _bl_idname = 'GeometryNodeConvexHull'

    def __init__(self, geometry: InputGeometry=None):
        super().__init__()
        key_args = {'Geometry': geometry}
        self._establish_links(**key_args)

class Cube(BaseNode):
    _bl_idname = 'GeometryNodeMeshCube'

    def __init__(self, size: InputVector=(1.0, 1.0, 1.0), vertices_x: InputInteger=2, vertices_y: InputInteger=2, vertices_z: InputInteger=2):
        super().__init__()
        key_args = {'Size': size, 'Vertices X': vertices_x, 'Vertices Y': vertices_y, 'Vertices Z': vertices_z}
        self._establish_links(**key_args)

class CurveCircle(BaseNode):
    _bl_idname = 'GeometryNodeCurvePrimitiveCircle'

    def __init__(self, resolution: InputInteger=32, point_1: InputVector=(-1.0, 0.0, 0.0), point_2: InputVector=(0.0, 1.0, 0.0), point_3: InputVector=(1.0, 0.0, 0.0), radius: InputFloat=1.0, *, mode: Literal['POINTS', 'RADIUS']='RADIUS'):
        super().__init__()
        key_args = {'Resolution': resolution, 'Point 1': point_1, 'Point 2': point_2, 'Point 3': point_3, 'Radius': radius}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def points(cls, resolution: InputInteger=32, point_1: InputVector=(-1.0, 0.0, 0.0), point_2: InputVector=(0.0, 1.0, 0.0), point_3: InputVector=(1.0, 0.0, 0.0)) -> 'CurveCircle':
        return cls(mode='POINTS', resolution=resolution, point_1=point_1, point_2=point_2, point_3=point_3)

    @classmethod
    def radius(cls, resolution: InputInteger=32, radius: InputFloat=1.0) -> 'CurveCircle':
        return cls(mode='RADIUS', resolution=resolution, radius=radius)

    @property
    def mode(self) -> Literal['POINTS', 'RADIUS']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['POINTS', 'RADIUS']) -> None:
        set_property(self.node, 'mode', value)

class CurveLength(BaseNode):
    _bl_idname = 'GeometryNodeCurveLength'

    def __init__(self, curve: InputGeometry=None):
        super().__init__()
        key_args = {'Curve': curve}
        self._establish_links(**key_args)

class CurveLine(BaseNode):
    _bl_idname = 'GeometryNodeCurvePrimitiveLine'

    def __init__(self, start: InputVector=(0.0, 0.0, 0.0), end: InputVector=(0.0, 0.0, 1.0), direction: InputVector=(0.0, 0.0, 1.0), length: InputFloat=1.0, *, mode: Literal['POINTS', 'DIRECTION']='POINTS'):
        super().__init__()
        key_args = {'Start': start, 'End': end, 'Direction': direction, 'Length': length}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def points(cls, start: InputVector=(0.0, 0.0, 0.0), end: InputVector=(0.0, 0.0, 1.0)) -> 'CurveLine':
        return cls(mode='POINTS', start=start, end=end)

    @classmethod
    def direction(cls, start: InputVector=(0.0, 0.0, 0.0), direction: InputVector=(0.0, 0.0, 1.0), length: InputFloat=1.0) -> 'CurveLine':
        return cls(mode='DIRECTION', start=start, direction=direction, length=length)

    @property
    def mode(self) -> Literal['POINTS', 'DIRECTION']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['POINTS', 'DIRECTION']) -> None:
        set_property(self.node, 'mode', value)

class CurveToMesh(BaseNode):
    _bl_idname = 'GeometryNodeCurveToMesh'

    def __init__(self, curve: InputGeometry=None, profile_curve: InputGeometry=None, scale: InputFloat=1.0, fill_caps: InputBoolean=False):
        super().__init__()
        key_args = {'Curve': curve, 'Profile Curve': profile_curve, 'Scale': scale, 'Fill Caps': fill_caps}
        self._establish_links(**key_args)

class CurveToPoints(BaseNode):
    _bl_idname = 'GeometryNodeCurveToPoints'

    def __init__(self, curve: InputGeometry=None, count: InputInteger=10, length: InputFloat=0.1, *, mode: Literal['EVALUATED', 'COUNT', 'LENGTH']='COUNT'):
        super().__init__()
        key_args = {'Curve': curve, 'Count': count, 'Length': length}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def evaluated(cls, curve: InputGeometry=None) -> 'CurveToPoints':
        return cls(mode='EVALUATED', curve=curve)

    @classmethod
    def count(cls, curve: InputGeometry=None, count: InputInteger=10) -> 'CurveToPoints':
        return cls(mode='COUNT', curve=curve, count=count)

    @classmethod
    def length(cls, curve: InputGeometry=None, length: InputFloat=0.1) -> 'CurveToPoints':
        return cls(mode='LENGTH', curve=curve, length=length)

    @property
    def mode(self) -> Literal['EVALUATED', 'COUNT', 'LENGTH']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['EVALUATED', 'COUNT', 'LENGTH']) -> None:
        set_property(self.node, 'mode', value)

class CurvesToGreasePencil(BaseNode):
    _bl_idname = 'GeometryNodeCurvesToGreasePencil'

    def __init__(self, curves: InputGeometry=None, selection: InputBoolean=None, instances_as_layers: InputBoolean=True):
        super().__init__()
        key_args = {'Curves': curves, 'Selection': selection, 'Instances as Layers': instances_as_layers}
        self._establish_links(**key_args)

class Cylinder(BaseNode):
    _bl_idname = 'GeometryNodeMeshCylinder'

    def __init__(self, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius: InputFloat=1.0, depth: InputFloat=2.0, *, fill_type: Literal['NONE', 'NGON', 'TRIANGLE_FAN']='NGON'):
        super().__init__()
        key_args = {'Vertices': vertices, 'Side Segments': side_segments, 'Fill Segments': fill_segments, 'Radius': radius, 'Depth': depth}
        self.fill_type = fill_type
        self._establish_links(**key_args)

    @classmethod
    def none(cls, vertices: InputInteger=32, side_segments: InputInteger=1, radius: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cylinder':
        return cls(fill_type='NONE', vertices=vertices, side_segments=side_segments, radius=radius, depth=depth)

    @classmethod
    def n_gon(cls, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cylinder':
        return cls(fill_type='NGON', vertices=vertices, side_segments=side_segments, fill_segments=fill_segments, radius=radius, depth=depth)

    @classmethod
    def triangles(cls, vertices: InputInteger=32, side_segments: InputInteger=1, fill_segments: InputInteger=1, radius: InputFloat=1.0, depth: InputFloat=2.0) -> 'Cylinder':
        return cls(fill_type='TRIANGLE_FAN', vertices=vertices, side_segments=side_segments, fill_segments=fill_segments, radius=radius, depth=depth)

    @property
    def fill_type(self) -> Literal['NONE', 'NGON', 'TRIANGLE_FAN']:
        return self.node.fill_type

    @fill_type.setter
    def fill_type(self, value: Literal['NONE', 'NGON', 'TRIANGLE_FAN']) -> None:
        set_property(self.node, 'fill_type', value)

class DeformCurvesOnSurface(BaseNode):
    _bl_idname = 'GeometryNodeDeformCurvesOnSurface'

    def __init__(self, curves: InputGeometry=None):
        super().__init__()
        key_args = {'Curves': curves}
        self._establish_links(**key_args)

class DeleteGeometry(BaseNode):
    _bl_idname = 'GeometryNodeDeleteGeometry'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, *, mode: Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']='ALL', domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection}
        self.mode = mode
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def all(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT') -> 'DeleteGeometry':
        return cls(mode='ALL', geometry=geometry, selection=selection, domain=domain)

    @classmethod
    def only_edges_faces(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT') -> 'DeleteGeometry':
        return cls(mode='EDGE_FACE', geometry=geometry, selection=selection, domain=domain)

    @classmethod
    def only_faces(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT') -> 'DeleteGeometry':
        return cls(mode='ONLY_FACE', geometry=geometry, selection=selection, domain=domain)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, mode: Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']='ALL') -> 'DeleteGeometry':
        return cls(domain='POINT', geometry=geometry, selection=selection, mode=mode)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, mode: Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']='ALL') -> 'DeleteGeometry':
        return cls(domain='EDGE', geometry=geometry, selection=selection, mode=mode)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, *, mode: Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']='ALL') -> 'DeleteGeometry':
        return cls(domain='FACE', geometry=geometry, selection=selection, mode=mode)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'DeleteGeometry':
        return cls(domain='CURVE', geometry=geometry, selection=selection)

    @classmethod
    def instance(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'DeleteGeometry':
        return cls(domain='INSTANCE', geometry=geometry, selection=selection)

    @classmethod
    def layer(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'DeleteGeometry':
        return cls(domain='LAYER', geometry=geometry, selection=selection)

    @property
    def mode(self) -> Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['ALL', 'EDGE_FACE', 'ONLY_FACE']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

class DistributePointsOnFaces(BaseNode):
    _bl_idname = 'GeometryNodeDistributePointsOnFaces'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, distance_min: InputFloat=0.0, density_max: InputFloat=10.0, density: InputFloat=10.0, density_factor: InputFloat=1.0, seed: InputInteger=0, *, distribute_method: Literal['RANDOM', 'POISSON']='RANDOM', use_legacy_normal: bool=False):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Distance Min': distance_min, 'Density Max': density_max, 'Density': density, 'Density Factor': density_factor, 'Seed': seed}
        self.distribute_method = distribute_method
        self.use_legacy_normal = use_legacy_normal
        self._establish_links(**key_args)

    @property
    def distribute_method(self) -> Literal['RANDOM', 'POISSON']:
        return self.node.distribute_method

    @distribute_method.setter
    def distribute_method(self, value: Literal['RANDOM', 'POISSON']) -> None:
        set_property(self.node, 'distribute_method', value)

    @property
    def use_legacy_normal(self) -> bool:
        return self.node.use_legacy_normal

    @use_legacy_normal.setter
    def use_legacy_normal(self, value: bool) -> None:
        set_property(self.node, 'use_legacy_normal', value)

class DualMesh(BaseNode):
    _bl_idname = 'GeometryNodeDualMesh'

    def __init__(self, mesh: InputGeometry=None, keep_boundaries: InputBoolean=False):
        super().__init__()
        key_args = {'Mesh': mesh, 'Keep Boundaries': keep_boundaries}
        self._establish_links(**key_args)

class DuplicateElements(BaseNode):
    _bl_idname = 'GeometryNodeDuplicateElements'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1, *, domain: Literal['POINT', 'EDGE', 'FACE', 'SPLINE', 'LAYER', 'INSTANCE']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Amount': amount}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='POINT', geometry=geometry, selection=selection, amount=amount)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='EDGE', geometry=geometry, selection=selection, amount=amount)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='FACE', geometry=geometry, selection=selection, amount=amount)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='SPLINE', geometry=geometry, selection=selection, amount=amount)

    @classmethod
    def layer(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='LAYER', geometry=geometry, selection=selection, amount=amount)

    @classmethod
    def instance(cls, geometry: InputGeometry=None, selection: InputBoolean=None, amount: InputInteger=1) -> 'DuplicateElements':
        return cls(domain='INSTANCE', geometry=geometry, selection=selection, amount=amount)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'SPLINE', 'LAYER', 'INSTANCE']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'SPLINE', 'LAYER', 'INSTANCE']) -> None:
        set_property(self.node, 'domain', value)

class EdgePathsToCurves(BaseNode):
    _bl_idname = 'GeometryNodeEdgePathsToCurves'

    def __init__(self, mesh: InputGeometry=None, start_vertices: InputBoolean=None, next_vertex_index: InputInteger=None):
        super().__init__()
        key_args = {'Mesh': mesh, 'Start Vertices': start_vertices, 'Next Vertex Index': next_vertex_index}
        self._establish_links(**key_args)

class ExtrudeMesh(BaseNode):
    _bl_idname = 'GeometryNodeExtrudeMesh'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, offset: InputVector=None, offset_scale: InputFloat=1.0, individual: InputBoolean=True, *, mode: Literal['VERTICES', 'EDGES', 'FACES']='FACES'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Offset': offset, 'Offset Scale': offset_scale, 'Individual': individual}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def vertices(cls, mesh: InputGeometry=None, selection: InputBoolean=None, offset: InputVector=None, offset_scale: InputFloat=1.0) -> 'ExtrudeMesh':
        return cls(mode='VERTICES', mesh=mesh, selection=selection, offset=offset, offset_scale=offset_scale)

    @classmethod
    def edges(cls, mesh: InputGeometry=None, selection: InputBoolean=None, offset: InputVector=None, offset_scale: InputFloat=1.0) -> 'ExtrudeMesh':
        return cls(mode='EDGES', mesh=mesh, selection=selection, offset=offset, offset_scale=offset_scale)

    @classmethod
    def faces(cls, mesh: InputGeometry=None, selection: InputBoolean=None, offset: InputVector=None, offset_scale: InputFloat=1.0, individual: InputBoolean=True) -> 'ExtrudeMesh':
        return cls(mode='FACES', mesh=mesh, selection=selection, offset=offset, offset_scale=offset_scale, individual=individual)

    @property
    def mode(self) -> Literal['VERTICES', 'EDGES', 'FACES']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['VERTICES', 'EDGES', 'FACES']) -> None:
        set_property(self.node, 'mode', value)

class FillCurve(BaseNode):
    _bl_idname = 'GeometryNodeFillCurve'

    def __init__(self, curve: InputGeometry=None, group_id: InputInteger=None, mode: InputMenu | Literal['Triangles', 'N-gons']='Triangles', fill_rule: InputMenu | Literal['Even-Odd', 'Non-Zero']='Even-Odd'):
        super().__init__()
        key_args = {'Curve': curve, 'Group ID': group_id, 'Mode': mode, 'Fill Rule': fill_rule}
        self._establish_links(**key_args)

class FilletCurve(BaseNode):
    _bl_idname = 'GeometryNodeFilletCurve'

    def __init__(self, curve: InputGeometry=None, radius: InputFloat=0.25, limit_radius: InputBoolean=False, mode: InputMenu | Literal['Bézier', 'Poly']='Bézier', count: InputInteger=1):
        super().__init__()
        key_args = {'Curve': curve, 'Radius': radius, 'Limit Radius': limit_radius, 'Mode': mode, 'Count': count}
        self._establish_links(**key_args)

class FlipFaces(BaseNode):
    _bl_idname = 'GeometryNodeFlipFaces'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection}
        self._establish_links(**key_args)

class GeometryProximity(BaseNode):
    _bl_idname = 'GeometryNodeProximity'

    def __init__(self, target: InputGeometry=None, group_id: InputInteger=None, source_position: InputVector=None, sample_group_id: InputInteger=None, *, target_element: Literal['POINTS', 'EDGES', 'FACES']='FACES'):
        super().__init__()
        key_args = {'Target': target, 'Group ID': group_id, 'Source Position': source_position, 'Sample Group ID': sample_group_id}
        self.target_element = target_element
        self._establish_links(**key_args)

    @property
    def target_element(self) -> Literal['POINTS', 'EDGES', 'FACES']:
        return self.node.target_element

    @target_element.setter
    def target_element(self, value: Literal['POINTS', 'EDGES', 'FACES']) -> None:
        set_property(self.node, 'target_element', value)

class GetGeometryBundle(BaseNode):
    _bl_idname = 'GeometryNodeGetGeometryBundle'

    def __init__(self, geometry: InputGeometry=None, remove: InputBoolean=False):
        super().__init__()
        key_args = {'Geometry': geometry, 'Remove': remove}
        self._establish_links(**key_args)

class GetGeometryComponent(BaseNode):
    _bl_idname = 'GeometryNodeGetGeometryComponent'

    def __init__(self, geometry: InputGeometry=None, type: InputMenu | Literal['Mesh', 'Point Cloud', 'Curve', 'Instances', 'Grease Pencil', 'Volume']='Mesh', remove: InputBoolean=True):
        super().__init__()
        key_args = {'Geometry': geometry, 'Type': type, 'Remove': remove}
        self._establish_links(**key_args)

    @classmethod
    def mesh(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Mesh')

    @classmethod
    def point_cloud(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Point Cloud')

    @classmethod
    def curve(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Curve')

    @classmethod
    def instances(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Instances')

    @classmethod
    def grease_pencil(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Grease Pencil')

    @classmethod
    def volume(cls, geometry: InputGeometry=None, remove: InputBoolean=True) -> 'GetGeometryComponent':
        return cls(geometry=geometry, remove=remove, type='Volume')

class GreasePencilToCurves(BaseNode):
    _bl_idname = 'GeometryNodeGreasePencilToCurves'

    def __init__(self, grease_pencil: InputGeometry=None, selection: InputBoolean=None, layers_as_instances: InputBoolean=True):
        super().__init__()
        key_args = {'Grease Pencil': grease_pencil, 'Selection': selection, 'Layers as Instances': layers_as_instances}
        self._establish_links(**key_args)

class Grid(BaseNode):
    _bl_idname = 'GeometryNodeMeshGrid'

    def __init__(self, size_x: InputFloat=1.0, size_y: InputFloat=1.0, vertices_x: InputInteger=3, vertices_y: InputInteger=3):
        super().__init__()
        key_args = {'Size X': size_x, 'Size Y': size_y, 'Vertices X': vertices_x, 'Vertices Y': vertices_y}
        self._establish_links(**key_args)

class IcoSphere(BaseNode):
    _bl_idname = 'GeometryNodeMeshIcoSphere'

    def __init__(self, radius: InputFloat=1.0, subdivisions: InputInteger=1):
        super().__init__()
        key_args = {'Radius': radius, 'Subdivisions': subdivisions}
        self._establish_links(**key_args)

class InstanceOnPoints(BaseNode):
    _bl_idname = 'GeometryNodeInstanceOnPoints'

    def __init__(self, points: InputGeometry=None, selection: InputBoolean=None, instance: InputGeometry=None, pick_instance: InputBoolean=False, instance_index: InputInteger=None, rotation: InputRotation=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0)):
        super().__init__()
        key_args = {'Points': points, 'Selection': selection, 'Instance': instance, 'Pick Instance': pick_instance, 'Instance Index': instance_index, 'Rotation': rotation, 'Scale': scale}
        self._establish_links(**key_args)

class InstancesToPoints(BaseNode):
    _bl_idname = 'GeometryNodeInstancesToPoints'

    def __init__(self, instances: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05):
        super().__init__()
        key_args = {'Instances': instances, 'Selection': selection, 'Position': position, 'Radius': radius}
        self._establish_links(**key_args)

class InterpolateCurves(BaseNode):
    _bl_idname = 'GeometryNodeInterpolateCurves'

    def __init__(self, guide_curves: InputGeometry=None, guide_up: InputVector=None, guide_group_id: InputInteger=None, points: InputGeometry=None, point_up: InputVector=None, point_group_id: InputInteger=None, max_neighbors: InputInteger=4):
        super().__init__()
        key_args = {'Guide Curves': guide_curves, 'Guide Up': guide_up, 'Guide Group ID': guide_group_id, 'Points': points, 'Point Up': point_up, 'Point Group ID': point_group_id, 'Max Neighbors': max_neighbors}
        self._establish_links(**key_args)

class MaterialSelection(BaseNode):
    _bl_idname = 'GeometryNodeMaterialSelection'

    def __init__(self, material: InputMaterial=None):
        super().__init__()
        key_args = {'Material': material}
        self._establish_links(**key_args)

class MergeLayers(BaseNode):
    _bl_idname = 'GeometryNodeMergeLayers'

    def __init__(self, grease_pencil: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, *, mode: Literal['MERGE_BY_NAME', 'MERGE_BY_ID']='MERGE_BY_NAME'):
        super().__init__()
        key_args = {'Grease Pencil': grease_pencil, 'Selection': selection, 'Group ID': group_id}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def by_name(cls, grease_pencil: InputGeometry=None, selection: InputBoolean=None) -> 'MergeLayers':
        return cls(mode='MERGE_BY_NAME', grease_pencil=grease_pencil, selection=selection)

    @classmethod
    def by_group_id(cls, grease_pencil: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'MergeLayers':
        return cls(mode='MERGE_BY_ID', grease_pencil=grease_pencil, selection=selection, group_id=group_id)

    @property
    def mode(self) -> Literal['MERGE_BY_NAME', 'MERGE_BY_ID']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['MERGE_BY_NAME', 'MERGE_BY_ID']) -> None:
        set_property(self.node, 'mode', value)

class MergePoints(BaseNode):
    _bl_idname = 'GeometryNodeMergePoints'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, merge_id: InputInteger=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Merge ID': merge_id}
        self._establish_links(**key_args)

class MergeByDistance(BaseNode):
    _bl_idname = 'GeometryNodeMergeByDistance'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, mode: InputMenu | Literal['All', 'Connected']='All', distance: InputFloat=0.001):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Mode': mode, 'Distance': distance}
        self._establish_links(**key_args)

class MeshBevel(BaseNode):
    _bl_idname = 'GeometryNodeMeshBevel'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, affect_kind: InputMenu | Literal['Vertices', 'Edges']='Edges', start_left_offset: InputFloat=0.1, start_right_offset: InputFloat=0.1, end_left_offset: InputFloat=0.1, end_right_offset: InputFloat=0.1, offset: InputFloat=0.1, miter: InputBoolean=False, spread: InputFloat=0.1, segments: InputInteger=1, shape: InputFloat=0.5, profile: InputGeometry=None):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Affect Kind': affect_kind, 'Start Left Offset': start_left_offset, 'Start Right Offset': start_right_offset, 'End Left Offset': end_left_offset, 'End Right Offset': end_right_offset, 'Offset': offset, 'Miter': miter, 'Spread': spread, 'Segments': segments, 'Shape': shape, 'Profile': profile}
        self._establish_links(**key_args)

class MeshCircle(BaseNode):
    _bl_idname = 'GeometryNodeMeshCircle'

    def __init__(self, vertices: InputInteger=32, radius: InputFloat=1.0, *, fill_type: Literal['NONE', 'NGON', 'TRIANGLE_FAN']='NONE'):
        super().__init__()
        key_args = {'Vertices': vertices, 'Radius': radius}
        self.fill_type = fill_type
        self._establish_links(**key_args)

    @classmethod
    def none(cls, vertices: InputInteger=32, radius: InputFloat=1.0) -> 'MeshCircle':
        return cls(fill_type='NONE', vertices=vertices, radius=radius)

    @classmethod
    def n_gon(cls, vertices: InputInteger=32, radius: InputFloat=1.0) -> 'MeshCircle':
        return cls(fill_type='NGON', vertices=vertices, radius=radius)

    @classmethod
    def triangles(cls, vertices: InputInteger=32, radius: InputFloat=1.0) -> 'MeshCircle':
        return cls(fill_type='TRIANGLE_FAN', vertices=vertices, radius=radius)

    @property
    def fill_type(self) -> Literal['NONE', 'NGON', 'TRIANGLE_FAN']:
        return self.node.fill_type

    @fill_type.setter
    def fill_type(self, value: Literal['NONE', 'NGON', 'TRIANGLE_FAN']) -> None:
        set_property(self.node, 'fill_type', value)

class MeshLine(BaseNode):
    _bl_idname = 'GeometryNodeMeshLine'

    def __init__(self, count: InputInteger=10, resolution: InputFloat=1.0, start_location: InputVector=(0.0, 0.0, 0.0), offset: InputVector=(0.0, 0.0, 1.0), *, mode: Literal['OFFSET', 'END_POINTS']='OFFSET', count_mode: Literal['TOTAL', 'RESOLUTION']='TOTAL'):
        super().__init__()
        key_args = {'Count': count, 'Resolution': resolution, 'Start Location': start_location, 'Offset': offset}
        self.mode = mode
        self.count_mode = count_mode
        self._establish_links(**key_args)

    @classmethod
    def offset(cls, count: InputInteger=10, start_location: InputVector=(0.0, 0.0, 0.0), offset: InputVector=(0.0, 0.0, 1.0)) -> 'MeshLine':
        return cls(mode='OFFSET', count=count, start_location=start_location, offset=offset)

    @classmethod
    def end_points(cls, count: InputInteger=10, start_location: InputVector=(0.0, 0.0, 0.0), offset: InputVector=(0.0, 0.0, 1.0), *, count_mode: Literal['TOTAL', 'RESOLUTION']='TOTAL') -> 'MeshLine':
        return cls(mode='END_POINTS', count=count, start_location=start_location, offset=offset, count_mode=count_mode)

    @property
    def mode(self) -> Literal['OFFSET', 'END_POINTS']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['OFFSET', 'END_POINTS']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def count_mode(self) -> Literal['TOTAL', 'RESOLUTION']:
        return self.node.count_mode

    @count_mode.setter
    def count_mode(self, value: Literal['TOTAL', 'RESOLUTION']) -> None:
        set_property(self.node, 'count_mode', value)

class MeshToCurve(BaseNode):
    _bl_idname = 'GeometryNodeMeshToCurve'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, *, mode: Literal['EDGES', 'FACES']='EDGES'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def edges(cls, mesh: InputGeometry=None, selection: InputBoolean=None) -> 'MeshToCurve':
        return cls(mode='EDGES', mesh=mesh, selection=selection)

    @classmethod
    def faces(cls, mesh: InputGeometry=None, selection: InputBoolean=None) -> 'MeshToCurve':
        return cls(mode='FACES', mesh=mesh, selection=selection)

    @property
    def mode(self) -> Literal['EDGES', 'FACES']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['EDGES', 'FACES']) -> None:
        set_property(self.node, 'mode', value)

class MeshToPoints(BaseNode):
    _bl_idname = 'GeometryNodeMeshToPoints'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05, *, mode: Literal['VERTICES', 'EDGES', 'FACES', 'CORNERS']='VERTICES'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Position': position, 'Radius': radius}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def vertices(cls, mesh: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05) -> 'MeshToPoints':
        return cls(mode='VERTICES', mesh=mesh, selection=selection, position=position, radius=radius)

    @classmethod
    def edges(cls, mesh: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05) -> 'MeshToPoints':
        return cls(mode='EDGES', mesh=mesh, selection=selection, position=position, radius=radius)

    @classmethod
    def faces(cls, mesh: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05) -> 'MeshToPoints':
        return cls(mode='FACES', mesh=mesh, selection=selection, position=position, radius=radius)

    @classmethod
    def corners(cls, mesh: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, radius: InputFloat=0.05) -> 'MeshToPoints':
        return cls(mode='CORNERS', mesh=mesh, selection=selection, position=position, radius=radius)

    @property
    def mode(self) -> Literal['VERTICES', 'EDGES', 'FACES', 'CORNERS']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['VERTICES', 'EDGES', 'FACES', 'CORNERS']) -> None:
        set_property(self.node, 'mode', value)

class Points(BaseNode):
    _bl_idname = 'GeometryNodePoints'

    def __init__(self, count: InputInteger=1, position: InputVector=(0.0, 0.0, 0.0), radius: InputFloat=0.1):
        super().__init__()
        key_args = {'Count': count, 'Position': position, 'Radius': radius}
        self._establish_links(**key_args)

class PointsToCurves(BaseNode):
    _bl_idname = 'GeometryNodePointsToCurves'

    def __init__(self, points: InputGeometry=None, curve_group_id: InputInteger=None, weight: InputFloat=None):
        super().__init__()
        key_args = {'Points': points, 'Curve Group ID': curve_group_id, 'Weight': weight}
        self._establish_links(**key_args)

class PointsToVertices(BaseNode):
    _bl_idname = 'GeometryNodePointsToVertices'

    def __init__(self, points: InputGeometry=None, selection: InputBoolean=None):
        super().__init__()
        key_args = {'Points': points, 'Selection': selection}
        self._establish_links(**key_args)

class QuadraticBezier(BaseNode):
    _bl_idname = 'GeometryNodeCurveQuadraticBezier'

    def __init__(self, resolution: InputInteger=16, start: InputVector=(-1.0, 0.0, 0.0), middle: InputVector=(0.0, 2.0, 0.0), end: InputVector=(1.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Resolution': resolution, 'Start': start, 'Middle': middle, 'End': end}
        self._establish_links(**key_args)

class Quadrilateral(BaseNode):
    _bl_idname = 'GeometryNodeCurvePrimitiveQuadrilateral'

    def __init__(self, width: InputFloat=2.0, height: InputFloat=2.0, bottom_width: InputFloat=4.0, top_width: InputFloat=2.0, offset: InputFloat=1.0, bottom_height: InputFloat=3.0, top_height: InputFloat=1.0, point_1: InputVector=(-1.0, -1.0, 0.0), point_2: InputVector=(1.0, -1.0, 0.0), point_3: InputVector=(1.0, 1.0, 0.0), point_4: InputVector=(-1.0, 1.0, 0.0), *, mode: Literal['RECTANGLE', 'PARALLELOGRAM', 'TRAPEZOID', 'KITE', 'POINTS']='RECTANGLE'):
        super().__init__()
        key_args = {'Width': width, 'Height': height, 'Bottom Width': bottom_width, 'Top Width': top_width, 'Offset': offset, 'Bottom Height': bottom_height, 'Top Height': top_height, 'Point 1': point_1, 'Point 2': point_2, 'Point 3': point_3, 'Point 4': point_4}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def rectangle(cls, width: InputFloat=2.0, height: InputFloat=2.0) -> 'Quadrilateral':
        return cls(mode='RECTANGLE', width=width, height=height)

    @classmethod
    def parallelogram(cls, width: InputFloat=2.0, height: InputFloat=2.0, offset: InputFloat=1.0) -> 'Quadrilateral':
        return cls(mode='PARALLELOGRAM', width=width, height=height, offset=offset)

    @classmethod
    def trapezoid(cls, height: InputFloat=2.0, bottom_width: InputFloat=4.0, top_width: InputFloat=2.0, offset: InputFloat=1.0) -> 'Quadrilateral':
        return cls(mode='TRAPEZOID', height=height, bottom_width=bottom_width, top_width=top_width, offset=offset)

    @classmethod
    def kite(cls, width: InputFloat=2.0, bottom_height: InputFloat=3.0, top_height: InputFloat=1.0) -> 'Quadrilateral':
        return cls(mode='KITE', width=width, bottom_height=bottom_height, top_height=top_height)

    @classmethod
    def points(cls, point_1: InputVector=(-1.0, -1.0, 0.0), point_2: InputVector=(1.0, -1.0, 0.0), point_3: InputVector=(1.0, 1.0, 0.0), point_4: InputVector=(-1.0, 1.0, 0.0)) -> 'Quadrilateral':
        return cls(mode='POINTS', point_1=point_1, point_2=point_2, point_3=point_3, point_4=point_4)

    @property
    def mode(self) -> Literal['RECTANGLE', 'PARALLELOGRAM', 'TRAPEZOID', 'KITE', 'POINTS']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['RECTANGLE', 'PARALLELOGRAM', 'TRAPEZOID', 'KITE', 'POINTS']) -> None:
        set_property(self.node, 'mode', value)

class Raycast(BaseNode):
    _bl_idname = 'GeometryNodeRaycast'

    def __init__(self, target_geometry: InputGeometry=None, attribute: InputAny=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Target Geometry': target_geometry, 'Attribute': attribute, 'Interpolation': interpolation, 'Source Position': source_position, 'Ray Direction': ray_direction, 'Ray Length': ray_length}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, target_geometry: InputGeometry=None, attribute: InputFloat=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[FloatSocket]':
        return Raycast(data_type='FLOAT', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def integer(cls, target_geometry: InputGeometry=None, attribute: InputInteger=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[IntegerSocket]':
        return Raycast(data_type='INT', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def boolean(cls, target_geometry: InputGeometry=None, attribute: InputBoolean=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[BooleanSocket]':
        return Raycast(data_type='BOOLEAN', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def vector(cls, target_geometry: InputGeometry=None, attribute: InputVector=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[VectorSocket]':
        return Raycast(data_type='FLOAT_VECTOR', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def color(cls, target_geometry: InputGeometry=None, attribute: InputColor=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[ColorSocket]':
        return Raycast(data_type='FLOAT_COLOR', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def quaternion(cls, target_geometry: InputGeometry=None, attribute: InputRotation=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[RotationSocket]':
        return Raycast(data_type='QUATERNION', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @classmethod
    def matrix(cls, target_geometry: InputGeometry=None, attribute: InputMatrix=None, interpolation: InputMenu | Literal['Interpolated', 'Nearest']='Interpolated', source_position: InputVector=None, ray_direction: InputVector=(0.0, 0.0, -1.0), ray_length: InputFloat=100.0) -> 'Raycast[MatrixSocket]':
        return Raycast(data_type='FLOAT4X4', target_geometry=target_geometry, attribute=attribute, interpolation=interpolation, source_position=source_position, ray_direction=ray_direction, ray_length=ray_length)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class RealizeInstances(BaseNode):
    _bl_idname = 'GeometryNodeRealizeInstances'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, realize_all: InputBoolean=True, depth: InputInteger=0, *, realize_to_point_domain: bool=False):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Realize All': realize_all, 'Depth': depth}
        self.realize_to_point_domain = realize_to_point_domain
        self._establish_links(**key_args)

    @property
    def realize_to_point_domain(self) -> bool:
        return self.node.realize_to_point_domain

    @realize_to_point_domain.setter
    def realize_to_point_domain(self, value: bool) -> None:
        set_property(self.node, 'realize_to_point_domain', value)

class RenameAttribute(BaseNode):
    _bl_idname = 'GeometryNodeRenameAttribute'

    def __init__(self, geometry: InputGeometry=None, mode: InputMenu | Literal['Single', 'Prefix']='Single', old: InputString='', new: InputString='', overwrite: InputBoolean=False):
        super().__init__()
        key_args = {'Geometry': geometry, 'Mode': mode, 'Old': old, 'New': new, 'Overwrite': overwrite}
        self._establish_links(**key_args)

class ReplaceMaterial(BaseNode):
    _bl_idname = 'GeometryNodeReplaceMaterial'

    def __init__(self, geometry: InputGeometry=None, old: InputMaterial=None, new: InputMaterial=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Old': old, 'New': new}
        self._establish_links(**key_args)

class ResampleCurve(BaseNode):
    _bl_idname = 'GeometryNodeResampleCurve'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, mode: InputMenu | Literal['Evaluated', 'Count', 'Length']='Count', count: InputInteger=10, length: InputFloat=0.1, *, keep_last_segment: bool=False):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Mode': mode, 'Count': count, 'Length': length}
        self.keep_last_segment = keep_last_segment
        self._establish_links(**key_args)

    @property
    def keep_last_segment(self) -> bool:
        return self.node.keep_last_segment

    @keep_last_segment.setter
    def keep_last_segment(self, value: bool) -> None:
        set_property(self.node, 'keep_last_segment', value)

class ReverseCurve(BaseNode):
    _bl_idname = 'GeometryNodeReverseCurve'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection}
        self._establish_links(**key_args)

class RotateInstances(BaseNode):
    _bl_idname = 'GeometryNodeRotateInstances'

    def __init__(self, instances: InputGeometry=None, selection: InputBoolean=None, rotation: InputRotation=(0.0, 0.0, 0.0), pivot_point: InputVector=(0.0, 0.0, 0.0), local_space: InputBoolean=True):
        super().__init__()
        key_args = {'Instances': instances, 'Selection': selection, 'Rotation': rotation, 'Pivot Point': pivot_point, 'Local Space': local_space}
        self._establish_links(**key_args)

class SampleNearest(BaseNode):
    _bl_idname = 'GeometryNodeSampleNearest'

    def __init__(self, geometry: InputGeometry=None, sample_position: InputVector=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CORNER']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Sample Position': sample_position}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, sample_position: InputVector=None) -> 'SampleNearest':
        return cls(domain='POINT', geometry=geometry, sample_position=sample_position)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, sample_position: InputVector=None) -> 'SampleNearest':
        return cls(domain='EDGE', geometry=geometry, sample_position=sample_position)

    @classmethod
    def face(cls, geometry: InputGeometry=None, sample_position: InputVector=None) -> 'SampleNearest':
        return cls(domain='FACE', geometry=geometry, sample_position=sample_position)

    @classmethod
    def face_corner(cls, geometry: InputGeometry=None, sample_position: InputVector=None) -> 'SampleNearest':
        return cls(domain='CORNER', geometry=geometry, sample_position=sample_position)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CORNER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CORNER']) -> None:
        set_property(self.node, 'domain', value)

class SampleNearestSurface(BaseNode):
    _bl_idname = 'GeometryNodeSampleNearestSurface'

    def __init__(self, mesh: InputGeometry=None, value: InputAny=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Value': value, 'Group ID': group_id, 'Sample Position': sample_position, 'Sample Group ID': sample_group_id}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, mesh: InputGeometry=None, value: InputFloat=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[FloatSocket]':
        return SampleNearestSurface(data_type='FLOAT', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def integer(cls, mesh: InputGeometry=None, value: InputInteger=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[IntegerSocket]':
        return SampleNearestSurface(data_type='INT', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def boolean(cls, mesh: InputGeometry=None, value: InputBoolean=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[BooleanSocket]':
        return SampleNearestSurface(data_type='BOOLEAN', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def vector(cls, mesh: InputGeometry=None, value: InputVector=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[VectorSocket]':
        return SampleNearestSurface(data_type='FLOAT_VECTOR', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def color(cls, mesh: InputGeometry=None, value: InputColor=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[ColorSocket]':
        return SampleNearestSurface(data_type='FLOAT_COLOR', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def quaternion(cls, mesh: InputGeometry=None, value: InputRotation=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[RotationSocket]':
        return SampleNearestSurface(data_type='QUATERNION', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @classmethod
    def matrix(cls, mesh: InputGeometry=None, value: InputMatrix=None, group_id: InputInteger=None, sample_position: InputVector=None, sample_group_id: InputInteger=None) -> 'SampleNearestSurface[MatrixSocket]':
        return SampleNearestSurface(data_type='FLOAT4X4', mesh=mesh, value=value, group_id=group_id, sample_position=sample_position, sample_group_id=sample_group_id)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SampleUVSurface(BaseNode):
    _bl_idname = 'GeometryNodeSampleUVSurface'

    def __init__(self, mesh: InputGeometry=None, value: InputAny=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0), *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Value': value, 'Source UV Map': source_uv_map, 'Sample UV': sample_uv}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, mesh: InputGeometry=None, value: InputFloat=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[FloatSocket]':
        return SampleUVSurface(data_type='FLOAT', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def integer(cls, mesh: InputGeometry=None, value: InputInteger=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[IntegerSocket]':
        return SampleUVSurface(data_type='INT', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def boolean(cls, mesh: InputGeometry=None, value: InputBoolean=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[BooleanSocket]':
        return SampleUVSurface(data_type='BOOLEAN', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def vector(cls, mesh: InputGeometry=None, value: InputVector=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[VectorSocket]':
        return SampleUVSurface(data_type='FLOAT_VECTOR', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def color(cls, mesh: InputGeometry=None, value: InputColor=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[ColorSocket]':
        return SampleUVSurface(data_type='FLOAT_COLOR', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def quaternion(cls, mesh: InputGeometry=None, value: InputRotation=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[RotationSocket]':
        return SampleUVSurface(data_type='QUATERNION', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @classmethod
    def matrix(cls, mesh: InputGeometry=None, value: InputMatrix=None, source_uv_map: InputVector=None, sample_uv: InputVector=(0.0, 0.0, 0.0)) -> 'SampleUVSurface[MatrixSocket]':
        return SampleUVSurface(data_type='FLOAT4X4', mesh=mesh, value=value, source_uv_map=source_uv_map, sample_uv=sample_uv)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ScaleElements(BaseNode):
    _bl_idname = 'GeometryNodeScaleElements'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, scale: InputFloat=1.0, center: InputVector=None, scale_mode: InputMenu | Literal['Uniform', 'Single Axis']='Uniform', axis: InputVector=(1.0, 0.0, 0.0), *, domain: Literal['FACE', 'EDGE']='FACE'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Scale': scale, 'Center': center, 'Scale Mode': scale_mode, 'Axis': axis}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, scale: InputFloat=1.0, center: InputVector=None, scale_mode: InputMenu | Literal['Uniform', 'Single Axis']='Uniform') -> 'ScaleElements':
        return cls(domain='FACE', geometry=geometry, selection=selection, scale=scale, center=center, scale_mode=scale_mode)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, scale: InputFloat=1.0, center: InputVector=None, scale_mode: InputMenu | Literal['Uniform', 'Single Axis']='Uniform') -> 'ScaleElements':
        return cls(domain='EDGE', geometry=geometry, selection=selection, scale=scale, center=center, scale_mode=scale_mode)

    @property
    def domain(self) -> Literal['FACE', 'EDGE']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['FACE', 'EDGE']) -> None:
        set_property(self.node, 'domain', value)

class ScaleInstances(BaseNode):
    _bl_idname = 'GeometryNodeScaleInstances'

    def __init__(self, instances: InputGeometry=None, selection: InputBoolean=None, scale: InputVector=(1.0, 1.0, 1.0), center: InputVector=(0.0, 0.0, 0.0), local_space: InputBoolean=True):
        super().__init__()
        key_args = {'Instances': instances, 'Selection': selection, 'Scale': scale, 'Center': center, 'Local Space': local_space}
        self._establish_links(**key_args)

class SeparateComponents(BaseNode):
    _bl_idname = 'GeometryNodeSeparateComponents'

    def __init__(self, geometry: InputGeometry=None):
        super().__init__()
        key_args = {'Geometry': geometry}
        self._establish_links(**key_args)

class SeparateGeometry(BaseNode):
    _bl_idname = 'GeometryNodeSeparateGeometry'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='POINT', geometry=geometry, selection=selection)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='EDGE', geometry=geometry, selection=selection)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='FACE', geometry=geometry, selection=selection)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='CURVE', geometry=geometry, selection=selection)

    @classmethod
    def instance(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='INSTANCE', geometry=geometry, selection=selection)

    @classmethod
    def layer(cls, geometry: InputGeometry=None, selection: InputBoolean=None) -> 'SeparateGeometry':
        return cls(domain='LAYER', geometry=geometry, selection=selection)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

class SetCurveNormal(BaseNode):
    _bl_idname = 'GeometryNodeSetCurveNormal'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, mode: InputMenu | Literal['Minimum Twist', 'Z Up', 'Free']='Minimum Twist', normal: InputVector=(0.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Mode': mode, 'Normal': normal}
        self._establish_links(**key_args)

class SetCurveRadius(BaseNode):
    _bl_idname = 'GeometryNodeSetCurveRadius'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, radius: InputFloat=0.005):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Radius': radius}
        self._establish_links(**key_args)

class SetCurveTilt(BaseNode):
    _bl_idname = 'GeometryNodeSetCurveTilt'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, tilt: InputFloat=0.0):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Tilt': tilt}
        self._establish_links(**key_args)

class SetFaceSet(BaseNode):
    _bl_idname = 'GeometryNodeToolSetFaceSet'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, face_set: InputInteger=None):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Face Set': face_set}
        self._establish_links(**key_args)

class SetGeometryBundle(BaseNode):
    _bl_idname = 'GeometryNodeSetGeometryBundle'

    def __init__(self, geometry: InputGeometry=None, bundle: InputBundle=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Bundle': bundle}
        self._establish_links(**key_args)

class SetGeometryName(BaseNode):
    _bl_idname = 'GeometryNodeSetGeometryName'

    def __init__(self, geometry: InputGeometry=None, name: InputString=''):
        super().__init__()
        key_args = {'Geometry': geometry, 'Name': name}
        self._establish_links(**key_args)

class SetGreasePencilColor(BaseNode):
    _bl_idname = 'GeometryNodeSetGreasePencilColor'

    def __init__(self, grease_pencil: InputGeometry=None, selection: InputBoolean=None, color: InputColor=(1.0, 1.0, 1.0, 1.0), opacity: InputFloat=1.0, *, mode: Literal['STROKE', 'FILL']='STROKE'):
        super().__init__()
        key_args = {'Grease Pencil': grease_pencil, 'Selection': selection, 'Color': color, 'Opacity': opacity}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def stroke(cls, grease_pencil: InputGeometry=None, selection: InputBoolean=None, color: InputColor=(1.0, 1.0, 1.0, 1.0), opacity: InputFloat=1.0) -> 'SetGreasePencilColor':
        return cls(mode='STROKE', grease_pencil=grease_pencil, selection=selection, color=color, opacity=opacity)

    @classmethod
    def fill(cls, grease_pencil: InputGeometry=None, selection: InputBoolean=None, color: InputColor=(1.0, 1.0, 1.0, 1.0), opacity: InputFloat=1.0) -> 'SetGreasePencilColor':
        return cls(mode='FILL', grease_pencil=grease_pencil, selection=selection, color=color, opacity=opacity)

    @property
    def mode(self) -> Literal['STROKE', 'FILL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['STROKE', 'FILL']) -> None:
        set_property(self.node, 'mode', value)

class SetGreasePencilDepth(BaseNode):
    _bl_idname = 'GeometryNodeSetGreasePencilDepth'

    def __init__(self, grease_pencil: InputGeometry=None, *, depth_order: Literal['2D', '3D']='2D'):
        super().__init__()
        key_args = {'Grease Pencil': grease_pencil}
        self.depth_order = depth_order
        self._establish_links(**key_args)

    @property
    def depth_order(self) -> Literal['2D', '3D']:
        return self.node.depth_order

    @depth_order.setter
    def depth_order(self, value: Literal['2D', '3D']) -> None:
        set_property(self.node, 'depth_order', value)

class SetGreasePencilSoftness(BaseNode):
    _bl_idname = 'GeometryNodeSetGreasePencilSoftness'

    def __init__(self, grease_pencil: InputGeometry=None, selection: InputBoolean=None, softness: InputFloat=0.0):
        super().__init__()
        key_args = {'Grease Pencil': grease_pencil, 'Selection': selection, 'Softness': softness}
        self._establish_links(**key_args)

class SetHandlePositions(BaseNode):
    _bl_idname = 'GeometryNodeSetCurveHandlePositions'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, offset: InputVector=(0.0, 0.0, 0.0), *, mode: Literal['LEFT', 'RIGHT']='LEFT'):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Position': position, 'Offset': offset}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def left(cls, curve: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, offset: InputVector=(0.0, 0.0, 0.0)) -> 'SetHandlePositions':
        return cls(mode='LEFT', curve=curve, selection=selection, position=position, offset=offset)

    @classmethod
    def right(cls, curve: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, offset: InputVector=(0.0, 0.0, 0.0)) -> 'SetHandlePositions':
        return cls(mode='RIGHT', curve=curve, selection=selection, position=position, offset=offset)

    @property
    def mode(self) -> Literal['LEFT', 'RIGHT']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['LEFT', 'RIGHT']) -> None:
        set_property(self.node, 'mode', value)

class SetHandleType(_HandleModeMixin, BaseNode):
    _bl_idname = 'GeometryNodeCurveSetHandles'

    @classmethod
    def free(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetHandleType':
        return cls(handle_type='FREE', curve=curve, selection=selection)

    @classmethod
    def auto(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetHandleType':
        return cls(handle_type='AUTO', curve=curve, selection=selection)

    @classmethod
    def vector(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetHandleType':
        return cls(handle_type='VECTOR', curve=curve, selection=selection)

    @classmethod
    def align(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetHandleType':
        return cls(handle_type='ALIGN', curve=curve, selection=selection)

    @property
    def handle_type(self) -> Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']:
        return self.node.handle_type

    @handle_type.setter
    def handle_type(self, value: Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']) -> None:
        set_property(self.node, 'handle_type', value)

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=True, *, left: bool=True, right: bool=True, handle_type: Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']='AUTO'):
        super().__init__()
        self.handle_type = handle_type
        self.left = left
        self.right = right
        self._establish_links(Curve=curve, Selection=selection)

class SetID(BaseNode):
    _bl_idname = 'GeometryNodeSetID'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, id: InputInteger=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'ID': id}
        self._establish_links(**key_args)

class SetInstanceTransform(BaseNode):
    _bl_idname = 'GeometryNodeSetInstanceTransform'

    def __init__(self, instances: InputGeometry=None, selection: InputBoolean=None, transform: InputMatrix=None):
        super().__init__()
        key_args = {'Instances': instances, 'Selection': selection, 'Transform': transform}
        self._establish_links(**key_args)

class SetMaterial(BaseNode):
    _bl_idname = 'GeometryNodeSetMaterial'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, material: InputMaterial=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Material': material}
        self._establish_links(**key_args)

class SetMaterialIndex(BaseNode):
    _bl_idname = 'GeometryNodeSetMaterialIndex'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, material_index: InputInteger=0):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Material Index': material_index}
        self._establish_links(**key_args)

class SetMeshNormal(BaseNode):
    _bl_idname = 'GeometryNodeSetMeshNormal'

    def __init__(self, mesh: InputGeometry=None, remove_custom: InputBoolean=True, edge_sharpness: InputBoolean=False, face_sharpness: InputBoolean=False, custom_normal: InputVector=None, *, mode: Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']='SHARPNESS', domain: Literal['POINT', 'FACE', 'CORNER']='POINT'):
        super().__init__()
        self.mode = mode
        self.domain = domain
        _all_args = {'Mesh': mesh, 'Remove Custom': remove_custom, 'Edge Sharpness': edge_sharpness, 'Face Sharpness': face_sharpness, 'Custom Normal': custom_normal}
        assert self.node.inputs is not None
        _socket_ids = {s.identifier for s in self.node.inputs}
        key_args = {k: v for k, v in _all_args.items() if k in _socket_ids}
        self._establish_links(**key_args)

    @classmethod
    def sharpness(cls, mesh: InputGeometry=None, remove_custom: InputBoolean=True, edge_sharpness: InputBoolean=False, face_sharpness: InputBoolean=False) -> 'SetMeshNormal':
        return cls(mode='SHARPNESS', mesh=mesh, remove_custom=remove_custom, edge_sharpness=edge_sharpness, face_sharpness=face_sharpness)

    @classmethod
    def free(cls, mesh: InputGeometry=None, custom_normal: InputVector=None, *, domain: Literal['POINT', 'FACE', 'CORNER']='POINT') -> 'SetMeshNormal':
        return cls(mode='FREE', mesh=mesh, custom_normal=custom_normal, domain=domain)

    @classmethod
    def tangent_space(cls, mesh: InputGeometry=None, custom_normal: InputVector=None) -> 'SetMeshNormal':
        return cls(mode='TANGENT_SPACE', mesh=mesh, custom_normal=custom_normal)

    @classmethod
    def point(cls, mesh: InputGeometry=None, remove_custom: InputBoolean=True, edge_sharpness: InputBoolean=False, face_sharpness: InputBoolean=False, *, mode: Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']='SHARPNESS') -> 'SetMeshNormal':
        return cls(domain='POINT', mesh=mesh, remove_custom=remove_custom, edge_sharpness=edge_sharpness, face_sharpness=face_sharpness, mode=mode)

    @classmethod
    def face(cls, mesh: InputGeometry=None, remove_custom: InputBoolean=True, edge_sharpness: InputBoolean=False, face_sharpness: InputBoolean=False, *, mode: Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']='SHARPNESS') -> 'SetMeshNormal':
        return cls(domain='FACE', mesh=mesh, remove_custom=remove_custom, edge_sharpness=edge_sharpness, face_sharpness=face_sharpness, mode=mode)

    @classmethod
    def face_corner(cls, mesh: InputGeometry=None, remove_custom: InputBoolean=True, edge_sharpness: InputBoolean=False, face_sharpness: InputBoolean=False, *, mode: Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']='SHARPNESS') -> 'SetMeshNormal':
        return cls(domain='CORNER', mesh=mesh, remove_custom=remove_custom, edge_sharpness=edge_sharpness, face_sharpness=face_sharpness, mode=mode)

    @property
    def mode(self) -> Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['SHARPNESS', 'FREE', 'TANGENT_SPACE']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def domain(self) -> Literal['POINT', 'FACE', 'CORNER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'FACE', 'CORNER']) -> None:
        set_property(self.node, 'domain', value)

class SetNURBSOrder(BaseNode):
    _bl_idname = 'GeometryNodeSetNURBSOrder'

    def __init__(self, curves: InputGeometry=None, selection: InputBoolean=None, order: InputInteger=4):
        super().__init__()
        key_args = {'Curves': curves, 'Selection': selection, 'Order': order}
        self._establish_links(**key_args)

class SetNURBSWeight(BaseNode):
    _bl_idname = 'GeometryNodeSetNURBSWeight'

    def __init__(self, curves: InputGeometry=None, selection: InputBoolean=None, weight: InputFloat=1.0):
        super().__init__()
        key_args = {'Curves': curves, 'Selection': selection, 'Weight': weight}
        self._establish_links(**key_args)

class SetPointRadius(BaseNode):
    _bl_idname = 'GeometryNodeSetPointRadius'

    def __init__(self, points: InputGeometry=None, selection: InputBoolean=None, radius: InputFloat=0.05):
        super().__init__()
        key_args = {'Points': points, 'Selection': selection, 'Radius': radius}
        self._establish_links(**key_args)

class SetPosition(BaseNode):
    _bl_idname = 'GeometryNodeSetPosition'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, position: InputVector=None, offset: InputVector=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Position': position, 'Offset': offset}
        self._establish_links(**key_args)

class SetSelection(BaseNode):
    _bl_idname = 'GeometryNodeToolSetSelection'

    def __init__(self, geometry: InputGeometry=None, selection: InputAny=True, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE']='POINT', selection_type: Literal['BOOLEAN', 'FLOAT']='BOOLEAN'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection}
        self.domain = domain
        self.selection_type = selection_type
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=True, *, selection_type: Literal['BOOLEAN', 'FLOAT']='BOOLEAN') -> 'SetSelection[BooleanSocket]':
        return SetSelection(domain='POINT', geometry=geometry, selection=selection, selection_type=selection_type)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=True, *, selection_type: Literal['BOOLEAN', 'FLOAT']='BOOLEAN') -> 'SetSelection[BooleanSocket]':
        return SetSelection(domain='EDGE', geometry=geometry, selection=selection, selection_type=selection_type)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=True, *, selection_type: Literal['BOOLEAN', 'FLOAT']='BOOLEAN') -> 'SetSelection[BooleanSocket]':
        return SetSelection(domain='FACE', geometry=geometry, selection=selection, selection_type=selection_type)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=True, *, selection_type: Literal['BOOLEAN', 'FLOAT']='BOOLEAN') -> 'SetSelection[BooleanSocket]':
        return SetSelection(domain='CURVE', geometry=geometry, selection=selection, selection_type=selection_type)

    @classmethod
    def boolean(cls, geometry: InputGeometry=None, selection: InputBoolean=True, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE']='POINT') -> 'SetSelection[BooleanSocket]':
        return SetSelection(selection_type='BOOLEAN', geometry=geometry, selection=selection, domain=domain)

    @classmethod
    def float(cls, geometry: InputGeometry=None, selection: InputFloat=1.0, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE']='POINT') -> 'SetSelection[FloatSocket]':
        return SetSelection(selection_type='FLOAT', geometry=geometry, selection=selection, domain=domain)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CURVE']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CURVE']) -> None:
        set_property(self.node, 'domain', value)

    @property
    def selection_type(self) -> Literal['BOOLEAN', 'FLOAT']:
        return self.node.selection_type

    @selection_type.setter
    def selection_type(self, value: Literal['BOOLEAN', 'FLOAT']) -> None:
        set_property(self.node, 'selection_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SetShadeSmooth(BaseNode):
    _bl_idname = 'GeometryNodeSetShadeSmooth'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, shade_smooth: InputBoolean=True, *, domain: Literal['EDGE', 'FACE']='FACE'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Shade Smooth': shade_smooth}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, shade_smooth: InputBoolean=True) -> 'SetShadeSmooth':
        return cls(domain='EDGE', geometry=geometry, selection=selection, shade_smooth=shade_smooth)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, shade_smooth: InputBoolean=True) -> 'SetShadeSmooth':
        return cls(domain='FACE', geometry=geometry, selection=selection, shade_smooth=shade_smooth)

    @property
    def domain(self) -> Literal['EDGE', 'FACE']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['EDGE', 'FACE']) -> None:
        set_property(self.node, 'domain', value)

class SetSplineCyclic(BaseNode):
    _bl_idname = 'GeometryNodeSetSplineCyclic'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, cyclic: InputBoolean=False):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Cyclic': cyclic}
        self._establish_links(**key_args)

class SetSplineResolution(BaseNode):
    _bl_idname = 'GeometryNodeSetSplineResolution'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, resolution: InputInteger=12):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Resolution': resolution}
        self._establish_links(**key_args)

class SetSplineType(BaseNode):
    _bl_idname = 'GeometryNodeCurveSplineType'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, *, spline_type: Literal['CATMULL_ROM', 'POLY', 'BEZIER', 'NURBS']='POLY'):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection}
        self.spline_type = spline_type
        self._establish_links(**key_args)

    @classmethod
    def catmull_rom(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetSplineType':
        return cls(spline_type='CATMULL_ROM', curve=curve, selection=selection)

    @classmethod
    def poly(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetSplineType':
        return cls(spline_type='POLY', curve=curve, selection=selection)

    @classmethod
    def bezier(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetSplineType':
        return cls(spline_type='BEZIER', curve=curve, selection=selection)

    @classmethod
    def nurbs(cls, curve: InputGeometry=None, selection: InputBoolean=None) -> 'SetSplineType':
        return cls(spline_type='NURBS', curve=curve, selection=selection)

    @property
    def spline_type(self) -> Literal['CATMULL_ROM', 'POLY', 'BEZIER', 'NURBS']:
        return self.node.spline_type

    @spline_type.setter
    def spline_type(self, value: Literal['CATMULL_ROM', 'POLY', 'BEZIER', 'NURBS']) -> None:
        set_property(self.node, 'spline_type', value)

class SortElements(BaseNode):
    _bl_idname = 'GeometryNodeSortElements'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Group ID': group_id, 'Sort Weight': sort_weight}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortElements':
        return cls(domain='POINT', geometry=geometry, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortElements':
        return cls(domain='EDGE', geometry=geometry, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortElements':
        return cls(domain='FACE', geometry=geometry, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortElements':
        return cls(domain='CURVE', geometry=geometry, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @classmethod
    def instance(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, sort_weight: InputFloat=None) -> 'SortElements':
        return cls(domain='INSTANCE', geometry=geometry, selection=selection, group_id=group_id, sort_weight=sort_weight)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE']) -> None:
        set_property(self.node, 'domain', value)

class Spiral(BaseNode):
    _bl_idname = 'GeometryNodeCurveSpiral'

    def __init__(self, resolution: InputInteger=32, rotations: InputFloat=2.0, start_radius: InputFloat=1.0, end_radius: InputFloat=2.0, height: InputFloat=2.0, reverse: InputBoolean=False):
        super().__init__()
        key_args = {'Resolution': resolution, 'Rotations': rotations, 'Start Radius': start_radius, 'End Radius': end_radius, 'Height': height, 'Reverse': reverse}
        self._establish_links(**key_args)

class SplitEdges(BaseNode):
    _bl_idname = 'GeometryNodeSplitEdges'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection}
        self._establish_links(**key_args)

class SplitToInstances(BaseNode):
    _bl_idname = 'GeometryNodeSplitToInstances'

    def __init__(self, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None, *, domain: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {'Geometry': geometry, 'Selection': selection, 'Group ID': group_id}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='POINT', geometry=geometry, selection=selection, group_id=group_id)

    @classmethod
    def edge(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='EDGE', geometry=geometry, selection=selection, group_id=group_id)

    @classmethod
    def face(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='FACE', geometry=geometry, selection=selection, group_id=group_id)

    @classmethod
    def spline(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='CURVE', geometry=geometry, selection=selection, group_id=group_id)

    @classmethod
    def instance(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='INSTANCE', geometry=geometry, selection=selection, group_id=group_id)

    @classmethod
    def layer(cls, geometry: InputGeometry=None, selection: InputBoolean=None, group_id: InputInteger=None) -> 'SplitToInstances':
        return cls(domain='LAYER', geometry=geometry, selection=selection, group_id=group_id)

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'CURVE', 'INSTANCE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

class Star(BaseNode):
    _bl_idname = 'GeometryNodeCurveStar'

    def __init__(self, points: InputInteger=8, inner_radius: InputFloat=1.0, outer_radius: InputFloat=2.0, twist: InputFloat=0.0):
        super().__init__()
        key_args = {'Points': points, 'Inner Radius': inner_radius, 'Outer Radius': outer_radius, 'Twist': twist}
        self._establish_links(**key_args)

class StringToCurves(BaseNode):
    _bl_idname = 'GeometryNodeStringToCurves'

    def __init__(self, string: InputString='', size: InputFloat=1.0, font: InputFont=None, align_x: InputMenu | Literal['Left', 'Center', 'Right', 'Justify', 'Flush']='Left', align_y: InputMenu | Literal['Top', 'Top Baseline', 'Middle', 'Bottom Baseline', 'Bottom']='Top Baseline', pivot_point: InputMenu | Literal['Midpoint', 'Top Left', 'Top Center', 'Top Right', 'Bottom Left', 'Bottom Center', 'Bottom Right']='Midpoint', character_spacing: InputFloat=1.0, word_spacing: InputFloat=1.0, line_spacing: InputFloat=1.0, overflow: InputMenu | Literal['Overflow', 'Scale To Fit', 'Truncate']='Overflow', text_box_width: InputFloat=0.0, text_box_height: InputFloat=0.0):
        super().__init__()
        key_args = {'String': string, 'Size': size, 'Font': font, 'Align X': align_x, 'Align Y': align_y, 'Pivot Point': pivot_point, 'Character Spacing': character_spacing, 'Word Spacing': word_spacing, 'Line Spacing': line_spacing, 'Overflow': overflow, 'Text Box Width': text_box_width, 'Text Box Height': text_box_height}
        self._establish_links(**key_args)

class SubdivideCurve(BaseNode):
    _bl_idname = 'GeometryNodeSubdivideCurve'

    def __init__(self, curve: InputGeometry=None, cuts: InputInteger=1):
        super().__init__()
        key_args = {'Curve': curve, 'Cuts': cuts}
        self._establish_links(**key_args)

class SubdivideMesh(BaseNode):
    _bl_idname = 'GeometryNodeSubdivideMesh'

    def __init__(self, mesh: InputGeometry=None, level: InputInteger=1):
        super().__init__()
        key_args = {'Mesh': mesh, 'Level': level}
        self._establish_links(**key_args)

class SubdivisionSurface(BaseNode):
    _bl_idname = 'GeometryNodeSubdivisionSurface'

    def __init__(self, mesh: InputGeometry=None, level: InputInteger=1, edge_crease: InputFloat=0.0, vertex_crease: InputFloat=0.0, limit_surface: InputBoolean=True, quality: InputInteger=3, uv_smooth: InputMenu | Literal['None', 'Keep Corners', 'Keep Corners, Junctions', 'Keep Corners, Junctions, Concave', 'Keep Boundaries', 'All']='Keep Boundaries', boundary_smooth: InputMenu | Literal['Keep Corners', 'All']='All'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Level': level, 'Edge Crease': edge_crease, 'Vertex Crease': vertex_crease, 'Limit Surface': limit_surface, 'Quality': quality, 'UV Smooth': uv_smooth, 'Boundary Smooth': boundary_smooth}
        self._establish_links(**key_args)

class TransferAttributes(BaseNode):
    _bl_idname = 'GeometryNodeTransferAttributes'

    def __init__(self, target: InputGeometry=None, target_point_id: InputInteger=None, target_edge_id: InputInteger=None, target_face_id: InputInteger=None, target_corner_id: InputInteger=None, target_curve_id: InputInteger=None, target_instance_id: InputInteger=None, source: InputGeometry=None, source_point_id: InputInteger=None, source_edge_id: InputInteger=None, source_face_id: InputInteger=None, source_corner_id: InputInteger=None, source_curve_id: InputInteger=None, source_instance_id: InputInteger=None, pattern_mode: InputMenu | Literal['Exact', 'Wildcard']='Wildcard', attribute_names: InputStringList=None, exclude_names: InputBoolean=False):
        super().__init__()
        key_args = {'Target': target, 'Target Point ID': target_point_id, 'Target Edge ID': target_edge_id, 'Target Face ID': target_face_id, 'Target Corner ID': target_corner_id, 'Target Curve ID': target_curve_id, 'Target Instance ID': target_instance_id, 'Source': source, 'Source Point ID': source_point_id, 'Source Edge ID': source_edge_id, 'Source Face ID': source_face_id, 'Source Corner ID': source_corner_id, 'Source Curve ID': source_curve_id, 'Source Instance ID': source_instance_id, 'Pattern Mode': pattern_mode, 'Attribute Names': attribute_names, 'Exclude Names': exclude_names}
        self._establish_links(**key_args)

class TransformGeometry(BaseNode):
    _bl_idname = 'GeometryNodeTransform'

    def __init__(self, geometry: InputGeometry=None, mode: InputMenu | Literal['Components', 'Matrix']='Components', translation: InputVector=(0.0, 0.0, 0.0), rotation: InputRotation=(0.0, 0.0, 0.0), scale: InputVector=(1.0, 1.0, 1.0), transform: InputMatrix=None):
        super().__init__()
        key_args = {'Geometry': geometry, 'Mode': mode, 'Translation': translation, 'Rotation': rotation, 'Scale': scale, 'Transform': transform}
        self._establish_links(**key_args)

class TranslateInstances(BaseNode):
    _bl_idname = 'GeometryNodeTranslateInstances'

    def __init__(self, instances: InputGeometry=None, selection: InputBoolean=None, translation: InputVector=(0.0, 0.0, 0.0), local_space: InputBoolean=True):
        super().__init__()
        key_args = {'Instances': instances, 'Selection': selection, 'Translation': translation, 'Local Space': local_space}
        self._establish_links(**key_args)

class Triangulate(BaseNode):
    _bl_idname = 'GeometryNodeTriangulate'

    def __init__(self, mesh: InputGeometry=None, selection: InputBoolean=None, quad_method: InputMenu | Literal['Beauty', 'Fixed', 'Fixed Alternate', 'Shortest Diagonal', 'Longest Diagonal']='Shortest Diagonal', n_gon_method: InputMenu | Literal['Beauty', 'Clip']='Beauty'):
        super().__init__()
        key_args = {'Mesh': mesh, 'Selection': selection, 'Quad Method': quad_method, 'N-gon Method': n_gon_method}
        self._establish_links(**key_args)

class TrimCurve(BaseNode):
    _bl_idname = 'GeometryNodeTrimCurve'

    def __init__(self, curve: InputGeometry=None, selection: InputBoolean=None, start: InputFloat=0.0, end: InputFloat=1.0, start_001: InputFloat=0.0, end_001: InputFloat=1.0, *, mode: Literal['FACTOR', 'LENGTH']='FACTOR'):
        super().__init__()
        key_args = {'Curve': curve, 'Selection': selection, 'Start': start, 'End': end, 'Start_001': start_001, 'End_001': end_001}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def factor(cls, curve: InputGeometry=None, selection: InputBoolean=None, start: InputFloat=0.0, end: InputFloat=1.0) -> 'TrimCurve':
        return cls(mode='FACTOR', curve=curve, selection=selection, start=start, end=end)

    @classmethod
    def length(cls, curve: InputGeometry=None, selection: InputBoolean=None, start: InputFloat=0.0, end: InputFloat=1.0) -> 'TrimCurve':
        return cls(mode='LENGTH', curve=curve, selection=selection, start_001=start, end_001=end)

    @property
    def mode(self) -> Literal['FACTOR', 'LENGTH']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['FACTOR', 'LENGTH']) -> None:
        set_property(self.node, 'mode', value)

class UVSphere(BaseNode):
    _bl_idname = 'GeometryNodeMeshUVSphere'

    def __init__(self, segments: InputInteger=32, rings: InputInteger=16, radius: InputFloat=1.0):
        super().__init__()
        key_args = {'Segments': segments, 'Rings': rings, 'Radius': radius}
        self._establish_links(**key_args)

class XPBDSolver(BaseNode):
    _bl_idname = 'GeometryNodeXPBDSolver'

    def __init__(self, world: InputBundle=None, delta_time: InputFloat=0.04, filter: InputString='', simulation_to_world: InputMatrix=None, substeps: InputInteger=10, constraint_iterations: InputInteger=1, solver_path: InputString='', begin: InputFloat=0.0, end: InputFloat=1.0):
        super().__init__()
        key_args = {'World': world, 'Delta Time': delta_time, 'Filter': filter, 'Simulation to World': simulation_to_world, 'Substeps': substeps, 'Constraint Iterations': constraint_iterations, 'Solver Path': solver_path, 'Begin': begin, 'End': end}
        self._establish_links(**key_args)
