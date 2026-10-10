# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
T = typing.TypeVar('T')
TGrid = typing.TypeVar('TGrid')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, BooleanSocketGrid, FloatSocket, FloatSocketGrid, GeometrySocket, IntegerSocket, IntegerSocketGrid, MatrixSocket, MenuSocket, StringSocket, VectorSocket, VectorSocketGrid
from ...socket_types import InputAny, InputBoolean, InputBooleanGrid, InputFloat, InputFloatGrid, InputGeometry, InputInteger, InputIntegerGrid, InputMatrix, InputMenu, InputString, InputVector, InputVectorGrid

class AdvectGrid(BaseNode):
    _bl_idname = 'GeometryNodeGridAdvect'

    def __init__(self, grid: InputAny=None, velocity: InputVectorGrid=None, time_step: InputFloat=1.0, integration_scheme: InputMenu | Literal['Semi-Lagrangian', 'Midpoint', 'Runge-Kutta 3', 'Runge-Kutta 4', 'MacCormack', 'BFECC']='Runge-Kutta 3', limiter: InputMenu | Literal['None', 'Clamp', 'Revert']='Clamp', *, data_type: Literal['FLOAT', 'INT', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Velocity': velocity, 'Time Step': time_step, 'Integration Scheme': integration_scheme, 'Limiter': limiter}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, velocity: InputVectorGrid=None, time_step: InputFloat=1.0, integration_scheme: InputMenu | Literal['Semi-Lagrangian', 'Midpoint', 'Runge-Kutta 3', 'Runge-Kutta 4', 'MacCormack', 'BFECC']='Runge-Kutta 3', limiter: InputMenu | Literal['None', 'Clamp', 'Revert']='Clamp') -> 'AdvectGrid[FloatSocketGrid]':
        return AdvectGrid(data_type='FLOAT', grid=grid, velocity=velocity, time_step=time_step, integration_scheme=integration_scheme, limiter=limiter)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, velocity: InputVectorGrid=None, time_step: InputFloat=1.0, integration_scheme: InputMenu | Literal['Semi-Lagrangian', 'Midpoint', 'Runge-Kutta 3', 'Runge-Kutta 4', 'MacCormack', 'BFECC']='Runge-Kutta 3', limiter: InputMenu | Literal['None', 'Clamp', 'Revert']='Clamp') -> 'AdvectGrid[IntegerSocketGrid]':
        return AdvectGrid(data_type='INT', grid=grid, velocity=velocity, time_step=time_step, integration_scheme=integration_scheme, limiter=limiter)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, velocity: InputVectorGrid=None, time_step: InputFloat=1.0, integration_scheme: InputMenu | Literal['Semi-Lagrangian', 'Midpoint', 'Runge-Kutta 3', 'Runge-Kutta 4', 'MacCormack', 'BFECC']='Runge-Kutta 3', limiter: InputMenu | Literal['None', 'Clamp', 'Revert']='Clamp') -> 'AdvectGrid[VectorSocketGrid]':
        return AdvectGrid(data_type='VECTOR', grid=grid, velocity=velocity, time_step=time_step, integration_scheme=integration_scheme, limiter=limiter)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ClipGrid(BaseNode):
    _bl_idname = 'GeometryNodeGridClip'

    def __init__(self, grid: InputAny=None, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Min X': min_x, 'Min Y': min_y, 'Min Z': min_z, 'Max X': max_x, 'Max Y': max_y, 'Max Z': max_z}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32) -> 'ClipGrid[FloatSocketGrid]':
        return ClipGrid(data_type='FLOAT', grid=grid, min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32) -> 'ClipGrid[IntegerSocketGrid]':
        return ClipGrid(data_type='INT', grid=grid, min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32) -> 'ClipGrid[BooleanSocketGrid]':
        return ClipGrid(data_type='BOOLEAN', grid=grid, min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0, max_x: InputInteger=32, max_y: InputInteger=32, max_z: InputInteger=32) -> 'ClipGrid[VectorSocketGrid]':
        return ClipGrid(data_type='VECTOR', grid=grid, min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class CubeGridTopology(BaseNode):
    _bl_idname = 'GeometryNodeCubeGridTopology'

    def __init__(self, bounds_min: InputVector=(-1.0, -1.0, -1.0), bounds_max: InputVector=(1.0, 1.0, 1.0), resolution_x: InputInteger=32, resolution_y: InputInteger=32, resolution_z: InputInteger=32, min_x: InputInteger=0, min_y: InputInteger=0, min_z: InputInteger=0):
        super().__init__()
        key_args = {'Bounds Min': bounds_min, 'Bounds Max': bounds_max, 'Resolution X': resolution_x, 'Resolution Y': resolution_y, 'Resolution Z': resolution_z, 'Min X': min_x, 'Min Y': min_y, 'Min Z': min_z}
        self._establish_links(**key_args)

class DistributePointsInGrid(BaseNode):
    _bl_idname = 'GeometryNodeDistributePointsInGrid'

    def __init__(self, grid: InputFloatGrid=None, density: InputFloat=1.0, seed: InputInteger=0, spacing: InputVector=(0.3, 0.3, 0.3), threshold: InputFloat=0.1, *, mode: Literal['DENSITY_RANDOM', 'DENSITY_GRID']='DENSITY_RANDOM'):
        super().__init__()
        key_args = {'Grid': grid, 'Density': density, 'Seed': seed, 'Spacing': spacing, 'Threshold': threshold}
        self.mode = mode
        self._establish_links(**key_args)

    @classmethod
    def random(cls, grid: InputFloatGrid=None, density: InputFloat=1.0, seed: InputInteger=0) -> 'DistributePointsInGrid':
        return cls(mode='DENSITY_RANDOM', grid=grid, density=density, seed=seed)

    @classmethod
    def grid(cls, grid: InputFloatGrid=None, spacing: InputVector=(0.3, 0.3, 0.3), threshold: InputFloat=0.1) -> 'DistributePointsInGrid':
        return cls(mode='DENSITY_GRID', grid=grid, spacing=spacing, threshold=threshold)

    @property
    def mode(self) -> Literal['DENSITY_RANDOM', 'DENSITY_GRID']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['DENSITY_RANDOM', 'DENSITY_GRID']) -> None:
        set_property(self.node, 'mode', value)

class DistributePointsInVolume(BaseNode):
    _bl_idname = 'GeometryNodeDistributePointsInVolume'

    def __init__(self, volume: InputGeometry=None, mode: InputMenu | Literal['Random', 'Grid']='Random', density: InputFloat=1.0, seed: InputInteger=0, spacing: InputVector=(0.3, 0.3, 0.3), threshold: InputFloat=0.1):
        super().__init__()
        key_args = {'Volume': volume, 'Mode': mode, 'Density': density, 'Seed': seed, 'Spacing': spacing, 'Threshold': threshold}
        self._establish_links(**key_args)

class GetNamedGrid(BaseNode):
    _bl_idname = 'GeometryNodeGetNamedGrid'

    def __init__(self, volume: InputGeometry=None, name: InputString='', remove: InputBoolean=True, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Volume': volume, 'Name': name, 'Remove': remove}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, volume: InputGeometry=None, name: InputString='', remove: InputBoolean=True) -> 'GetNamedGrid[FloatSocketGrid]':
        return GetNamedGrid(data_type='FLOAT', volume=volume, name=name, remove=remove)

    @classmethod
    def integer(cls, volume: InputGeometry=None, name: InputString='', remove: InputBoolean=True) -> 'GetNamedGrid[IntegerSocketGrid]':
        return GetNamedGrid(data_type='INT', volume=volume, name=name, remove=remove)

    @classmethod
    def boolean(cls, volume: InputGeometry=None, name: InputString='', remove: InputBoolean=True) -> 'GetNamedGrid[BooleanSocketGrid]':
        return GetNamedGrid(data_type='BOOLEAN', volume=volume, name=name, remove=remove)

    @classmethod
    def vector(cls, volume: InputGeometry=None, name: InputString='', remove: InputBoolean=True) -> 'GetNamedGrid[VectorSocketGrid]':
        return GetNamedGrid(data_type='VECTOR', volume=volume, name=name, remove=remove)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GridCurl(BaseNode):
    _bl_idname = 'GeometryNodeGridCurl'

    def __init__(self, grid: InputVectorGrid=None):
        super().__init__()
        key_args = {'Grid': grid}
        self._establish_links(**key_args)

class GridDilateErode(BaseNode):
    _bl_idname = 'GeometryNodeGridDilateAndErode'

    def __init__(self, grid: InputAny=None, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve', steps: InputInteger=1, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Connectivity': connectivity, 'Tiles': tiles, 'Steps': steps}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve', steps: InputInteger=1) -> 'GridDilateErode[FloatSocketGrid]':
        return GridDilateErode(data_type='FLOAT', grid=grid, connectivity=connectivity, tiles=tiles, steps=steps)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve', steps: InputInteger=1) -> 'GridDilateErode[IntegerSocketGrid]':
        return GridDilateErode(data_type='INT', grid=grid, connectivity=connectivity, tiles=tiles, steps=steps)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve', steps: InputInteger=1) -> 'GridDilateErode[BooleanSocketGrid]':
        return GridDilateErode(data_type='BOOLEAN', grid=grid, connectivity=connectivity, tiles=tiles, steps=steps)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, connectivity: InputMenu | Literal['Face', 'Edge', 'Vertex']='Face', tiles: InputMenu | Literal['Ignore', 'Expand', 'Preserve']='Preserve', steps: InputInteger=1) -> 'GridDilateErode[VectorSocketGrid]':
        return GridDilateErode(data_type='VECTOR', grid=grid, connectivity=connectivity, tiles=tiles, steps=steps)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GridDivergence(BaseNode):
    _bl_idname = 'GeometryNodeGridDivergence'

    def __init__(self, grid: InputVectorGrid=None):
        super().__init__()
        key_args = {'Grid': grid}
        self._establish_links(**key_args)

class GridGradient(BaseNode):
    _bl_idname = 'GeometryNodeGridGradient'

    def __init__(self, grid: InputFloatGrid=None):
        super().__init__()
        key_args = {'Grid': grid}
        self._establish_links(**key_args)

class GridInfo(BaseNode):
    _bl_idname = 'GeometryNodeGridInfo'

    def __init__(self, grid: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None) -> 'GridInfo[FloatSocket, FloatSocketGrid]':
        return GridInfo(data_type='FLOAT', grid=grid)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None) -> 'GridInfo[IntegerSocket, IntegerSocketGrid]':
        return GridInfo(data_type='INT', grid=grid)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None) -> 'GridInfo[BooleanSocket, BooleanSocketGrid]':
        return GridInfo(data_type='BOOLEAN', grid=grid)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None) -> 'GridInfo[VectorSocket, VectorSocketGrid]':
        return GridInfo(data_type='VECTOR', grid=grid)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GridLaplacian(BaseNode):
    _bl_idname = 'GeometryNodeGridLaplacian'

    def __init__(self, grid: InputFloatGrid=None):
        super().__init__()
        key_args = {'Grid': grid}
        self._establish_links(**key_args)

