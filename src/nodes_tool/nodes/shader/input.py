# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket, VectorSocket
from ...socket_types import InputColor, InputFloat, InputVector

class AmbientOcclusion(BaseNode):
    _bl_idname = 'ShaderNodeAmbientOcclusion'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), distance: InputFloat=1.0, normal: InputVector=None, *, samples: int=0, inside: bool=False, only_local: bool=False):
        super().__init__()
        key_args = {'Color': color, 'Distance': distance, 'Normal': normal}
        self.samples = samples
        self.inside = inside
        self.only_local = only_local
        self._establish_links(**key_args)

    @property
    def samples(self) -> int:
        return self.node.samples

    @samples.setter
    def samples(self, value: int) -> None:
        set_property(self.node, 'samples', value)

    @property
    def inside(self) -> bool:
        return self.node.inside

    @inside.setter
    def inside(self, value: bool) -> None:
        set_property(self.node, 'inside', value)

    @property
    def only_local(self) -> bool:
        return self.node.only_local

    @only_local.setter
    def only_local(self, value: bool) -> None:
        set_property(self.node, 'only_local', value)

class Bevel(BaseNode):
    _bl_idname = 'ShaderNodeBevel'

    def __init__(self, radius: InputFloat=0.05, normal: InputVector=None, *, samples: int=0):
        super().__init__()
        key_args = {'Radius': radius, 'Normal': normal}
        self.samples = samples
        self._establish_links(**key_args)

    @property
    def samples(self) -> int:
        return self.node.samples

    @samples.setter
    def samples(self, value: int) -> None:
        set_property(self.node, 'samples', value)

class CameraData(BaseNode):
    _bl_idname = 'ShaderNodeCameraData'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Color(BaseNode):
    _bl_idname = 'ShaderNodeRGB'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ColorAttribute(BaseNode):
    _bl_idname = 'ShaderNodeVertexColor'

    def __init__(self, layer_name: str=''):
        super().__init__()
        key_args = {}
        self.layer_name = layer_name
        self._establish_links(**key_args)

    @property
    def layer_name(self) -> str:
        return self.node.layer_name

    @layer_name.setter
    def layer_name(self, value: str) -> None:
        set_property(self.node, 'layer_name', value)

class CurvesInfo(BaseNode):
    _bl_idname = 'ShaderNodeHairInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Fresnel(BaseNode):
    _bl_idname = 'ShaderNodeFresnel'

    def __init__(self, ior: InputFloat=1.5, normal: InputVector=None):
        super().__init__()
        key_args = {'IOR': ior, 'Normal': normal}
        self._establish_links(**key_args)

class Geometry(BaseNode):
    _bl_idname = 'ShaderNodeNewGeometry'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class LayerWeight(BaseNode):
    _bl_idname = 'ShaderNodeLayerWeight'

    def __init__(self, blend: InputFloat=0.5, normal: InputVector=None):
        super().__init__()
        key_args = {'Blend': blend, 'Normal': normal}
        self._establish_links(**key_args)

class LightPath(BaseNode):
    _bl_idname = 'ShaderNodeLightPath'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ObjectInfo(BaseNode):
    _bl_idname = 'ShaderNodeObjectInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ParticleInfo(BaseNode):
    _bl_idname = 'ShaderNodeParticleInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class PointInfo(BaseNode):
    _bl_idname = 'ShaderNodePointInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Raycast(BaseNode):
    _bl_idname = 'ShaderNodeRaycast'

    def __init__(self, position: InputVector=None, direction: InputVector=None, length: InputFloat=1.0, *, only_local: bool=False):
        super().__init__()
        key_args = {'Position': position, 'Direction': direction, 'Length': length}
        self.only_local = only_local
        self._establish_links(**key_args)

    @property
    def only_local(self) -> bool:
        return self.node.only_local

    @only_local.setter
    def only_local(self, value: bool) -> None:
        set_property(self.node, 'only_local', value)

class Tangent(BaseNode):
    _bl_idname = 'ShaderNodeTangent'

    def __init__(self, direction_type: Literal['RADIAL', 'UV_MAP']='RADIAL', axis: Literal['X', 'Y', 'Z']='Z', uv_map: str=''):
        super().__init__()
        key_args = {}
        self.direction_type = direction_type
        self.axis = axis
        self.uv_map = uv_map
        self._establish_links(**key_args)

    @property
    def direction_type(self) -> Literal['RADIAL', 'UV_MAP']:
        return self.node.direction_type

    @direction_type.setter
    def direction_type(self, value: Literal['RADIAL', 'UV_MAP']) -> None:
        set_property(self.node, 'direction_type', value)

    @property
    def axis(self) -> Literal['X', 'Y', 'Z']:
        return self.node.axis

    @axis.setter
    def axis(self, value: Literal['X', 'Y', 'Z']) -> None:
        set_property(self.node, 'axis', value)

    @property
    def uv_map(self) -> str:
        return self.node.uv_map

    @uv_map.setter
    def uv_map(self, value: str) -> None:
        set_property(self.node, 'uv_map', value)

class TextureCoordinate(BaseNode):
    _bl_idname = 'ShaderNodeTexCoord'

    def __init__(self, from_instancer: bool=False):
        super().__init__()
        key_args = {}
        self.from_instancer = from_instancer
        self._establish_links(**key_args)

    @property
    def from_instancer(self) -> bool:
        return self.node.from_instancer

    @from_instancer.setter
    def from_instancer(self, value: bool) -> None:
        set_property(self.node, 'from_instancer', value)

class UVAlongStroke(BaseNode):
    _bl_idname = 'ShaderNodeUVAlongStroke'

    def __init__(self, use_tips: bool=False):
        super().__init__()
        key_args = {}
        self.use_tips = use_tips
        self._establish_links(**key_args)

    @property
    def use_tips(self) -> bool:
        return self.node.use_tips

    @use_tips.setter
    def use_tips(self, value: bool) -> None:
        set_property(self.node, 'use_tips', value)

class UVMap(BaseNode):
    _bl_idname = 'ShaderNodeUVMap'

    def __init__(self, from_instancer: bool=False, uv_map: str=''):
        super().__init__()
        key_args = {}
        self.from_instancer = from_instancer
        self.uv_map = uv_map
        self._establish_links(**key_args)

    @property
    def from_instancer(self) -> bool:
        return self.node.from_instancer

    @from_instancer.setter
    def from_instancer(self, value: bool) -> None:
        set_property(self.node, 'from_instancer', value)

    @property
    def uv_map(self) -> str:
        return self.node.uv_map

    @uv_map.setter
    def uv_map(self, value: str) -> None:
        set_property(self.node, 'uv_map', value)

class Wireframe(BaseNode):
    _bl_idname = 'ShaderNodeWireframe'

    def __init__(self, size: InputFloat=0.01, *, use_pixel_size: bool=False):
        super().__init__()
        key_args = {'Size': size}
        self.use_pixel_size = use_pixel_size
        self._establish_links(**key_args)

    @property
    def use_pixel_size(self) -> bool:
        return self.node.use_pixel_size

    @use_pixel_size.setter
    def use_pixel_size(self, value: bool) -> None:
        set_property(self.node, 'use_pixel_size', value)
