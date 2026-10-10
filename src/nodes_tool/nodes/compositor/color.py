# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from mathutils import Color
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, MenuSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputMenu

class AlphaOver(BaseNode):
    _bl_idname = 'CompositorNodeAlphaOver'

    def __init__(self, background: InputColor=(1.0, 1.0, 1.0, 1.0), foreground: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, type: InputMenu | Literal['Over', 'Disjoint Over', 'Conjoint Over']='Over', straight_alpha: InputBoolean=False):
        super().__init__()
        key_args = {'Background': background, 'Foreground': foreground, 'Fac': fac, 'Type': type, 'Straight Alpha': straight_alpha}
        self._establish_links(**key_args)

    @classmethod
    def over(cls, background: InputColor=(1.0, 1.0, 1.0, 1.0), foreground: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, straight_alpha: InputBoolean=False) -> 'AlphaOver':
        return cls(background=background, foreground=foreground, fac=fac, straight_alpha=straight_alpha, type='Over')

    @classmethod
    def disjoint_over(cls, background: InputColor=(1.0, 1.0, 1.0, 1.0), foreground: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, straight_alpha: InputBoolean=False) -> 'AlphaOver':
        return cls(background=background, foreground=foreground, fac=fac, straight_alpha=straight_alpha, type='Disjoint Over')

    @classmethod
    def conjoint_over(cls, background: InputColor=(1.0, 1.0, 1.0, 1.0), foreground: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, straight_alpha: InputBoolean=False) -> 'AlphaOver':
        return cls(background=background, foreground=foreground, fac=fac, straight_alpha=straight_alpha, type='Conjoint Over')

class BrightnessContrast(BaseNode):
    _bl_idname = 'CompositorNodeBrightContrast'

    def __init__(self, image: InputColor=None, bright: InputFloat=0.0, contrast: InputFloat=0.0):
        super().__init__()
        key_args = {'Image': image, 'Bright': bright, 'Contrast': contrast}
        self._establish_links(**key_args)

class ColorBalance(BaseNode):
    _bl_idname = 'CompositorNodeColorBalance'

    def __init__(self, image: InputColor=None, fac: InputFloat=1.0, type: InputMenu | Literal['Lift/Gamma/Gain', 'Offset/Power/Slope (ASC-CDL)', 'White Point']='Lift/Gamma/Gain', base_lift: InputFloat=0.0, color_lift: InputColor=(1.0, 1.0, 1.0, 1.0), base_gamma: InputFloat=1.0, color_gamma: InputColor=(1.0, 1.0, 1.0, 1.0), base_gain: InputFloat=1.0, color_gain: InputColor=(1.0, 1.0, 1.0, 1.0), base_offset: InputFloat=0.0, color_offset: InputColor=(0.0, 0.0, 0.0, 1.0), base_power: InputFloat=1.0, color_power: InputColor=(1.0, 1.0, 1.0, 1.0), base_slope: InputFloat=1.0, color_slope: InputColor=(1.0, 1.0, 1.0, 1.0), input_temperature: InputFloat=6500.0, input_tint: InputFloat=10.0, output_temperature: InputFloat=6500.0, output_tint: InputFloat=10.0, *, input_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735), output_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735)):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac, 'Type': type, 'Base Lift': base_lift, 'Color Lift': color_lift, 'Base Gamma': base_gamma, 'Color Gamma': color_gamma, 'Base Gain': base_gain, 'Color Gain': color_gain, 'Base Offset': base_offset, 'Color Offset': color_offset, 'Base Power': base_power, 'Color Power': color_power, 'Base Slope': base_slope, 'Color Slope': color_slope, 'Input Temperature': input_temperature, 'Input Tint': input_tint, 'Output Temperature': output_temperature, 'Output Tint': output_tint}
        self.input_whitepoint = input_whitepoint
        self.output_whitepoint = output_whitepoint
        self._establish_links(**key_args)

    @classmethod
    def lift_gamma_gain(cls, image: InputColor=None, fac: InputFloat=1.0, base_lift: InputFloat=0.0, color_lift: InputColor=(1.0, 1.0, 1.0, 1.0), base_gamma: InputFloat=1.0, color_gamma: InputColor=(1.0, 1.0, 1.0, 1.0), base_gain: InputFloat=1.0, color_gain: InputColor=(1.0, 1.0, 1.0, 1.0), *, input_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735), output_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735)) -> 'ColorBalance':
        return cls(image=image, fac=fac, base_lift=base_lift, color_lift=color_lift, base_gamma=base_gamma, color_gamma=color_gamma, base_gain=base_gain, color_gain=color_gain, input_whitepoint=input_whitepoint, output_whitepoint=output_whitepoint, type='Lift/Gamma/Gain')

    @classmethod
    def offset_power_slope_asc_cdl(cls, image: InputColor=None, fac: InputFloat=1.0, base_offset: InputFloat=0.0, color_offset: InputColor=(0.0, 0.0, 0.0, 1.0), base_power: InputFloat=1.0, color_power: InputColor=(1.0, 1.0, 1.0, 1.0), base_slope: InputFloat=1.0, color_slope: InputColor=(1.0, 1.0, 1.0, 1.0), *, input_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735), output_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735)) -> 'ColorBalance':
        return cls(image=image, fac=fac, base_offset=base_offset, color_offset=color_offset, base_power=base_power, color_power=color_power, base_slope=base_slope, color_slope=color_slope, input_whitepoint=input_whitepoint, output_whitepoint=output_whitepoint, type='Offset/Power/Slope (ASC-CDL)')

    @classmethod
    def white_point(cls, image: InputColor=None, fac: InputFloat=1.0, input_temperature: InputFloat=6500.0, input_tint: InputFloat=10.0, output_temperature: InputFloat=6500.0, output_tint: InputFloat=10.0, *, input_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735), output_whitepoint: tuple[float, float, float]=(0.735, 0.735, 0.735)) -> 'ColorBalance':
        return cls(image=image, fac=fac, input_temperature=input_temperature, input_tint=input_tint, output_temperature=output_temperature, output_tint=output_tint, input_whitepoint=input_whitepoint, output_whitepoint=output_whitepoint, type='White Point')

    @property
    def input_whitepoint(self) -> Color:
        return self.node.input_whitepoint

    @input_whitepoint.setter
    def input_whitepoint(self, value: Color | tuple[float, float, float]) -> None:
        set_property(self.node, 'input_whitepoint', value)

    @property
    def output_whitepoint(self) -> Color:
        return self.node.output_whitepoint

    @output_whitepoint.setter
    def output_whitepoint(self, value: Color | tuple[float, float, float]) -> None:
        set_property(self.node, 'output_whitepoint', value)