class GridMean(BaseNode):
    _bl_idname = 'GeometryNodeGridMean'

    def __init__(self, grid: InputAny=None, width: InputInteger=1, iterations: InputInteger=1, *, data_type: Literal['FLOAT', 'INT', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Width': width, 'Iterations': iterations}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMean[FloatSocketGrid]':
        return GridMean(data_type='FLOAT', grid=grid, width=width, iterations=iterations)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMean[IntegerSocketGrid]':
        return GridMean(data_type='INT', grid=grid, width=width, iterations=iterations)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMean[VectorSocketGrid]':
        return GridMean(data_type='VECTOR', grid=grid, width=width, iterations=iterations)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GridMedian(BaseNode):
    _bl_idname = 'GeometryNodeGridMedian'

    def __init__(self, grid: InputAny=None, width: InputInteger=1, iterations: InputInteger=1, *, data_type: Literal['FLOAT', 'INT', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Width': width, 'Iterations': iterations}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMedian[FloatSocketGrid]':
        return GridMedian(data_type='FLOAT', grid=grid, width=width, iterations=iterations)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMedian[IntegerSocketGrid]':
        return GridMedian(data_type='INT', grid=grid, width=width, iterations=iterations)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, width: InputInteger=1, iterations: InputInteger=1) -> 'GridMedian[VectorSocketGrid]':
        return GridMedian(data_type='VECTOR', grid=grid, width=width, iterations=iterations)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class GridToMesh(BaseNode):
    _bl_idname = 'GeometryNodeGridToMesh'

    def __init__(self, grid: InputFloatGrid=None, threshold: InputFloat=0.1, adaptivity: InputFloat=0.0):
        super().__init__()
        key_args = {'Grid': grid, 'Threshold': threshold, 'Adaptivity': adaptivity}
        self._establish_links(**key_args)

class GridToPoints(BaseNode):
    _bl_idname = 'GeometryNodeGridToPoints'

    def __init__(self, grid: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None) -> 'GridToPoints[FloatSocket, FloatSocketGrid]':
        return GridToPoints(data_type='FLOAT', grid=grid)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None) -> 'GridToPoints[IntegerSocket, IntegerSocketGrid]':
        return GridToPoints(data_type='INT', grid=grid)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None) -> 'GridToPoints[BooleanSocket, BooleanSocketGrid]':
        return GridToPoints(data_type='BOOLEAN', grid=grid)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None) -> 'GridToPoints[VectorSocket, VectorSocketGrid]':
        return GridToPoints(data_type='VECTOR', grid=grid)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class MeshToDensityGrid(BaseNode):
    _bl_idname = 'GeometryNodeMeshToDensityGrid'

    def __init__(self, mesh: InputGeometry=None, density: InputFloat=1.0, voxel_size: InputFloat=0.3, gradient_width: InputFloat=0.2):
        super().__init__()
        key_args = {'Mesh': mesh, 'Density': density, 'Voxel Size': voxel_size, 'Gradient Width': gradient_width}
        self._establish_links(**key_args)

