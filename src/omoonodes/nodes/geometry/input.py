# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
from typing import TYPE_CHECKING, Literal
import bpy
from mathutils import Euler, Vector
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, CollectionSocket, CollectionSocketList, ColorSocket, FloatSocket, FontSocket, GeometrySocket, ImageSocket, IntegerSocket, MatrixSocket, MenuSocket, ObjectSocket, ObjectSocketList, RotationSocket, StringSocket, VectorSocket
from ...socket_types import InputBoolean, InputCollection, InputFloat, InputImage, InputInteger, InputMenu, InputObject, InputString, InputVector
from .._mixins import _HandleModeMixin

class Cursor3D(BaseNode):
    _bl_idname = 'GeometryNodeTool3DCursor'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ActiveCamera(BaseNode):
    _bl_idname = 'GeometryNodeInputActiveCamera'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ActiveElement(BaseNode):
    _bl_idname = 'GeometryNodeToolActiveElement'

    def __init__(self, domain: Literal['POINT', 'EDGE', 'FACE', 'LAYER']='POINT'):
        super().__init__()
        key_args = {}
        self.domain = domain
        self._establish_links(**key_args)

    @classmethod
    def point(cls) -> 'ActiveElement':
        return cls(domain='POINT')

    @classmethod
    def edge(cls) -> 'ActiveElement':
        return cls(domain='EDGE')

    @classmethod
    def face(cls) -> 'ActiveElement':
        return cls(domain='FACE')

    @classmethod
    def layer(cls) -> 'ActiveElement':
        return cls(domain='LAYER')

    @property
    def domain(self) -> Literal['POINT', 'EDGE', 'FACE', 'LAYER']:
        return self.node.domain

    @domain.setter
    def domain(self, value: Literal['POINT', 'EDGE', 'FACE', 'LAYER']) -> None:
        set_property(self.node, 'domain', value)

