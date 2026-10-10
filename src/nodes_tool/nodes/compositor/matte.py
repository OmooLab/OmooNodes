# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
import math
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, IntegerSocket, MenuSocket, VectorSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputInteger, InputMenu, InputVector

class BoxMask(BaseNode):
    _bl_idname = 'CompositorNodeBoxMask'

    def __init__(self, operation: InputMenu | Literal['Add', 'Subtract', 'Multiply', 'Not']='Add', mask: InputFloat=0.0, value: InputFloat=1.0, position: InputVector=(0.5, 0.5), size: InputVector=(0.2, 0.1), rotation: InputFloat=0.0):
        super().__init__()
        key_args = {'Operation': operation, 'Mask': mask, 'Value': value, 'Position': position, 'Size': size, 'Rotation': rotation}
        self._establish_links(**key_args)

class ChannelKey(BaseNode):
    _bl_idname = 'CompositorNodeChannelMatte'

    def __init__(self, image: InputColor=None, minimum: InputFloat=0.0, maximum: InputFloat=1.0, color_space: InputMenu | Literal['RGB', 'HSV', 'YUV', 'YCbCr']='RGB', rgb_key_channel: InputMenu | Literal['R', 'G', 'B']='G', hsv_key_channel: InputMenu | Literal['H', 'S', 'V']='H', yuv_key_channel: InputMenu | Literal['Y', 'U', 'V']='V', ycbcr_key_channel: InputMenu | Literal['Y', 'Cb', 'Cr']='Cr', limit_method: InputMenu | Literal['Single', 'Max']='Max', rgb_limit_channel: InputMenu | Literal['R', 'G', 'B']='R', hsv_limit_channel: InputMenu | Literal['H', 'S', 'V']='S', yuv_limit_channel: InputMenu | Literal['Y', 'U', 'V']='U', ycbcr_limit_channel: InputMenu | Literal['Y', 'Cb', 'Cr']='Cb'):
        super().__init__()
        key_args = {'Image': image, 'Minimum': minimum, 'Maximum': maximum, 'Color Space': color_space, 'RGB Key Channel': rgb_key_channel, 'HSV Key Channel': hsv_key_channel, 'YUV Key Channel': yuv_key_channel, 'YCbCr Key Channel': ycbcr_key_channel, 'Limit Method': limit_method, 'RGB Limit Channel': rgb_limit_channel, 'HSV Limit Channel': hsv_limit_channel, 'YUV Limit Channel': yuv_limit_channel, 'YCbCr Limit Channel': ycbcr_limit_channel}
        self._establish_links(**key_args)

class ChromaKey(BaseNode):
    _bl_idname = 'CompositorNodeChromaMatte'

    def __init__(self, image: InputColor=None, key_color: InputColor=(1.0, 1.0, 1.0, 1.0), minimum: InputFloat=0.17453292, maximum: InputFloat=math.pi / 6, falloff: InputFloat=1.0):
        super().__init__()
        key_args = {'Image': image, 'Key Color': key_color, 'Minimum': minimum, 'Maximum': maximum, 'Falloff': falloff}
        self._establish_links(**key_args)

class ColorKey(BaseNode):
    _bl_idname = 'CompositorNodeColorMatte'

    def __init__(self, image: InputColor=None, key_color: InputColor=(1.0, 1.0, 1.0, 1.0), hue: InputFloat=0.01, saturation: InputFloat=0.1, value: InputFloat=0.1):
        super().__init__()
        key_args = {'Image': image, 'Key Color': key_color, 'Hue': hue, 'Saturation': saturation, 'Value': value}
        self._establish_links(**key_args)

class ColorSpill(BaseNode):
    _bl_idname = 'CompositorNodeColorSpill'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, spill_channel: InputMenu | Literal['R', 'G', 'B']='G', limit_method: InputMenu | Literal['Single', 'Average']='Single', limit_channel: InputMenu | Literal['R', 'G', 'B']='R', limit_strength: InputFloat=1.0, use_spill_strength: InputBoolean=False, spill_strength: InputColor=(0.0, 1.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac, 'Spill Channel': spill_channel, 'Limit Method': limit_method, 'Limit Channel': limit_channel, 'Limit Strength': limit_strength, 'Use Spill Strength': use_spill_strength, 'Spill Strength': spill_strength}
        self._establish_links(**key_args)