class MeshToSDFGrid(BaseNode):
    _bl_idname = 'GeometryNodeMeshToSDFGrid'

    def __init__(self, mesh: InputGeometry=None, voxel_size: InputFloat=0.3, band_width: InputInteger=3):
        super().__init__()
        key_args = {'Mesh': mesh, 'Voxel Size': voxel_size, 'Band Width': band_width}
        self._establish_links(**key_args)

class MeshToVolume(BaseNode):
    _bl_idname = 'GeometryNodeMeshToVolume'

    def __init__(self, mesh: InputGeometry=None, density: InputFloat=1.0, resolution_mode: InputMenu | Literal['Amount', 'Size']='Amount', voxel_size: InputFloat=0.3, voxel_amount: InputFloat=64.0, interior_band_width: InputFloat=0.2):
        super().__init__()
        key_args = {'Mesh': mesh, 'Density': density, 'Resolution Mode': resolution_mode, 'Voxel Size': voxel_size, 'Voxel Amount': voxel_amount, 'Interior Band Width': interior_band_width}
        self._establish_links(**key_args)

class PointsToSDFGrid(BaseNode):
    _bl_idname = 'GeometryNodePointsToSDFGrid'

    def __init__(self, points: InputGeometry=None, radius: InputFloat=0.5, voxel_size: InputFloat=0.3):
        super().__init__()
        key_args = {'Points': points, 'Radius': radius, 'Voxel Size': voxel_size}
        self._establish_links(**key_args)