class BoneInfo(BaseNode):
    _bl_idname = 'GeometryNodeBoneInfo'

    def __init__(self, armature: InputObject=None, bone_name: InputString='', *, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL'):
        super().__init__()
        key_args = {'Armature': armature, 'Bone Name': bone_name}
        self.transform_space = transform_space
        self._establish_links(**key_args)

    @property
    def transform_space(self) -> Literal['ORIGINAL', 'RELATIVE']:
        return self.node.transform_space

    @transform_space.setter
    def transform_space(self, value: Literal['ORIGINAL', 'RELATIVE']) -> None:
        set_property(self.node, 'transform_space', value)

class Boolean(BaseNode):
    _bl_idname = 'FunctionNodeInputBool'

    def __init__(self, boolean: bool=False):
        super().__init__()
        key_args = {}
        self.boolean = boolean
        self._establish_links(**key_args)

    @property
    def boolean(self) -> bool:
        return self.node.boolean

    @boolean.setter
    def boolean(self, value: bool) -> None:
        set_property(self.node, 'boolean', value)

class CameraInfo(BaseNode):
    _bl_idname = 'GeometryNodeCameraInfo'

    def __init__(self, camera: InputObject=None):
        super().__init__()
        key_args = {'Camera': camera}
        self._establish_links(**key_args)

class CollectionChildren(BaseNode):
    _bl_idname = 'GeometryNodeCollectionChildren'

    def __init__(self, collection: InputCollection=None, recursive: InputBoolean=False):
        super().__init__()
        key_args = {'Collection': collection, 'Recursive': recursive}
        self._establish_links(**key_args)

class CollectionInfo(BaseNode):
    _bl_idname = 'GeometryNodeCollectionInfo'

    def __init__(self, collection: InputCollection=None, separate_children: InputBoolean=False, reset_children: InputBoolean=False, *, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL'):
        super().__init__()
        key_args = {'Collection': collection, 'Separate Children': separate_children, 'Reset Children': reset_children}
        self.transform_space = transform_space
        self._establish_links(**key_args)

    @property
    def transform_space(self) -> Literal['ORIGINAL', 'RELATIVE']:
        return self.node.transform_space

    @transform_space.setter
    def transform_space(self, value: Literal['ORIGINAL', 'RELATIVE']) -> None:
        set_property(self.node, 'transform_space', value)

class Color(BaseNode):
    _bl_idname = 'FunctionNodeInputColor'

    def __init__(self, value: tuple[float, float, float, float]=(0.735, 0.735, 0.735, 1.0)):
        super().__init__()
        key_args = {}
        self.value = value
        self._establish_links(**key_args)

    @property
    def value(self) -> tuple[float, float, float, float]:
        return self.node.value

    @value.setter
    def value(self, value: tuple[float, float, float, float]) -> None:
        set_property(self.node, 'value', value)

class CornersOfEdge(BaseNode):
    _bl_idname = 'GeometryNodeCornersOfEdge'

    def __init__(self, edge_index: InputInteger=None, weights: InputFloat=None, sort_index: InputInteger=0):
        super().__init__()
        key_args = {'Edge Index': edge_index, 'Weights': weights, 'Sort Index': sort_index}
        self._establish_links(**key_args)

class CornersOfFace(BaseNode):
    _bl_idname = 'GeometryNodeCornersOfFace'

    def __init__(self, face_index: InputInteger=None, weights: InputFloat=None, sort_index: InputInteger=0):
        super().__init__()
        key_args = {'Face Index': face_index, 'Weights': weights, 'Sort Index': sort_index}
        self._establish_links(**key_args)

class CornersOfVertex(BaseNode):
    _bl_idname = 'GeometryNodeCornersOfVertex'

    def __init__(self, vertex_index: InputInteger=None, weights: InputFloat=None, sort_index: InputInteger=0):
        super().__init__()
        key_args = {'Vertex Index': vertex_index, 'Weights': weights, 'Sort Index': sort_index}
        self._establish_links(**key_args)

class CurveHandlePositions(BaseNode):
    _bl_idname = 'GeometryNodeInputCurveHandlePositions'

    def __init__(self, relative: InputBoolean=False):
        super().__init__()
        key_args = {'Relative': relative}
        self._establish_links(**key_args)

class CurveTangent(BaseNode):
    _bl_idname = 'GeometryNodeInputTangent'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class CurveTilt(BaseNode):
    _bl_idname = 'GeometryNodeInputCurveTilt'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class CurveOfPoint(BaseNode):
    _bl_idname = 'GeometryNodeCurveOfPoint'

    def __init__(self, point_index: InputInteger=None):
        super().__init__()
        key_args = {'Point Index': point_index}
        self._establish_links(**key_args)

class EdgeAngle(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshEdgeAngle'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class EdgeNeighbors(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshEdgeNeighbors'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class EdgePathsToSelection(BaseNode):
    _bl_idname = 'GeometryNodeEdgePathsToSelection'

    def __init__(self, start_vertices: InputBoolean=None, next_vertex_index: InputInteger=None):
        super().__init__()
        key_args = {'Start Vertices': start_vertices, 'Next Vertex Index': next_vertex_index}
        self._establish_links(**key_args)

class EdgeVertices(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshEdgeVertices'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class EdgesOfCorner(BaseNode):
    _bl_idname = 'GeometryNodeEdgesOfCorner'

    def __init__(self, corner_index: InputInteger=None):
        super().__init__()
        key_args = {'Corner Index': corner_index}
        self._establish_links(**key_args)

class EdgesOfVertex(BaseNode):
    _bl_idname = 'GeometryNodeEdgesOfVertex'

    def __init__(self, vertex_index: InputInteger=None, weights: InputFloat=None, sort_index: InputInteger=0):
        super().__init__()
        key_args = {'Vertex Index': vertex_index, 'Weights': weights, 'Sort Index': sort_index}
        self._establish_links(**key_args)

class EdgesToFaceGroups(BaseNode):
    _bl_idname = 'GeometryNodeEdgesToFaceGroups'

    def __init__(self, boundary_edges: InputBoolean=None):
        super().__init__()
        key_args = {'Boundary Edges': boundary_edges}
        self._establish_links(**key_args)

class EndpointSelection(BaseNode):
    _bl_idname = 'GeometryNodeCurveEndpointSelection'

    def __init__(self, start_size: InputInteger=1, end_size: InputInteger=1):
        super().__init__()
        key_args = {'Start Size': start_size, 'End Size': end_size}
        self._establish_links(**key_args)

class FaceArea(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshFaceArea'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class FaceGroupBoundaries(BaseNode):
    _bl_idname = 'GeometryNodeMeshFaceSetBoundaries'

    def __init__(self, face_set: InputInteger=None):
        super().__init__()
        key_args = {'Face Set': face_set}
        self._establish_links(**key_args)

class FaceNeighbors(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshFaceNeighbors'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class FaceSet(BaseNode):
    _bl_idname = 'GeometryNodeToolFaceSet'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class FaceOfCorner(BaseNode):
    _bl_idname = 'GeometryNodeFaceOfCorner'

    def __init__(self, corner_index: InputInteger=None):
        super().__init__()
        key_args = {'Corner Index': corner_index}
        self._establish_links(**key_args)

class Font(BaseNode):
    _bl_idname = 'GeometryNodeInputFont'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class HandleTypeSelection(_HandleModeMixin, BaseNode):
    _bl_idname = 'GeometryNodeCurveHandleTypeSelection'

    @classmethod
    def free(cls) -> 'HandleTypeSelection':
        return cls(handle_type='FREE')

    @classmethod
    def auto(cls) -> 'HandleTypeSelection':
        return cls(handle_type='AUTO')

    @classmethod
    def vector(cls) -> 'HandleTypeSelection':
        return cls(handle_type='VECTOR')

    @classmethod
    def align(cls) -> 'HandleTypeSelection':
        return cls(handle_type='ALIGN')

    @property
    def handle_type(self) -> Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']:
        return self.node.handle_type

    @handle_type.setter
    def handle_type(self, value: Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']) -> None:
        set_property(self.node, 'handle_type', value)

    def __init__(self, handle_type: Literal['FREE', 'AUTO', 'VECTOR', 'ALIGN']='AUTO', left: bool=True, right: bool=True):
        super().__init__()
        self.handle_type = handle_type
        self.left = left
        self.right = right

class ID(BaseNode):
    _bl_idname = 'GeometryNodeInputID'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Image(BaseNode):
    _bl_idname = 'GeometryNodeInputImage'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ImageInfo(BaseNode):
    _bl_idname = 'GeometryNodeImageInfo'

    def __init__(self, image: InputImage=None, frame: InputInteger=0):
        super().__init__()
        key_args = {'Image': image, 'Frame': frame}
        self._establish_links(**key_args)

class ImportCSV(BaseNode):
    _bl_idname = 'GeometryNodeImportCSV'

    def __init__(self, path: InputString='', delimiter: InputString=','):
        super().__init__()
        key_args = {'Path': path, 'Delimiter': delimiter}
        self._establish_links(**key_args)

class ImportOBJ(BaseNode):
    _bl_idname = 'GeometryNodeImportOBJ'

    def __init__(self, path: InputString=''):
        super().__init__()
        key_args = {'Path': path}
        self._establish_links(**key_args)

class ImportPLY(BaseNode):
    _bl_idname = 'GeometryNodeImportPLY'

    def __init__(self, path: InputString=''):
        super().__init__()
        key_args = {'Path': path}
        self._establish_links(**key_args)

class ImportSTL(BaseNode):
    _bl_idname = 'GeometryNodeImportSTL'

    def __init__(self, path: InputString=''):
        super().__init__()
        key_args = {'Path': path}
        self._establish_links(**key_args)

class ImportText(BaseNode):
    _bl_idname = 'GeometryNodeImportText'

    def __init__(self, path: InputString=''):
        super().__init__()
        key_args = {'Path': path}
        self._establish_links(**key_args)

class ImportVDB(BaseNode):
    _bl_idname = 'GeometryNodeImportVDB'

    def __init__(self, path: InputString=''):
        super().__init__()
        key_args = {'Path': path}
        self._establish_links(**key_args)

class Index(BaseNode):
    _bl_idname = 'GeometryNodeInputIndex'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class InstanceBounds(BaseNode):
    _bl_idname = 'GeometryNodeInputInstanceBounds'

    def __init__(self, use_radius: InputBoolean=True):
        super().__init__()
        key_args = {'Use Radius': use_radius}
        self._establish_links(**key_args)

class InstanceReference(BaseNode):
    _bl_idname = 'GeometryNodeInputInstanceReference'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class InstanceRotation(BaseNode):
    _bl_idname = 'GeometryNodeInputInstanceRotation'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class InstanceScale(BaseNode):
    _bl_idname = 'GeometryNodeInputInstanceScale'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class InstanceTransform(BaseNode):
    _bl_idname = 'GeometryNodeInstanceTransform'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Integer(BaseNode):
    _bl_idname = 'FunctionNodeInputInt'

    def __init__(self, integer: int=1):
        super().__init__()
        key_args = {}
        self.integer = integer
        self._establish_links(**key_args)

    @property
    def integer(self) -> int:
        return self.node.integer

    @integer.setter
    def integer(self, value: int) -> None:
        set_property(self.node, 'integer', value)

class IsEdgeSmooth(BaseNode):
    _bl_idname = 'GeometryNodeInputEdgeSmooth'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class IsFacePlanar(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshFaceIsPlanar'

    def __init__(self, threshold: InputFloat=0.01):
        super().__init__()
        key_args = {'Threshold': threshold}
        self._establish_links(**key_args)

class IsFaceSmooth(BaseNode):
    _bl_idname = 'GeometryNodeInputShadeSmooth'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class IsSplineCyclic(BaseNode):
    _bl_idname = 'GeometryNodeInputSplineCyclic'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class IsViewport(BaseNode):
    _bl_idname = 'GeometryNodeIsViewport'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class MaterialIndex(BaseNode):
    _bl_idname = 'GeometryNodeInputMaterialIndex'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class MeshIsland(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshIsland'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class MousePosition(BaseNode):
    _bl_idname = 'GeometryNodeToolMousePosition'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class NamedAttribute(BaseNode):
    _bl_idname = 'GeometryNodeInputNamedAttribute'

    def __init__(self, name: InputString='', *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']='FLOAT'):
        super().__init__()
        key_args = {'Name': name}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, name: InputString='') -> 'NamedAttribute[FloatSocket]':
        return NamedAttribute(data_type='FLOAT', name=name)

    @classmethod
    def integer(cls, name: InputString='') -> 'NamedAttribute[IntegerSocket]':
        return NamedAttribute(data_type='INT', name=name)

    @classmethod
    def boolean(cls, name: InputString='') -> 'NamedAttribute[BooleanSocket]':
        return NamedAttribute(data_type='BOOLEAN', name=name)

    @classmethod
    def vector(cls, name: InputString='') -> 'NamedAttribute[VectorSocket]':
        return NamedAttribute(data_type='FLOAT_VECTOR', name=name)

    @classmethod
    def color(cls, name: InputString='') -> 'NamedAttribute[ColorSocket]':
        return NamedAttribute(data_type='FLOAT_COLOR', name=name)

    @classmethod
    def quaternion(cls, name: InputString='') -> 'NamedAttribute[RotationSocket]':
        return NamedAttribute(data_type='QUATERNION', name=name)

    @classmethod
    def matrix(cls, name: InputString='') -> 'NamedAttribute[MatrixSocket]':
        return NamedAttribute(data_type='FLOAT4X4', name=name)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'FLOAT_VECTOR', 'FLOAT_COLOR', 'QUATERNION', 'FLOAT4X4']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class NamedLayerSelection(BaseNode):
    _bl_idname = 'GeometryNodeInputNamedLayerSelection'

    def __init__(self, name: InputString=''):
        super().__init__()
        key_args = {'Name': name}
        self._establish_links(**key_args)

class Normal(BaseNode):
    _bl_idname = 'GeometryNodeInputNormal'

    def __init__(self, legacy_corner_normals: bool=False):
        super().__init__()
        key_args = {}
        self.legacy_corner_normals = legacy_corner_normals
        self._establish_links(**key_args)

    @property
    def legacy_corner_normals(self) -> bool:
        return self.node.legacy_corner_normals

    @legacy_corner_normals.setter
    def legacy_corner_normals(self, value: bool) -> None:
        set_property(self.node, 'legacy_corner_normals', value)

class ObjectInfo(BaseNode):
    _bl_idname = 'GeometryNodeObjectInfo'

    def __init__(self, object: InputObject=None, as_instance: InputBoolean=False, *, transform_space: Literal['ORIGINAL', 'RELATIVE']='ORIGINAL'):
        super().__init__()
        key_args = {'Object': object, 'As Instance': as_instance}
        self.transform_space = transform_space
        self._establish_links(**key_args)

    @property
    def transform_space(self) -> Literal['ORIGINAL', 'RELATIVE']:
        return self.node.transform_space

    @transform_space.setter
    def transform_space(self, value: Literal['ORIGINAL', 'RELATIVE']) -> None:
        set_property(self.node, 'transform_space', value)

class OffsetCornerInFace(BaseNode):
    _bl_idname = 'GeometryNodeOffsetCornerInFace'

    def __init__(self, corner_index: InputInteger=None, offset: InputInteger=0):
        super().__init__()
        key_args = {'Corner Index': corner_index, 'Offset': offset}
        self._establish_links(**key_args)

class OffsetPointInCurve(BaseNode):
    _bl_idname = 'GeometryNodeOffsetPointInCurve'

    def __init__(self, point_index: InputInteger=None, offset: InputInteger=0):
        super().__init__()
        key_args = {'Point Index': point_index, 'Offset': offset}
        self._establish_links(**key_args)

class PointsOfCurve(BaseNode):
    _bl_idname = 'GeometryNodePointsOfCurve'

    def __init__(self, curve_index: InputInteger=None, weights: InputFloat=None, sort_index: InputInteger=0):
        super().__init__()
        key_args = {'Curve Index': curve_index, 'Weights': weights, 'Sort Index': sort_index}
        self._establish_links(**key_args)

class Position(BaseNode):
    _bl_idname = 'GeometryNodeInputPosition'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Radius(BaseNode):
    _bl_idname = 'GeometryNodeInputRadius'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Rotation(BaseNode):
    _bl_idname = 'FunctionNodeInputRotation'

    def __init__(self, rotation_euler: tuple[float, float, float]=(0.0, 0.0, 0.0)):
        super().__init__()
        key_args = {}
        self.rotation_euler = rotation_euler
        self._establish_links(**key_args)

    @property
    def rotation_euler(self) -> Euler:
        return self.node.rotation_euler

    @rotation_euler.setter
    def rotation_euler(self, value: Euler | tuple[float, float, float]) -> None:
        set_property(self.node, 'rotation_euler', value)

class SceneTime(BaseNode):
    _bl_idname = 'GeometryNodeInputSceneTime'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Selection(BaseNode):
    _bl_idname = 'GeometryNodeToolSelection'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class SelfObject(BaseNode):
    _bl_idname = 'GeometryNodeSelfObject'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ShortestEdgePaths(BaseNode):
    _bl_idname = 'GeometryNodeInputShortestEdgePaths'

    def __init__(self, end_vertex: InputBoolean=None, edge_cost: InputFloat=None):
        super().__init__()
        key_args = {'End Vertex': end_vertex, 'Edge Cost': edge_cost}
        self._establish_links(**key_args)

class SpecialCharacters(BaseNode):
    _bl_idname = 'FunctionNodeInputSpecialCharacters'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class SplineLength(BaseNode):
    _bl_idname = 'GeometryNodeSplineLength'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class SplineParameter(BaseNode):
    _bl_idname = 'GeometryNodeSplineParameter'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class SplineResolution(BaseNode):
    _bl_idname = 'GeometryNodeInputSplineResolution'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class String(BaseNode):
    _bl_idname = 'FunctionNodeInputString'

    def __init__(self, string: str=''):
        super().__init__()
        key_args = {}
        self.string = string
        self._establish_links(**key_args)

    @property
    def string(self) -> str:
        return self.node.string

    @string.setter
    def string(self, value: str) -> None:
        set_property(self.node, 'string', value)

class UVTangent(BaseNode):
    _bl_idname = 'GeometryNodeUVTangent'

    def __init__(self, method: InputMenu | Literal['Exact', 'Fast']='Exact', uv: InputVector=(0.0, 0.0)):
        super().__init__()
        key_args = {'Method': method, 'UV': uv}
        self._establish_links(**key_args)

class Vector(BaseNode):
    _bl_idname = 'FunctionNodeInputVector'

    def __init__(self, vector: tuple[float, float, float]=(0.0, 0.0, 0.0), vector_dimensions: int=3):
        super().__init__()
        key_args = {}
        self.vector = vector
        self.vector_dimensions = vector_dimensions
        self._establish_links(**key_args)

    @property
    def vector(self) -> Vector:
        return self.node.vector

    @vector.setter
    def vector(self, value: Vector | tuple[float, float, float]) -> None:
        set_property(self.node, 'vector', value)

    @property
    def vector_dimensions(self) -> int:
        return self.node.vector_dimensions

    @vector_dimensions.setter
    def vector_dimensions(self, value: int) -> None:
        set_property(self.node, 'vector_dimensions', value)

class VertexNeighbors(BaseNode):
    _bl_idname = 'GeometryNodeInputMeshVertexNeighbors'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class VertexOfCorner(BaseNode):
    _bl_idname = 'GeometryNodeVertexOfCorner'

    def __init__(self, corner_index: InputInteger=None):
        super().__init__()
        key_args = {'Corner Index': corner_index}
        self._establish_links(**key_args)

class ViewportTransform(BaseNode):
    _bl_idname = 'GeometryNodeViewportTransform'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class VoxelIndex(BaseNode):
    _bl_idname = 'GeometryNodeInputVoxelIndex'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)
