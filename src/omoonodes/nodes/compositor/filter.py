# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, IntegerSocket, MenuSocket, VectorSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputInteger, InputMenu, InputVector

class AntiAliasing(BaseNode):
    _bl_idname = 'CompositorNodeAntiAliasing'

    def __init__(self, image: InputColor=None, threshold: InputFloat=0.2, contrast_limit: InputFloat=2.0, corner_rounding: InputFloat=0.25):
        super().__init__()
        key_args = {'Image': image, 'Threshold': threshold, 'Contrast Limit': contrast_limit, 'Corner Rounding': corner_rounding}
        self._establish_links(**key_args)

class BilateralBlur(BaseNode):
    _bl_idname = 'CompositorNodeBilateralblur'

    def __init__(self, image: InputColor=None, determinator: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputInteger=0, threshold: InputFloat=0.1):
        super().__init__()
        key_args = {'Image': image, 'Determinator': determinator, 'Size': size, 'Threshold': threshold}
        self._establish_links(**key_args)

class Blur(BaseNode):
    _bl_idname = 'CompositorNodeBlur'

    def __init__(self, image: InputColor=None, size: InputVector=(0.0, 0.0), type: InputMenu | Literal['Flat', 'Tent', 'Quadratic', 'Cubic', 'Gaussian', 'Fast Gaussian', 'Catrom', 'Mitch']='Gaussian', extend_bounds: InputBoolean=False, separable: InputBoolean=True):
        super().__init__()
        key_args = {'Image': image, 'Size': size, 'Type': type, 'Extend Bounds': extend_bounds, 'Separable': separable}
        self._establish_links(**key_args)

    @classmethod
    def flat(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Flat')

    @classmethod
    def tent(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Tent')

    @classmethod
    def quadratic(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Quadratic')

    @classmethod
    def cubic(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Cubic')

    @classmethod
    def gaussian(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Gaussian')

    @classmethod
    def fast_gaussian(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Fast Gaussian')

    @classmethod
    def catrom(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Catrom')

    @classmethod
    def mitch(cls, image: InputColor=None, size: InputVector=(0.0, 0.0), extend_bounds: InputBoolean=False, separable: InputBoolean=True) -> 'Blur':
        return cls(image=image, size=size, extend_bounds=extend_bounds, separable=separable, type='Mitch')

class BokehBlur(BaseNode):
    _bl_idname = 'CompositorNodeBokehBlur'

    def __init__(self, image: InputColor=None, bokeh: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputFloat=0.0, mask: InputFloat=1.0, extend_bounds: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'Bokeh': bokeh, 'Size': size, 'Mask': mask, 'Extend Bounds': extend_bounds}
        self._establish_links(**key_args)

class Convolve(BaseNode):
    _bl_idname = 'CompositorNodeConvolve'

    def __init__(self, image: InputColor=None, kernel_data_type: InputMenu | Literal['Float', 'Color']='Float', float_kernel: InputFloat=None, color_kernel: InputColor=None, normalize_kernel: InputBoolean=True):
        super().__init__()
        key_args = {'Image': image, 'Kernel Data Type': kernel_data_type, 'Float Kernel': float_kernel, 'Color Kernel': color_kernel, 'Normalize Kernel': normalize_kernel}
        self._establish_links(**key_args)

class Defocus(BaseNode):
    _bl_idname = 'CompositorNodeDefocus'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), z: InputFloat=1.0, *, bokeh: Literal['OCTAGON', 'HEPTAGON', 'HEXAGON', 'PENTAGON', 'SQUARE', 'TRIANGLE', 'CIRCLE']='CIRCLE', angle: float=0.0, f_stop: float=0.0, blur_max: float=0.0, use_zbuffer: bool=True, z_scale: float=0.0):
        super().__init__()
        key_args = {'Image': image, 'Z': z}
        self.bokeh = bokeh
        self.angle = angle
        self.f_stop = f_stop
        self.blur_max = blur_max
        self.use_zbuffer = use_zbuffer
        self.z_scale = z_scale
        self._establish_links(**key_args)

    @property
    def bokeh(self) -> Literal['OCTAGON', 'HEPTAGON', 'HEXAGON', 'PENTAGON', 'SQUARE', 'TRIANGLE', 'CIRCLE']:
        return self.node.bokeh

    @bokeh.setter
    def bokeh(self, value: Literal['OCTAGON', 'HEPTAGON', 'HEXAGON', 'PENTAGON', 'SQUARE', 'TRIANGLE', 'CIRCLE']) -> None:
        set_property(self.node, 'bokeh', value)

    @property
    def angle(self) -> float:
        return self.node.angle

    @angle.setter
    def angle(self, value: float) -> None:
        set_property(self.node, 'angle', value)

    @property
    def f_stop(self) -> float:
        return self.node.f_stop

    @f_stop.setter
    def f_stop(self, value: float) -> None:
        set_property(self.node, 'f_stop', value)

    @property
    def blur_max(self) -> float:
        return self.node.blur_max

    @blur_max.setter
    def blur_max(self, value: float) -> None:
        set_property(self.node, 'blur_max', value)

    @property
    def use_zbuffer(self) -> bool:
        return self.node.use_zbuffer

    @use_zbuffer.setter
    def use_zbuffer(self, value: bool) -> None:
        set_property(self.node, 'use_zbuffer', value)

    @property
    def z_scale(self) -> float:
        return self.node.z_scale

    @z_scale.setter
    def z_scale(self, value: float) -> None:
        set_property(self.node, 'z_scale', value)

class Denoise(BaseNode):
    _bl_idname = 'CompositorNodeDenoise'

    def __init__(self, image: InputColor=None, albedo: InputColor=None, normal: InputVector=None, hdr: InputBoolean=True, prefilter: InputMenu | Literal['None', 'Fast', 'Accurate']='Accurate', quality: InputMenu | Literal['Follow Scene', 'High', 'Balanced', 'Fast']='Follow Scene'):
        super().__init__()
        key_args = {'Image': image, 'Albedo': albedo, 'Normal': normal, 'HDR': hdr, 'Prefilter': prefilter, 'Quality': quality}
        self._establish_links(**key_args)

class Despeckle(BaseNode):
    _bl_idname = 'CompositorNodeDespeckle'

    def __init__(self, image: InputColor=None, fac: InputFloat=1.0, color_threshold: InputFloat=0.5, neighbor_threshold: InputFloat=0.5):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac, 'Color Threshold': color_threshold, 'Neighbor Threshold': neighbor_threshold}
        self._establish_links(**key_args)

class DilateErode(BaseNode):
    _bl_idname = 'CompositorNodeDilateErode'

    def __init__(self, mask: InputFloat=0.0, size: InputInteger=0, type: InputMenu | Literal['Steps', 'Threshold', 'Distance', 'Feather']='Steps', falloff_size: InputFloat=0.0, falloff: InputMenu | Literal['Smooth', 'Sphere', 'Root', 'Inverse Square', 'Sharp', 'Linear']='Smooth'):
        super().__init__()
        key_args = {'Mask': mask, 'Size': size, 'Type': type, 'Falloff Size': falloff_size, 'Falloff': falloff}
        self._establish_links(**key_args)

    @classmethod
    def steps(cls, mask: InputFloat=0.0, size: InputInteger=0) -> 'DilateErode':
        return cls(mask=mask, size=size, type='Steps')

    @classmethod
    def threshold(cls, mask: InputFloat=0.0, size: InputInteger=0, falloff_size: InputFloat=0.0) -> 'DilateErode':
        return cls(mask=mask, size=size, falloff_size=falloff_size, type='Threshold')

    @classmethod
    def distance(cls, mask: InputFloat=0.0, size: InputInteger=0) -> 'DilateErode':
        return cls(mask=mask, size=size, type='Distance')

    @classmethod
    def feather(cls, mask: InputFloat=0.0, size: InputInteger=0, falloff: InputMenu | Literal['Smooth', 'Sphere', 'Root', 'Inverse Square', 'Sharp', 'Linear']='Smooth') -> 'DilateErode':
        return cls(mask=mask, size=size, falloff=falloff, type='Feather')

class DirectionalBlur(BaseNode):
    _bl_idname = 'CompositorNodeDBlur'

    def __init__(self, image: InputColor=None, samples: InputInteger=1, center: InputVector=(0.5, 0.5), rotation: InputFloat=0.0, scale: InputFloat=1.0, translation_amount: InputFloat=0.0, translation_direction: InputFloat=0.0):
        super().__init__()
        key_args = {'Image': image, 'Samples': samples, 'Center': center, 'Rotation': rotation, 'Scale': scale, 'Translation Amount': translation_amount, 'Translation Direction': translation_direction}
        self._establish_links(**key_args)

class Filter(BaseNode):
    _bl_idname = 'CompositorNodeFilter'

    def __init__(self, image: InputColor=None, fac: InputFloat=1.0, type: InputMenu | Literal['Soften', 'Box Sharpen', 'Diamond Sharpen', 'Laplace', 'Sobel', 'Prewitt', 'Kirsch', 'Shadow']='Soften'):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac, 'Type': type}
        self._establish_links(**key_args)

    @classmethod
    def soften(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Soften')

    @classmethod
    def box_sharpen(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Box Sharpen')

    @classmethod
    def diamond_sharpen(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Diamond Sharpen')

    @classmethod
    def laplace(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Laplace')

    @classmethod
    def sobel(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Sobel')

    @classmethod
    def prewitt(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Prewitt')

    @classmethod
    def kirsch(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Kirsch')

    @classmethod
    def shadow(cls, image: InputColor=None, fac: InputFloat=1.0) -> 'Filter':
        return cls(image=image, fac=fac, type='Shadow')

class Glare(BaseNode):
    _bl_idname = 'CompositorNodeGlare'

    def __init__(self, image: InputColor=None, type: InputMenu | Literal['Bloom', 'Ghosts', 'Streaks', 'Fog Glow', 'Simple Star', 'Sun Beams', 'Kernel']='Streaks', quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputFloat=0.5, streaks: InputInteger=4, streaks_angle: InputFloat=0.0, iterations: InputInteger=3, fade: InputFloat=0.9, color_modulation: InputFloat=0.25, diagonal_star: InputBoolean=True, sun_position: InputVector=(0.5, 0.5), jitter: InputFloat=0.0, kernel_data_type: InputMenu | Literal['Float', 'Color']='Float', float_kernel: InputFloat=None, color_kernel: InputColor=None):
        super().__init__()
        key_args = {'Image': image, 'Type': type, 'Quality': quality, 'Highlights Threshold': highlights_threshold, 'Highlights Smoothness': highlights_smoothness, 'Clamp Highlights': clamp_highlights, 'Maximum Highlights': maximum_highlights, 'Strength': strength, 'Saturation': saturation, 'Tint': tint, 'Size': size, 'Streaks': streaks, 'Streaks Angle': streaks_angle, 'Iterations': iterations, 'Fade': fade, 'Color Modulation': color_modulation, 'Diagonal Star': diagonal_star, 'Sun Position': sun_position, 'Jitter': jitter, 'Kernel Data Type': kernel_data_type, 'Float Kernel': float_kernel, 'Color Kernel': color_kernel}
        self._establish_links(**key_args)

    @classmethod
    def bloom(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputFloat=0.5) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, size=size, type='Bloom')

    @classmethod
    def ghosts(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), iterations: InputInteger=3, color_modulation: InputFloat=0.25) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, iterations=iterations, color_modulation=color_modulation, type='Ghosts')

    @classmethod
    def streaks(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), streaks: InputInteger=4, streaks_angle: InputFloat=0.0, iterations: InputInteger=3, fade: InputFloat=0.9, color_modulation: InputFloat=0.25) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, streaks=streaks, streaks_angle=streaks_angle, iterations=iterations, fade=fade, color_modulation=color_modulation, type='Streaks')

    @classmethod
    def fog_glow(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputFloat=0.5) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, size=size, type='Fog Glow')

    @classmethod
    def simple_star(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), iterations: InputInteger=3, fade: InputFloat=0.9, diagonal_star: InputBoolean=True) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, iterations=iterations, fade=fade, diagonal_star=diagonal_star, type='Simple Star')

    @classmethod
    def sun_beams(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), size: InputFloat=0.5, sun_position: InputVector=(0.5, 0.5), jitter: InputFloat=0.0) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, size=size, sun_position=sun_position, jitter=jitter, type='Sun Beams')

    @classmethod
    def kernel(cls, image: InputColor=None, quality: InputMenu | Literal['High', 'Medium', 'Low']='Medium', highlights_threshold: InputFloat=1.0, highlights_smoothness: InputFloat=0.1, clamp_highlights: InputBoolean=False, maximum_highlights: InputFloat=10.0, strength: InputFloat=1.0, saturation: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), kernel_data_type: InputMenu | Literal['Float', 'Color']='Float', float_kernel: InputFloat=None) -> 'Glare':
        return cls(image=image, quality=quality, highlights_threshold=highlights_threshold, highlights_smoothness=highlights_smoothness, clamp_highlights=clamp_highlights, maximum_highlights=maximum_highlights, strength=strength, saturation=saturation, tint=tint, kernel_data_type=kernel_data_type, float_kernel=float_kernel, type='Kernel')

