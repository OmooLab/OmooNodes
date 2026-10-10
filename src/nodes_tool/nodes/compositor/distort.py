# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, IntegerSocket, MenuSocket, VectorSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputInteger, InputMenu, InputVector

class CornerPin(BaseNode):
    _bl_idname = 'CompositorNodeCornerPin'

    def __init__(self, image: InputColor=None, upper_left: InputVector=(0.0, 1.0), upper_right: InputVector=(1.0, 1.0), lower_left: InputVector=(0.0, 0.0), lower_right: InputVector=(1.0, 0.0), interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'Upper Left': upper_left, 'Upper Right': upper_right, 'Lower Left': lower_left, 'Lower Right': lower_right, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class Crop(BaseNode):
    _bl_idname = 'CompositorNodeCrop'

    def __init__(self, image: InputColor=None, x: InputInteger=0, y: InputInteger=0, width: InputInteger=1920, height: InputInteger=1080, alpha_crop: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'X': x, 'Y': y, 'Width': width, 'Height': height, 'Alpha Crop': alpha_crop}
        self._establish_links(**key_args)

class Displace(BaseNode):
    _bl_idname = 'CompositorNodeDisplace'

    def __init__(self, image: InputColor=None, displacement: InputVector=(0.0, 0.0), interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'Displacement': displacement, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class Flip(BaseNode):
    _bl_idname = 'CompositorNodeFlip'

    def __init__(self, image: InputColor=None, flip_x: InputBoolean=False, flip_y: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'Flip X': flip_x, 'Flip Y': flip_y}
        self._establish_links(**key_args)

class LensDistortion(BaseNode):
    _bl_idname = 'CompositorNodeLensdist'

    def __init__(self, image: InputColor=None, type: InputMenu | Literal['Radial', 'Horizontal']='Radial', distortion: InputFloat=0.0, dispersion: InputFloat=0.0, jitter: InputBoolean=False, fit: InputBoolean=False):
        super().__init__()
        key_args = {'Image': image, 'Type': type, 'Distortion': distortion, 'Dispersion': dispersion, 'Jitter': jitter, 'Fit': fit}
        self._establish_links(**key_args)

    @classmethod
    def radial(cls, image: InputColor=None, distortion: InputFloat=0.0, dispersion: InputFloat=0.0, jitter: InputBoolean=False, fit: InputBoolean=False) -> 'LensDistortion':
        return cls(image=image, distortion=distortion, dispersion=dispersion, jitter=jitter, fit=fit, type='Radial')

    @classmethod
    def horizontal(cls, image: InputColor=None, dispersion: InputFloat=0.0) -> 'LensDistortion':
        return cls(image=image, dispersion=dispersion, type='Horizontal')

class MapUV(BaseNode):
    _bl_idname = 'CompositorNodeMapUV'

    def __init__(self, image: InputColor=None, uv: InputVector=(1.0, 0.0, 0.0), interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'UV': uv, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class MovieDistortion(BaseNode):
    _bl_idname = 'CompositorNodeMovieDistortion'

    def __init__(self, image: InputColor=(0.8, 0.8, 0.8, 1.0), type: InputMenu | Literal['Undistort', 'Distort']='Undistort'):
        super().__init__()
        key_args = {'Image': image, 'Type': type}
        self._establish_links(**key_args)

    @classmethod
    def undistort(cls, image: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'MovieDistortion':
        return cls(image=image, type='Undistort')

    @classmethod
    def distort(cls, image: InputColor=(0.8, 0.8, 0.8, 1.0)) -> 'MovieDistortion':
        return cls(image=image, type='Distort')

class PlaneTrackDeform(BaseNode):
    _bl_idname = 'CompositorNodePlaneTrackDeform'

    def __init__(self, image: InputColor=None, motion_blur: InputBoolean=False, motion_blur_samples: InputInteger=16, motion_blur_shutter: InputFloat=0.5, *, tracking_object: str='', plane_track_name: str=''):
        super().__init__()
        key_args = {'Image': image, 'Motion Blur': motion_blur, 'Motion Blur Samples': motion_blur_samples, 'Motion Blur Shutter': motion_blur_shutter}
        self.tracking_object = tracking_object
        self.plane_track_name = plane_track_name
        self._establish_links(**key_args)

    @property
    def tracking_object(self) -> str:
        return self.node.tracking_object

    @tracking_object.setter
    def tracking_object(self, value: str) -> None:
        set_property(self.node, 'tracking_object', value)

    @property
    def plane_track_name(self) -> str:
        return self.node.plane_track_name

    @plane_track_name.setter
    def plane_track_name(self, value: str) -> None:
        set_property(self.node, 'plane_track_name', value)

class Rotate(BaseNode):
    _bl_idname = 'CompositorNodeRotate'

    def __init__(self, image: InputColor=None, angle: InputFloat=0.0, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'Angle': angle, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class Scale(BaseNode):
    _bl_idname = 'CompositorNodeScale'

    def __init__(self, image: InputColor=None, type: InputMenu | Literal['Relative', 'Absolute', 'Scene Size', 'Render Size']='Relative', x: InputFloat=1.0, y: InputFloat=1.0, frame_type: InputMenu | Literal['Stretch', 'Fit', 'Crop']='Stretch', interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'Type': type, 'X': x, 'Y': y, 'Frame Type': frame_type, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

    @classmethod
    def relative(cls, image: InputColor=None, x: InputFloat=1.0, y: InputFloat=1.0, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip') -> 'Scale':
        return cls(image=image, x=x, y=y, interpolation=interpolation, extension_x=extension_x, extension_y=extension_y, type='Relative')

    @classmethod
    def absolute(cls, image: InputColor=None, x: InputFloat=1.0, y: InputFloat=1.0, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip') -> 'Scale':
        return cls(image=image, x=x, y=y, interpolation=interpolation, extension_x=extension_x, extension_y=extension_y, type='Absolute')

    @classmethod
    def scene_size(cls, image: InputColor=None, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip') -> 'Scale':
        return cls(image=image, interpolation=interpolation, extension_x=extension_x, extension_y=extension_y, type='Scene Size')

    @classmethod
    def render_size(cls, image: InputColor=None, frame_type: InputMenu | Literal['Stretch', 'Fit', 'Crop']='Stretch', interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip') -> 'Scale':
        return cls(image=image, frame_type=frame_type, interpolation=interpolation, extension_x=extension_x, extension_y=extension_y, type='Render Size')

class Stabilize2D(BaseNode):
    _bl_idname = 'CompositorNodeStabilize'

    def __init__(self, image: InputColor=None, frame: InputInteger=None, invert: InputBoolean=False, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'Frame': frame, 'Invert': invert, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class Transform(BaseNode):
    _bl_idname = 'CompositorNodeTransform'

    def __init__(self, image: InputColor=None, x: InputFloat=0.0, y: InputFloat=0.0, angle: InputFloat=0.0, scale: InputFloat=1.0, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'X': x, 'Y': y, 'Angle': angle, 'Scale': scale, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)

class Translate(BaseNode):
    _bl_idname = 'CompositorNodeTranslate'

    def __init__(self, image: InputColor=None, x: InputFloat=0.0, y: InputFloat=0.0, interpolation: InputMenu | Literal['Nearest', 'Bilinear', 'Bicubic', 'Anisotropic']='Bilinear', extension_x: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip', extension_y: InputMenu | Literal['Clip', 'Extend', 'Repeat']='Clip'):
        super().__init__()
        key_args = {'Image': image, 'X': x, 'Y': y, 'Interpolation': interpolation, 'Extension X': extension_x, 'Extension Y': extension_y}
        self._establish_links(**key_args)