class PointsToVolume(BaseNode):
    _bl_idname = 'GeometryNodePointsToVolume'

    def __init__(self, points: InputGeometry=None, density: InputFloat=1.0, resolution_mode: InputMenu | Literal['Amount', 'Size']='Amount', voxel_size: InputFloat=0.3, voxel_amount: InputFloat=64.0, radius: InputFloat=0.5):
        super().__init__()
        key_args = {'Points': points, 'Density': density, 'Resolution Mode': resolution_mode, 'Voxel Size': voxel_size, 'Voxel Amount': voxel_amount, 'Radius': radius}
        self._establish_links(**key_args)

class PruneGrid(BaseNode):
    _bl_idname = 'GeometryNodeGridPrune'

    def __init__(self, grid: InputAny=None, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']='Threshold', threshold: InputAny=0.01, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Mode': mode, 'Threshold': threshold}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']='Threshold', threshold: InputFloat=0.01) -> 'PruneGrid[FloatSocket, FloatSocketGrid]':
        return PruneGrid(data_type='FLOAT', grid=grid, mode=mode, threshold=threshold)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']='Threshold', threshold: InputInteger=0) -> 'PruneGrid[IntegerSocket, IntegerSocketGrid]':
        return PruneGrid(data_type='INT', grid=grid, mode=mode, threshold=threshold)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']='Threshold') -> 'PruneGrid[BooleanSocket, BooleanSocketGrid]':
        return PruneGrid(data_type='BOOLEAN', grid=grid, mode=mode)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, mode: InputMenu | Literal['Inactive', 'Threshold', 'SDF']='Threshold', threshold: InputVector=(0.01, 0.01, 0.01)) -> 'PruneGrid[VectorSocket, VectorSocketGrid]':
        return PruneGrid(data_type='VECTOR', grid=grid, mode=mode, threshold=threshold)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SDFGridFillet(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridFillet'

    def __init__(self, grid: InputFloatGrid=None, iterations: InputInteger=1):
        super().__init__()
        key_args = {'Grid': grid, 'Iterations': iterations}
        self._establish_links(**key_args)

class SDFGridLaplacian(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridLaplacian'

    def __init__(self, grid: InputFloatGrid=None, iterations: InputInteger=1):
        super().__init__()
        key_args = {'Grid': grid, 'Iterations': iterations}
        self._establish_links(**key_args)

class SDFGridMean(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridMean'

    def __init__(self, grid: InputFloatGrid=None, width: InputInteger=1, iterations: InputInteger=1):
        super().__init__()
        key_args = {'Grid': grid, 'Width': width, 'Iterations': iterations}
        self._establish_links(**key_args)

class SDFGridMeanCurvature(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridMeanCurvature'

    def __init__(self, grid: InputFloatGrid=None, iterations: InputInteger=1):
        super().__init__()
        key_args = {'Grid': grid, 'Iterations': iterations}
        self._establish_links(**key_args)

class SDFGridMedian(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridMedian'

    def __init__(self, grid: InputFloatGrid=None, width: InputInteger=1, iterations: InputInteger=1):
        super().__init__()
        key_args = {'Grid': grid, 'Width': width, 'Iterations': iterations}
        self._establish_links(**key_args)

class SDFGridOffset(BaseNode):
    _bl_idname = 'GeometryNodeSDFGridOffset'

    def __init__(self, grid: InputFloatGrid=None, distance: InputFloat=0.1):
        super().__init__()
        key_args = {'Grid': grid, 'Distance': distance}
        self._establish_links(**key_args)

class SampleGrid(BaseNode):
    _bl_idname = 'GeometryNodeSampleGrid'

    def __init__(self, grid: InputAny=None, position: InputVector=None, interpolation: InputMenu | Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear', *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Position': position, 'Interpolation': interpolation}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, position: InputVector=None, interpolation: InputMenu | Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear') -> 'SampleGrid[FloatSocket, FloatSocketGrid]':
        return SampleGrid(data_type='FLOAT', grid=grid, position=position, interpolation=interpolation)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, position: InputVector=None, interpolation: InputMenu | Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear') -> 'SampleGrid[IntegerSocket, IntegerSocketGrid]':
        return SampleGrid(data_type='INT', grid=grid, position=position, interpolation=interpolation)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, position: InputVector=None, interpolation: InputMenu | Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear') -> 'SampleGrid[BooleanSocket, BooleanSocketGrid]':
        return SampleGrid(data_type='BOOLEAN', grid=grid, position=position, interpolation=interpolation)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, position: InputVector=None, interpolation: InputMenu | Literal['Nearest Neighbor', 'Trilinear', 'Triquadratic']='Trilinear') -> 'SampleGrid[VectorSocket, VectorSocketGrid]':
        return SampleGrid(data_type='VECTOR', grid=grid, position=position, interpolation=interpolation)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SampleGridIndex(BaseNode):
    _bl_idname = 'GeometryNodeSampleGridIndex'

    def __init__(self, grid: InputAny=None, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'X': x, 'Y': y, 'Z': z}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0) -> 'SampleGridIndex[FloatSocket, FloatSocketGrid]':
        return SampleGridIndex(data_type='FLOAT', grid=grid, x=x, y=y, z=z)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0) -> 'SampleGridIndex[IntegerSocket, IntegerSocketGrid]':
        return SampleGridIndex(data_type='INT', grid=grid, x=x, y=y, z=z)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0) -> 'SampleGridIndex[BooleanSocket, BooleanSocketGrid]':
        return SampleGridIndex(data_type='BOOLEAN', grid=grid, x=x, y=y, z=z)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, x: InputInteger=0, y: InputInteger=0, z: InputInteger=0) -> 'SampleGridIndex[VectorSocket, VectorSocketGrid]':
        return SampleGridIndex(data_type='VECTOR', grid=grid, x=x, y=y, z=z)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SetGridBackground(BaseNode):
    _bl_idname = 'GeometryNodeSetGridBackground'

    def __init__(self, grid: InputAny=None, background: InputAny=0.0, update_inactive: InputBoolean=False, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Background': background, 'Update Inactive': update_inactive}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, background: InputFloat=0.0, update_inactive: InputBoolean=False) -> 'SetGridBackground[FloatSocket, FloatSocketGrid]':
        return SetGridBackground(data_type='FLOAT', grid=grid, background=background, update_inactive=update_inactive)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, background: InputInteger=0, update_inactive: InputBoolean=False) -> 'SetGridBackground[IntegerSocket, IntegerSocketGrid]':
        return SetGridBackground(data_type='INT', grid=grid, background=background, update_inactive=update_inactive)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, background: InputBoolean=False, update_inactive: InputBoolean=False) -> 'SetGridBackground[BooleanSocket, BooleanSocketGrid]':
        return SetGridBackground(data_type='BOOLEAN', grid=grid, background=background, update_inactive=update_inactive)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, background: InputVector=(0.0, 0.0, 0.0), update_inactive: InputBoolean=False) -> 'SetGridBackground[VectorSocket, VectorSocketGrid]':
        return SetGridBackground(data_type='VECTOR', grid=grid, background=background, update_inactive=update_inactive)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class SetGridTransform(BaseNode):
    _bl_idname = 'GeometryNodeSetGridTransform'

    def __init__(self, grid: InputAny=None, transform: InputMatrix=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid, 'Transform': transform}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None, transform: InputMatrix=None) -> 'SetGridTransform[FloatSocketGrid]':
        return SetGridTransform(data_type='FLOAT', grid=grid, transform=transform)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None, transform: InputMatrix=None) -> 'SetGridTransform[IntegerSocketGrid]':
        return SetGridTransform(data_type='INT', grid=grid, transform=transform)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None, transform: InputMatrix=None) -> 'SetGridTransform[BooleanSocketGrid]':
        return SetGridTransform(data_type='BOOLEAN', grid=grid, transform=transform)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None, transform: InputMatrix=None) -> 'SetGridTransform[VectorSocketGrid]':
        return SetGridTransform(data_type='VECTOR', grid=grid, transform=transform)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class StoreNamedGrid(BaseNode):
    _bl_idname = 'GeometryNodeStoreNamedGrid'

    def __init__(self, volume: InputGeometry=None, name: InputString='', grid: InputAny=None, *, data_type: Literal['BOOLEAN', 'FLOAT', 'INT', 'VECTOR_FLOAT']='FLOAT'):
        super().__init__()
        key_args = {'Volume': volume, 'Name': name, 'Grid': grid}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def boolean(cls, volume: InputGeometry=None, name: InputString='', grid: InputBooleanGrid=None) -> 'StoreNamedGrid[BooleanSocketGrid]':
        return StoreNamedGrid(data_type='BOOLEAN', volume=volume, name=name, grid=grid)

    @classmethod
    def float(cls, volume: InputGeometry=None, name: InputString='', grid: InputFloatGrid=None) -> 'StoreNamedGrid[FloatSocketGrid]':
        return StoreNamedGrid(data_type='FLOAT', volume=volume, name=name, grid=grid)

    @classmethod
    def integer(cls, volume: InputGeometry=None, name: InputString='', grid: InputIntegerGrid=None) -> 'StoreNamedGrid[IntegerSocketGrid]':
        return StoreNamedGrid(data_type='INT', volume=volume, name=name, grid=grid)

    @classmethod
    def vector(cls, volume: InputGeometry=None, name: InputString='', grid: InputVectorGrid=None) -> 'StoreNamedGrid[VectorSocketGrid]':
        return StoreNamedGrid(data_type='VECTOR_FLOAT', volume=volume, name=name, grid=grid)

    @property
    def data_type(self) -> Literal['BOOLEAN', 'FLOAT', 'INT', 'VECTOR_FLOAT']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['BOOLEAN', 'FLOAT', 'INT', 'VECTOR_FLOAT']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class VolumeCube(BaseNode):
    _bl_idname = 'GeometryNodeVolumeCube'

    def __init__(self, density: InputFloat=1.0, background: InputFloat=0.0, min: InputVector=(-1.0, -1.0, -1.0), max: InputVector=(1.0, 1.0, 1.0), resolution_x: InputInteger=32, resolution_y: InputInteger=32, resolution_z: InputInteger=32):
        super().__init__()
        key_args = {'Density': density, 'Background': background, 'Min': min, 'Max': max, 'Resolution X': resolution_x, 'Resolution Y': resolution_y, 'Resolution Z': resolution_z}
        self._establish_links(**key_args)