class Inpaint(BaseNode):
    _bl_idname = 'CompositorNodeInpaint'

    def __init__(self, image: InputColor=None, size: InputInteger=0):
        super().__init__()
        key_args = {'Image': image, 'Size': size}
        self._establish_links(**key_args)

class Kuwahara(BaseNode):
    _bl_idname = 'CompositorNodeKuwahara'

    def __init__(self, image: InputColor=None, size: InputFloat=6.0, type: InputMenu | Literal['Classic', 'Anisotropic']='Anisotropic', uniformity: InputInteger=4, sharpness: InputFloat=1.0, eccentricity: InputFloat=1.0, high_precision: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'Size': size, 'Type': type, 'Uniformity': uniformity, 'Sharpness': sharpness, 'Eccentricity': eccentricity, 'High Precision': high_precision}
        self._establish_links(**key_args)

    @classmethod
    def classic(cls, image: InputColor=None, size: InputFloat=6.0, high_precision: InputBoolean=False) -> 'Kuwahara':
        return cls(image=image, size=size, high_precision=high_precision, type='Classic')

    @classmethod
    def anisotropic(cls, image: InputColor=None, size: InputFloat=6.0, uniformity: InputInteger=4, sharpness: InputFloat=1.0, eccentricity: InputFloat=1.0) -> 'Kuwahara':
        return cls(image=image, size=size, uniformity=uniformity, sharpness=sharpness, eccentricity=eccentricity, type='Anisotropic')

class MaskToSDF(BaseNode):
    _bl_idname = 'CompositorNodeMaskToSDF'

    def __init__(self, mask: InputBoolean=None):
        super().__init__()
        key_args = {'Mask': mask}
        self._establish_links(**key_args)

class Pixelate(BaseNode):
    _bl_idname = 'CompositorNodePixelate'

    def __init__(self, color: InputColor=None, size: InputInteger=1):
        super().__init__()
        key_args = {'Color': color, 'Size': size}
        self._establish_links(**key_args)

class VectorBlur(BaseNode):
    _bl_idname = 'CompositorNodeVecBlur'

    def __init__(self, image: InputColor=None, speed: InputVector=(0.0, 0.0, 0.0, 0.0), z: InputFloat=0.0, samples: InputInteger=32, shutter: InputFloat=0.5):
        super().__init__()
        key_args = {'Image': image, 'Speed': speed, 'Z': z, 'Samples': samples, 'Shutter': shutter}
        self._establish_links(**key_args)
