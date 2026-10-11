# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
import math
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket, ImageSocket, IntegerSocket, VectorSocket
from ...socket_types import InputColor, InputFloat, InputImage, InputInteger, InputVector

class BrickTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexBrick'

    def __init__(self, vector: InputVector=None, color1: InputColor=(0.8, 0.8, 0.8, 1.0), color2: InputColor=(0.2, 0.2, 0.2, 1.0), mortar: InputColor=(0.0, 0.0, 0.0, 1.0), scale: InputFloat=5.0, mortar_size: InputFloat=0.02, mortar_smooth: InputFloat=0.1, bias: InputFloat=0.0, brick_width: InputFloat=0.5, row_height: InputFloat=0.25, *, offset_frequency: int=2, squash_frequency: int=2, offset: float=0.5, squash: float=1.0):
        super().__init__()
        key_args = {'Vector': vector, 'Color1': color1, 'Color2': color2, 'Mortar': mortar, 'Scale': scale, 'Mortar Size': mortar_size, 'Mortar Smooth': mortar_smooth, 'Bias': bias, 'Brick Width': brick_width, 'Row Height': row_height}
        self.offset_frequency = offset_frequency
        self.squash_frequency = squash_frequency
        self.offset = offset
        self.squash = squash
        self._establish_links(**key_args)

    @property
    def offset_frequency(self) -> int:
        return self.node.offset_frequency

    @offset_frequency.setter
    def offset_frequency(self, value: int) -> None:
        set_property(self.node, 'offset_frequency', value)

    @property
    def squash_frequency(self) -> int:
        return self.node.squash_frequency

    @squash_frequency.setter
    def squash_frequency(self, value: int) -> None:
        set_property(self.node, 'squash_frequency', value)

    @property
    def offset(self) -> float:
        return self.node.offset

    @offset.setter
    def offset(self, value: float) -> None:
        set_property(self.node, 'offset', value)

    @property
    def squash(self) -> float:
        return self.node.squash

    @squash.setter
    def squash(self, value: float) -> None:
        set_property(self.node, 'squash', value)

class CheckerTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexChecker'

    def __init__(self, vector: InputVector=None, color1: InputColor=(0.8, 0.8, 0.8, 1.0), color2: InputColor=(0.2, 0.2, 0.2, 1.0), scale: InputFloat=5.0):
        super().__init__()
        key_args = {'Vector': vector, 'Color1': color1, 'Color2': color2, 'Scale': scale}
        self._establish_links(**key_args)

class GaborTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexGabor'

    def __init__(self, vector: InputVector=None, scale: InputFloat=5.0, frequency: InputFloat=2.0, anisotropy: InputFloat=1.0, orientation_2d: InputFloat=math.pi / 4, orientation_3d: InputVector=(1.4142135, 1.4142135, 0.0), *, gabor_type: Literal['2D', '3D']='2D'):
        super().__init__()
        key_args = {'Vector': vector, 'Scale': scale, 'Frequency': frequency, 'Anisotropy': anisotropy, 'Orientation 2D': orientation_2d, 'Orientation 3D': orientation_3d}
        self.gabor_type = gabor_type
        self._establish_links(**key_args)

    @classmethod
    def type_2d(cls, vector: InputVector=None, scale: InputFloat=5.0, frequency: InputFloat=2.0, anisotropy: InputFloat=1.0, orientation_2d: InputFloat=math.pi / 4) -> 'GaborTexture':
        return cls(gabor_type='2D', vector=vector, scale=scale, frequency=frequency, anisotropy=anisotropy, orientation_2d=orientation_2d)

    @classmethod
    def type_3d(cls, vector: InputVector=None, scale: InputFloat=5.0, frequency: InputFloat=2.0, anisotropy: InputFloat=1.0, orientation_3d: InputVector=(1.4142135, 1.4142135, 0.0)) -> 'GaborTexture':
        return cls(gabor_type='3D', vector=vector, scale=scale, frequency=frequency, anisotropy=anisotropy, orientation_3d=orientation_3d)

    @property
    def gabor_type(self) -> Literal['2D', '3D']:
        return self.node.gabor_type

    @gabor_type.setter
    def gabor_type(self, value: Literal['2D', '3D']) -> None:
        set_property(self.node, 'gabor_type', value)

class GradientTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexGradient'

    def __init__(self, vector: InputVector=None, *, gradient_type: Literal['LINEAR', 'QUADRATIC', 'EASING', 'DIAGONAL', 'SPHERICAL', 'QUADRATIC_SPHERE', 'RADIAL']='LINEAR'):
        super().__init__()
        key_args = {'Vector': vector}
        self.gradient_type = gradient_type
        self._establish_links(**key_args)

    @classmethod
    def linear(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='LINEAR', vector=vector)

    @classmethod
    def quadratic(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='QUADRATIC', vector=vector)

    @classmethod
    def easing(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='EASING', vector=vector)

    @classmethod
    def diagonal(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='DIAGONAL', vector=vector)

    @classmethod
    def spherical(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='SPHERICAL', vector=vector)

    @classmethod
    def quadratic_sphere(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='QUADRATIC_SPHERE', vector=vector)

    @classmethod
    def radial(cls, vector: InputVector=None) -> 'GradientTexture':
        return cls(gradient_type='RADIAL', vector=vector)

    @property
    def gradient_type(self) -> Literal['LINEAR', 'QUADRATIC', 'EASING', 'DIAGONAL', 'SPHERICAL', 'QUADRATIC_SPHERE', 'RADIAL']:
        return self.node.gradient_type

    @gradient_type.setter
    def gradient_type(self, value: Literal['LINEAR', 'QUADRATIC', 'EASING', 'DIAGONAL', 'SPHERICAL', 'QUADRATIC_SPHERE', 'RADIAL']) -> None:
        set_property(self.node, 'gradient_type', value)

class ImageTexture(BaseNode):
    _bl_idname = 'GeometryNodeImageTexture'

    def __init__(self, image: InputImage=None, vector: InputVector=None, frame: InputInteger=0, *, interpolation: Literal['Linear', 'Closest', 'Cubic']='Linear', extension: Literal['REPEAT', 'EXTEND', 'CLIP', 'MIRROR']='REPEAT'):
        super().__init__()
        key_args = {'Image': image, 'Vector': vector, 'Frame': frame}
        self.interpolation = interpolation
        self.extension = extension
        self._establish_links(**key_args)

    @property
    def interpolation(self) -> Literal['Linear', 'Closest', 'Cubic']:
        return self.node.interpolation

    @interpolation.setter
    def interpolation(self, value: Literal['Linear', 'Closest', 'Cubic']) -> None:
        set_property(self.node, 'interpolation', value)

    @property
    def extension(self) -> Literal['REPEAT', 'EXTEND', 'CLIP', 'MIRROR']:
        return self.node.extension

    @extension.setter
    def extension(self, value: Literal['REPEAT', 'EXTEND', 'CLIP', 'MIRROR']) -> None:
        set_property(self.node, 'extension', value)

class MagicTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexMagic'

    def __init__(self, vector: InputVector=None, scale: InputFloat=5.0, distortion: InputFloat=1.0, *, turbulence_depth: int=0):
        super().__init__()
        key_args = {'Vector': vector, 'Scale': scale, 'Distortion': distortion}
        self.turbulence_depth = turbulence_depth
        self._establish_links(**key_args)

    @property
    def turbulence_depth(self) -> int:
        return self.node.turbulence_depth

    @turbulence_depth.setter
    def turbulence_depth(self, value: int) -> None:
        set_property(self.node, 'turbulence_depth', value)

class NoiseTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexNoise'

    def __init__(self, vector: InputVector=None, w: InputFloat=0.0, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, offset: InputFloat=0.0, gain: InputFloat=1.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D', noise_type: Literal['MULTIFRACTAL', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL', 'FBM', 'HETERO_TERRAIN']='FBM', normalize: bool=False):
        super().__init__()
        key_args = {'Vector': vector, 'W': w, 'Scale': scale, 'Detail': detail, 'Roughness': roughness, 'Lacunarity': lacunarity, 'Offset': offset, 'Gain': gain, 'Distortion': distortion}
        self.noise_dimensions = noise_dimensions
        self.noise_type = noise_type
        self.normalize = normalize
        self._establish_links(**key_args)

    @classmethod
    def multifractal(cls, vector: InputVector=None, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D') -> 'NoiseTexture':
        return cls(noise_type='MULTIFRACTAL', vector=vector, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, distortion=distortion, noise_dimensions=noise_dimensions)

    @classmethod
    def ridged_multifractal(cls, vector: InputVector=None, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, offset: InputFloat=0.0, gain: InputFloat=1.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D') -> 'NoiseTexture':
        return cls(noise_type='RIDGED_MULTIFRACTAL', vector=vector, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, offset=offset, gain=gain, distortion=distortion, noise_dimensions=noise_dimensions)

    @classmethod
    def hybrid_multifractal(cls, vector: InputVector=None, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, offset: InputFloat=0.0, gain: InputFloat=1.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D') -> 'NoiseTexture':
        return cls(noise_type='HYBRID_MULTIFRACTAL', vector=vector, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, offset=offset, gain=gain, distortion=distortion, noise_dimensions=noise_dimensions)

    @classmethod
    def fbm(cls, vector: InputVector=None, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D', normalize: bool=False) -> 'NoiseTexture':
        return cls(noise_type='FBM', vector=vector, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, distortion=distortion, noise_dimensions=noise_dimensions, normalize=normalize)

    @classmethod
    def hetero_terrain(cls, vector: InputVector=None, scale: InputFloat=5.0, detail: InputFloat=2.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, offset: InputFloat=0.0, distortion: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D') -> 'NoiseTexture':
        return cls(noise_type='HETERO_TERRAIN', vector=vector, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, offset=offset, distortion=distortion, noise_dimensions=noise_dimensions)

    @property
    def noise_dimensions(self) -> Literal['1D', '2D', '3D', '4D']:
        return self.node.noise_dimensions

    @noise_dimensions.setter
    def noise_dimensions(self, value: Literal['1D', '2D', '3D', '4D']) -> None:
        set_property(self.node, 'noise_dimensions', value)

    @property
    def noise_type(self) -> Literal['MULTIFRACTAL', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL', 'FBM', 'HETERO_TERRAIN']:
        return self.node.noise_type

    @noise_type.setter
    def noise_type(self, value: Literal['MULTIFRACTAL', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL', 'FBM', 'HETERO_TERRAIN']) -> None:
        set_property(self.node, 'noise_type', value)

    @property
    def normalize(self) -> bool:
        return self.node.normalize

    @normalize.setter
    def normalize(self, value: bool) -> None:
        set_property(self.node, 'normalize', value)

class VoronoiTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexVoronoi'

    def __init__(self, vector: InputVector=None, w: InputFloat=0.0, scale: InputFloat=5.0, detail: InputFloat=0.0, roughness: InputFloat=0.5, lacunarity: InputFloat=2.0, smoothness: InputFloat=1.0, exponent: InputFloat=0.5, randomness: InputFloat=1.0, *, voronoi_dimensions: Literal['1D', '2D', '3D', '4D']='3D', distance: Literal['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']='EUCLIDEAN', feature: Literal['F1', 'F2', 'SMOOTH_F1', 'DISTANCE_TO_EDGE', 'N_SPHERE_RADIUS']='F1', normalize: bool=False):
        super().__init__()
        key_args = {'Vector': vector, 'W': w, 'Scale': scale, 'Detail': detail, 'Roughness': roughness, 'Lacunarity': lacunarity, 'Smoothness': smoothness, 'Exponent': exponent, 'Randomness': randomness}
        self.voronoi_dimensions = voronoi_dimensions
        self.distance = distance
        self.feature = feature
        self.normalize = normalize
        self._establish_links(**key_args)

    @property
    def voronoi_dimensions(self) -> Literal['1D', '2D', '3D', '4D']:
        return self.node.voronoi_dimensions

    @voronoi_dimensions.setter
    def voronoi_dimensions(self, value: Literal['1D', '2D', '3D', '4D']) -> None:
        set_property(self.node, 'voronoi_dimensions', value)

    @property
    def distance(self) -> Literal['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']:
        return self.node.distance

    @distance.setter
    def distance(self, value: Literal['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']) -> None:
        set_property(self.node, 'distance', value)

    @property
    def feature(self) -> Literal['F1', 'F2', 'SMOOTH_F1', 'DISTANCE_TO_EDGE', 'N_SPHERE_RADIUS']:
        return self.node.feature

    @feature.setter
    def feature(self, value: Literal['F1', 'F2', 'SMOOTH_F1', 'DISTANCE_TO_EDGE', 'N_SPHERE_RADIUS']) -> None:
        set_property(self.node, 'feature', value)

    @property
    def normalize(self) -> bool:
        return self.node.normalize

    @normalize.setter
    def normalize(self, value: bool) -> None:
        set_property(self.node, 'normalize', value)

class WaveTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexWave'

    def __init__(self, vector: InputVector=None, scale: InputFloat=5.0, distortion: InputFloat=0.0, detail: InputFloat=2.0, detail_scale: InputFloat=1.0, detail_roughness: InputFloat=0.5, phase_offset: InputFloat=0.0, *, wave_type: Literal['BANDS', 'RINGS']='BANDS', bands_direction: Literal['X', 'Y', 'Z', 'DIAGONAL']='X', rings_direction: Literal['X', 'Y', 'Z', 'SPHERICAL']='X', wave_profile: Literal['SIN', 'SAW', 'TRI']='SIN'):
        super().__init__()
        key_args = {'Vector': vector, 'Scale': scale, 'Distortion': distortion, 'Detail': detail, 'Detail Scale': detail_scale, 'Detail Roughness': detail_roughness, 'Phase Offset': phase_offset}
        self.wave_type = wave_type
        self.bands_direction = bands_direction
        self.rings_direction = rings_direction
        self.wave_profile = wave_profile
        self._establish_links(**key_args)

    @classmethod
    def bands(cls, vector: InputVector=None, scale: InputFloat=5.0, distortion: InputFloat=0.0, detail: InputFloat=2.0, detail_scale: InputFloat=1.0, detail_roughness: InputFloat=0.5, phase_offset: InputFloat=0.0, *, bands_direction: Literal['X', 'Y', 'Z', 'DIAGONAL']='X', wave_profile: Literal['SIN', 'SAW', 'TRI']='SIN') -> 'WaveTexture':
        return cls(wave_type='BANDS', vector=vector, scale=scale, distortion=distortion, detail=detail, detail_scale=detail_scale, detail_roughness=detail_roughness, phase_offset=phase_offset, bands_direction=bands_direction, wave_profile=wave_profile)

    @classmethod
    def rings(cls, vector: InputVector=None, scale: InputFloat=5.0, distortion: InputFloat=0.0, detail: InputFloat=2.0, detail_scale: InputFloat=1.0, detail_roughness: InputFloat=0.5, phase_offset: InputFloat=0.0, *, rings_direction: Literal['X', 'Y', 'Z', 'SPHERICAL']='X', wave_profile: Literal['SIN', 'SAW', 'TRI']='SIN') -> 'WaveTexture':
        return cls(wave_type='RINGS', vector=vector, scale=scale, distortion=distortion, detail=detail, detail_scale=detail_scale, detail_roughness=detail_roughness, phase_offset=phase_offset, rings_direction=rings_direction, wave_profile=wave_profile)

    @property
    def wave_type(self) -> Literal['BANDS', 'RINGS']:
        return self.node.wave_type

    @wave_type.setter
    def wave_type(self, value: Literal['BANDS', 'RINGS']) -> None:
        set_property(self.node, 'wave_type', value)

    @property
    def bands_direction(self) -> Literal['X', 'Y', 'Z', 'DIAGONAL']:
        return self.node.bands_direction

    @bands_direction.setter
    def bands_direction(self, value: Literal['X', 'Y', 'Z', 'DIAGONAL']) -> None:
        set_property(self.node, 'bands_direction', value)

    @property
    def rings_direction(self) -> Literal['X', 'Y', 'Z', 'SPHERICAL']:
        return self.node.rings_direction

    @rings_direction.setter
    def rings_direction(self, value: Literal['X', 'Y', 'Z', 'SPHERICAL']) -> None:
        set_property(self.node, 'rings_direction', value)

    @property
    def wave_profile(self) -> Literal['SIN', 'SAW', 'TRI']:
        return self.node.wave_profile

    @wave_profile.setter
    def wave_profile(self, value: Literal['SIN', 'SAW', 'TRI']) -> None:
        set_property(self.node, 'wave_profile', value)

class WhiteNoiseTexture(BaseNode):
    _bl_idname = 'ShaderNodeTexWhiteNoise'

    def __init__(self, vector: InputVector=None, w: InputFloat=0.0, *, noise_dimensions: Literal['1D', '2D', '3D', '4D']='3D'):
        super().__init__()
        key_args = {'Vector': vector, 'W': w}
        self.noise_dimensions = noise_dimensions
        self._establish_links(**key_args)

    @property
    def noise_dimensions(self) -> Literal['1D', '2D', '3D', '4D']:
        return self.node.noise_dimensions

    @noise_dimensions.setter
    def noise_dimensions(self, value: Literal['1D', '2D', '3D', '4D']) -> None:
        set_property(self.node, 'noise_dimensions', value)