class DifferenceKey(BaseNode):
    _bl_idname = 'CompositorNodeDiffMatte'

    def __init__(self, image_1: InputColor=(1.0, 1.0, 1.0, 1.0), image_2: InputColor=(1.0, 1.0, 1.0, 1.0), tolerance: InputFloat=0.1, falloff: InputFloat=0.1):
        super().__init__()
        key_args = {'Image 1': image_1, 'Image 2': image_2, 'Tolerance': tolerance, 'Falloff': falloff}
        self._establish_links(**key_args)

class DistanceKey(BaseNode):
    _bl_idname = 'CompositorNodeDistanceMatte'

    def __init__(self, image: InputColor=None, key_color: InputColor=(1.0, 1.0, 1.0, 1.0), color_space: InputMenu | Literal['RGB', 'YCC']='RGB', tolerance: InputFloat=0.1, falloff: InputFloat=0.1):
        super().__init__()
        key_args = {'Image': image, 'Key Color': key_color, 'Color Space': color_space, 'Tolerance': tolerance, 'Falloff': falloff}
        self._establish_links(**key_args)

class DoubleEdgeMask(BaseNode):
    _bl_idname = 'CompositorNodeDoubleEdgeMask'

    def __init__(self, outer_mask: InputFloat=0.8, inner_mask: InputFloat=0.8, image_edges: InputBoolean=False, only_inside_outer: InputBoolean=False):
        super().__init__()
        key_args = {'Outer Mask': outer_mask, 'Inner Mask': inner_mask, 'Image Edges': image_edges, 'Only Inside Outer': only_inside_outer}
        self._establish_links(**key_args)

class EllipseMask(BaseNode):
    _bl_idname = 'CompositorNodeEllipseMask'

    def __init__(self, operation: InputMenu | Literal['Add', 'Subtract', 'Multiply', 'Not']='Add', mask: InputFloat=0.0, value: InputFloat=1.0, position: InputVector=(0.5, 0.5), size: InputVector=(0.2, 0.1), rotation: InputFloat=0.0):
        super().__init__()
        key_args = {'Operation': operation, 'Mask': mask, 'Value': value, 'Position': position, 'Size': size, 'Rotation': rotation}
        self._establish_links(**key_args)

class Keying(BaseNode):
    _bl_idname = 'CompositorNodeKeying'

    def __init__(self, image: InputColor=None, key_color: InputColor=(1.0, 1.0, 1.0, 1.0), preprocess_blur_size: InputInteger=0, key_balance: InputFloat=0.5, black_level: InputFloat=0.0, white_level: InputFloat=1.0, edge_search_size: InputInteger=3, edge_tolerance: InputFloat=0.1, garbage_matte: InputFloat=0.0, core_matte: InputFloat=0.0, postprocess_blur_size: InputInteger=0, postprocess_dilate_size: InputInteger=0, postprocess_feather_size: InputInteger=0, feather_falloff: InputMenu | Literal['Smooth', 'Sphere', 'Root', 'Inverse Square', 'Sharp', 'Linear']='Smooth', despill_strength: InputFloat=1.0, despill_balance: InputFloat=0.5):
        super().__init__()
        key_args = {'Image': image, 'Key Color': key_color, 'Preprocess Blur Size': preprocess_blur_size, 'Key Balance': key_balance, 'Black Level': black_level, 'White Level': white_level, 'Edge Search Size': edge_search_size, 'Edge Tolerance': edge_tolerance, 'Garbage Matte': garbage_matte, 'Core Matte': core_matte, 'Postprocess Blur Size': postprocess_blur_size, 'Postprocess Dilate Size': postprocess_dilate_size, 'Postprocess Feather Size': postprocess_feather_size, 'Feather Falloff': feather_falloff, 'Despill Strength': despill_strength, 'Despill Balance': despill_balance}
        self._establish_links(**key_args)

class KeyingScreen(BaseNode):
    _bl_idname = 'CompositorNodeKeyingScreen'

    def __init__(self, smoothness: InputFloat=0.0, *, tracking_object: str=''):
        super().__init__()
        key_args = {'Smoothness': smoothness}
        self.tracking_object = tracking_object
        self._establish_links(**key_args)

    @property
    def tracking_object(self) -> str:
        return self.node.tracking_object

    @tracking_object.setter
    def tracking_object(self, value: str) -> None:
        set_property(self.node, 'tracking_object', value)

class LuminanceKey(BaseNode):
    _bl_idname = 'CompositorNodeLumaMatte'

    def __init__(self, image: InputColor=None, minimum: InputFloat=0.0, maximum: InputFloat=1.0):
        super().__init__()
        key_args = {'Image': image, 'Minimum': minimum, 'Maximum': maximum}
        self._establish_links(**key_args)
