# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket, FloatSocket, ShaderSocket, StringSocket, VectorSocket
from ...socket_types import InputColor, InputFloat, InputString, InputVector

class PrincipledVolume(BaseNode):
    _bl_idname = 'ShaderNodeVolumePrincipled'

    def __init__(self, color: InputColor=(0.5, 0.5, 0.5, 1.0), color_attribute: InputString='', density: InputFloat=1.0, density_attribute: InputString='density', anisotropy: InputFloat=0.0, absorption_color: InputColor=(0.0, 0.0, 0.0, 1.0), emission_strength: InputFloat=0.0, emission_color: InputColor=(1.0, 1.0, 1.0, 1.0), blackbody_intensity: InputFloat=0.0, blackbody_tint: InputColor=(1.0, 1.0, 1.0, 1.0), temperature: InputFloat=1000.0, temperature_attribute: InputString='temperature', weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Color Attribute': color_attribute, 'Density': density, 'Density Attribute': density_attribute, 'Anisotropy': anisotropy, 'Absorption Color': absorption_color, 'Emission Strength': emission_strength, 'Emission Color': emission_color, 'Blackbody Intensity': blackbody_intensity, 'Blackbody Tint': blackbody_tint, 'Temperature': temperature, 'Temperature Attribute': temperature_attribute, 'Weight': weight}
        self._establish_links(**key_args)

class VolumeAbsorption(BaseNode):
    _bl_idname = 'ShaderNodeVolumeAbsorption'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), density: InputFloat=1.0, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Density': density, 'Weight': weight}
        self._establish_links(**key_args)

class VolumeCoefficients(BaseNode):
    _bl_idname = 'ShaderNodeVolumeCoefficients'

    def __init__(self, weight: InputFloat=0.0, absorption_coefficients: InputVector=(1.0, 1.0, 1.0), scatter_coefficients: InputVector=(1.0, 1.0, 1.0), anisotropy: InputFloat=0.0, ior: InputFloat=1.33, backscatter: InputFloat=0.1, alpha: InputFloat=0.5, diameter: InputFloat=20.0, emission_coefficients: InputVector=(0.0, 0.0, 0.0), *, phase: Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']='HENYEY_GREENSTEIN'):
        super().__init__()
        key_args = {'Weight': weight, 'Absorption Coefficients': absorption_coefficients, 'Scatter Coefficients': scatter_coefficients, 'Anisotropy': anisotropy, 'IOR': ior, 'Backscatter': backscatter, 'Alpha': alpha, 'Diameter': diameter, 'Emission Coefficients': emission_coefficients}
        self.phase = phase
        self._establish_links(**key_args)

    @property
    def phase(self) -> Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']:
        return self.node.phase

    @phase.setter
    def phase(self, value: Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']) -> None:
        set_property(self.node, 'phase', value)

class VolumeInfo(BaseNode):
    _bl_idname = 'ShaderNodeVolumeInfo'

    def __init__(self) -> None:
        super().__init__()
        key_args = {}
        self._establish_links(**key_args)

class VolumeScatter(BaseNode):
    _bl_idname = 'ShaderNodeVolumeScatter'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), density: InputFloat=1.0, anisotropy: InputFloat=0.0, ior: InputFloat=1.33, backscatter: InputFloat=0.1, alpha: InputFloat=0.5, diameter: InputFloat=20.0, weight: InputFloat=0.0, *, phase: Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']='HENYEY_GREENSTEIN'):
        super().__init__()
        key_args = {'Color': color, 'Density': density, 'Anisotropy': anisotropy, 'IOR': ior, 'Backscatter': backscatter, 'Alpha': alpha, 'Diameter': diameter, 'Weight': weight}
        self.phase = phase
        self._establish_links(**key_args)

    @property
    def phase(self) -> Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']:
        return self.node.phase

    @phase.setter
    def phase(self, value: Literal['HENYEY_GREENSTEIN', 'FOURNIER_FORAND', 'DRAINE', 'RAYLEIGH', 'MIE']) -> None:
        set_property(self.node, 'phase', value)