class VolumeToMesh(BaseNode):
    _bl_idname = 'GeometryNodeVolumeToMesh'

    def __init__(self, volume: InputGeometry=None, resolution_mode: InputMenu | Literal['Grid', 'Amount', 'Size']='Grid', voxel_size: InputFloat=0.3, voxel_amount: InputFloat=64.0, threshold: InputFloat=0.1, adaptivity: InputFloat=0.0):
        super().__init__()
        key_args = {'Volume': volume, 'Resolution Mode': resolution_mode, 'Voxel Size': voxel_size, 'Voxel Amount': voxel_amount, 'Threshold': threshold, 'Adaptivity': adaptivity}
        self._establish_links(**key_args)

class VoxelizeGrid(BaseNode):
    _bl_idname = 'GeometryNodeGridVoxelize'

    def __init__(self, grid: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Grid': grid}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, grid: InputFloatGrid=None) -> 'VoxelizeGrid[FloatSocketGrid]':
        return VoxelizeGrid(data_type='FLOAT', grid=grid)

    @classmethod
    def integer(cls, grid: InputIntegerGrid=None) -> 'VoxelizeGrid[IntegerSocketGrid]':
        return VoxelizeGrid(data_type='INT', grid=grid)

    @classmethod
    def boolean(cls, grid: InputBooleanGrid=None) -> 'VoxelizeGrid[BooleanSocketGrid]':
        return VoxelizeGrid(data_type='BOOLEAN', grid=grid)

    @classmethod
    def vector(cls, grid: InputVectorGrid=None) -> 'VoxelizeGrid[VectorSocketGrid]':
        return VoxelizeGrid(data_type='VECTOR', grid=grid)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