class ColorCorrection(BaseNode):
    _bl_idname = 'CompositorNodeColorCorrection'

    def __init__(self, image: InputColor=None, mask: InputFloat=1.0, master_saturation: InputFloat=1.0, master_contrast: InputFloat=1.0, master_gamma: InputFloat=1.0, master_gain: InputFloat=1.0, master_offset: InputFloat=0.0, highlights_saturation: InputFloat=1.0, highlights_contrast: InputFloat=1.0, highlights_gamma: InputFloat=1.0, highlights_gain: InputFloat=1.0, highlights_offset: InputFloat=0.0, midtones_saturation: InputFloat=1.0, midtones_contrast: InputFloat=1.0, midtones_gamma: InputFloat=1.0, midtones_gain: InputFloat=1.0, midtones_offset: InputFloat=0.0, shadows_saturation: InputFloat=1.0, shadows_contrast: InputFloat=1.0, shadows_gamma: InputFloat=1.0, shadows_gain: InputFloat=1.0, shadows_offset: InputFloat=0.0, midtones_start: InputFloat=0.2, midtones_end: InputFloat=0.7, apply_on_red: InputBoolean=True, apply_on_green: InputBoolean=True, apply_on_blue: InputBoolean=True):
        super().__init__()
        key_args = {'Image': image, 'Mask': mask, 'Master Saturation': master_saturation, 'Master Contrast': master_contrast, 'Master Gamma': master_gamma, 'Master Gain': master_gain, 'Master Offset': master_offset, 'Highlights Saturation': highlights_saturation, 'Highlights Contrast': highlights_contrast, 'Highlights Gamma': highlights_gamma, 'Highlights Gain': highlights_gain, 'Highlights Offset': highlights_offset, 'Midtones Saturation': midtones_saturation, 'Midtones Contrast': midtones_contrast, 'Midtones Gamma': midtones_gamma, 'Midtones Gain': midtones_gain, 'Midtones Offset': midtones_offset, 'Shadows Saturation': shadows_saturation, 'Shadows Contrast': shadows_contrast, 'Shadows Gamma': shadows_gamma, 'Shadows Gain': shadows_gain, 'Shadows Offset': shadows_offset, 'Midtones Start': midtones_start, 'Midtones End': midtones_end, 'Apply On Red': apply_on_red, 'Apply On Green': apply_on_green, 'Apply On Blue': apply_on_blue}
        self._establish_links(**key_args)

