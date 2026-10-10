# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, FontSocket, IntegerSocket, MenuSocket, StringSocket, VectorSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputFont, InputInteger, InputIntegerVector, InputMenu, InputString

class BlankImage(BaseNode):
    _bl_idname = 'CompositorNodeBlankImage'

    def __init__(self, color: InputColor=(0.0, 0.0, 0.0, 1.0), size: InputIntegerVector=(1920, 1080)):
        super().__init__()
        key_args = {'Color': color, 'Size': size}
        self._establish_links(**key_args)

class BokehImage(BaseNode):
    _bl_idname = 'CompositorNodeBokehImage'

    def __init__(self, flaps: InputInteger=5, angle: InputFloat=0.0, roundness: InputFloat=0.0, catadioptric_size: InputFloat=0.0, color_shift: InputFloat=0.0):
        super().__init__()
        key_args = {'Flaps': flaps, 'Angle': angle, 'Roundness': roundness, 'Catadioptric Size': catadioptric_size, 'Color Shift': color_shift}
        self._establish_links(**key_args)

class Color(BaseNode):
    _bl_idname = 'CompositorNodeRGB'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class ImageCoordinates(BaseNode):
    _bl_idname = 'CompositorNodeImageCoordinates'

    def __init__(self, image: InputColor=None):
        super().__init__()
        key_args = {'Image': image}
        self._establish_links(**key_args)

class ImageInfo(BaseNode):
    _bl_idname = 'CompositorNodeImageInfo'

    def __init__(self, image: InputColor=None):
        super().__init__()
        key_args = {'Image': image}
        self._establish_links(**key_args)

class Mask(BaseNode):
    _bl_idname = 'CompositorNodeMask'

    def __init__(self, size_source: InputMenu | Literal['Scene Size', 'Fixed', 'Fixed/Scene']='Scene Size', size_x: InputInteger=256, size_y: InputInteger=256, feather: InputBoolean=True, motion_blur: InputBoolean=False, motion_blur_samples: InputInteger=16, motion_blur_shutter: InputFloat=0.5):
        super().__init__()
        key_args = {'Size Source': size_source, 'Size X': size_x, 'Size Y': size_y, 'Feather': feather, 'Motion Blur': motion_blur, 'Motion Blur Samples': motion_blur_samples, 'Motion Blur Shutter': motion_blur_shutter}
        self._establish_links(**key_args)

class MovieClip(BaseNode):
    _bl_idname = 'CompositorNodeMovieClip'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class Normal(BaseNode):
    _bl_idname = 'CompositorNodeNormal'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class RenderLayers(BaseNode):
    _bl_idname = 'CompositorNodeRLayers'

    def __init__(self, layer: str='ViewLayer'):
        super().__init__()
        key_args = {}
        self.layer = layer
        self._establish_links(**key_args)

    @property
    def layer(self) -> str:
        return self.node.layer

    @layer.setter
    def layer(self, value: str) -> None:
        set_property(self.node, 'layer', value)

class SceneTime(BaseNode):
    _bl_idname = 'CompositorNodeSceneTime'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class SequencerStripInfo(BaseNode):
    _bl_idname = 'CompositorNodeSequencerStripInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class StringToImage(BaseNode):
    _bl_idname = 'CompositorNodeStringToImage'

    def __init__(self, string: InputString='', font: InputFont=None, size: InputFloat=128.0, horizontal_alignment: InputMenu | Literal['Left', 'Center', 'Right']='Center', vertical_alignment: InputMenu | Literal['Top', 'Top Baseline', 'Middle', 'Bottom Baseline', 'Bottom']='Middle', wrap: InputBoolean=True, wrap_width: InputInteger=1920):
        super().__init__()
        key_args = {'String': string, 'Font': font, 'Size': size, 'Horizontal Alignment': horizontal_alignment, 'Vertical Alignment': vertical_alignment, 'Wrap': wrap, 'Wrap Width': wrap_width}
        self._establish_links(**key_args)

class TimeCurve(BaseNode):
    _bl_idname = 'CompositorNodeTime'

    def __init__(self, start_frame: InputInteger=1, end_frame: InputInteger=250):
        super().__init__()
        key_args = {'Start Frame': start_frame, 'End Frame': end_frame}
        self._establish_links(**key_args)

class TrackPosition(BaseNode):
    _bl_idname = 'CompositorNodeTrackPos'

    def __init__(self, mode: InputMenu | Literal['Absolute', 'Relative Start', 'Relative Frame', 'Absolute Frame']='Absolute', frame: InputInteger=0, *, tracking_object: str='', track_name: str=''):
        super().__init__()
        key_args = {'Mode': mode, 'Frame': frame}
        self.tracking_object = tracking_object
        self.track_name = track_name
        self._establish_links(**key_args)

    @property
    def tracking_object(self) -> str:
        return self.node.tracking_object

    @tracking_object.setter
    def tracking_object(self, value: str) -> None:
        set_property(self.node, 'tracking_object', value)

    @property
    def track_name(self) -> str:
        return self.node.track_name

    @track_name.setter
    def track_name(self, value: str) -> None:
        set_property(self.node, 'track_name', value)