class DepthCombine(BaseNode):
    _bl_idname = 'CompositorNodeZcombine'

    def __init__(self, a: InputColor=(1.0, 1.0, 1.0, 1.0), depth_a: InputFloat=1.0, b: InputColor=(1.0, 1.0, 1.0, 1.0), depth_b: InputFloat=1.0, use_alpha: InputBoolean=False, anti_alias: InputBoolean=True):
        super().__init__()
        key_args = {'A': a, 'Depth A': depth_a, 'B': b, 'Depth B': depth_b, 'Use Alpha': use_alpha, 'Anti-Alias': anti_alias}
        self._establish_links(**key_args)

class Exposure(BaseNode):
    _bl_idname = 'CompositorNodeExposure'

    def __init__(self, image: InputColor=None, exposure: InputFloat=0.0):
        super().__init__()
        key_args = {'Image': image, 'Exposure': exposure}
        self._establish_links(**key_args)

class HueCorrect(BaseNode):
    _bl_idname = 'CompositorNodeHueCorrect'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac}
        self._establish_links(**key_args)

class HueSaturationValue(BaseNode):
    _bl_idname = 'CompositorNodeHueSat'

    def __init__(self, image: InputColor=None, hue: InputFloat=0.5, saturation: InputFloat=1.0, value: InputFloat=1.0, fac: InputFloat=1.0):
        super().__init__()
        key_args = {'Image': image, 'Hue': hue, 'Saturation': saturation, 'Value': value, 'Fac': fac}
        self._establish_links(**key_args)

class InvertColor(BaseNode):
    _bl_idname = 'CompositorNodeInvert'

    def __init__(self, color: InputColor=None, fac: InputFloat=1.0, invert_color: InputBoolean=True, invert_alpha: InputBoolean=False):
        super().__init__()
        key_args = {'Color': color, 'Fac': fac, 'Invert Color': invert_color, 'Invert Alpha': invert_alpha}
        self._establish_links(**key_args)

class Posterize(BaseNode):
    _bl_idname = 'CompositorNodePosterize'

    def __init__(self, image: InputColor=None, steps: InputFloat=8.0):
        super().__init__()
        key_args = {'Image': image, 'Steps': steps}
        self._establish_links(**key_args)

class RGBCurves(BaseNode):
    _bl_idname = 'CompositorNodeCurveRGB'

    def __init__(self, image: InputColor=(1.0, 1.0, 1.0, 1.0), fac: InputFloat=1.0, black_level: InputColor=(0.0, 0.0, 0.0, 1.0), white_level: InputColor=(1.0, 1.0, 1.0, 1.0)):
        super().__init__()
        key_args = {'Image': image, 'Fac': fac, 'Black Level': black_level, 'White Level': white_level}
        self._establish_links(**key_args)

class Tonemap(BaseNode):
    _bl_idname = 'CompositorNodeTonemap'

    def __init__(self, image: InputColor=None, type: InputMenu | Literal['R/D Photoreceptor', 'Rh Simple']='R/D Photoreceptor', key: InputFloat=0.18, balance: InputFloat=1.0, gamma: InputFloat=1.0, intensity: InputFloat=0.0, contrast: InputFloat=0.0, light_adaptation: InputFloat=0.0, chromatic_adaptation: InputFloat=0.0):
        super().__init__()
        key_args = {'Image': image, 'Type': type, 'Key': key, 'Balance': balance, 'Gamma': gamma, 'Intensity': intensity, 'Contrast': contrast, 'Light Adaptation': light_adaptation, 'Chromatic Adaptation': chromatic_adaptation}
        self._establish_links(**key_args)

    @classmethod
    def r_d_photoreceptor(cls, image: InputColor=None, intensity: InputFloat=0.0, contrast: InputFloat=0.0, light_adaptation: InputFloat=0.0, chromatic_adaptation: InputFloat=0.0) -> 'Tonemap':
        return cls(image=image, intensity=intensity, contrast=contrast, light_adaptation=light_adaptation, chromatic_adaptation=chromatic_adaptation, type='R/D Photoreceptor')

    @classmethod
    def rh_simple(cls, image: InputColor=None, key: InputFloat=0.18, balance: InputFloat=1.0, gamma: InputFloat=1.0) -> 'Tonemap':
        return cls(image=image, key=key, balance=balance, gamma=gamma, type='Rh Simple')
