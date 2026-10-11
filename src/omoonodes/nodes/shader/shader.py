# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, ShaderSocket, VectorSocket
from ...socket_types import InputBoolean, InputColor, InputFloat, InputShader, InputVector

class AddShader(BaseNode):
    _bl_idname = 'ShaderNodeAddShader'

    def __init__(self, shader: InputShader=None, shader_001: InputShader=None):
        super().__init__()
        key_args = {'Shader': shader, 'Shader_001': shader_001}
        self._establish_links(**key_args)

class Background(BaseNode):
    _bl_idname = 'ShaderNodeBackground'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), strength: InputFloat=1.0, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Strength': strength, 'Weight': weight}
        self._establish_links(**key_args)

class DiffuseBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfDiffuse'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), roughness: InputFloat=0.0, normal: InputVector=None, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Roughness': roughness, 'Normal': normal, 'Weight': weight}
        self._establish_links(**key_args)

class Emission(BaseNode):
    _bl_idname = 'ShaderNodeEmission'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), strength: InputFloat=1.0, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Strength': strength, 'Weight': weight}
        self._establish_links(**key_args)

class GlassBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfGlass'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), roughness: InputFloat=0.0, ior: InputFloat=1.5, normal: InputVector=None, weight: InputFloat=0.0, thin_film_thickness: InputFloat=0.0, thin_film_ior: InputFloat=1.33, *, distribution: Literal['BECKMANN', 'GGX', 'MULTI_GGX']='MULTI_GGX'):
        super().__init__()
        key_args = {'Color': color, 'Roughness': roughness, 'IOR': ior, 'Normal': normal, 'Weight': weight, 'Thin Film Thickness': thin_film_thickness, 'Thin Film IOR': thin_film_ior}
        self.distribution = distribution
        self._establish_links(**key_args)

    @property
    def distribution(self) -> Literal['BECKMANN', 'GGX', 'MULTI_GGX']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['BECKMANN', 'GGX', 'MULTI_GGX']) -> None:
        set_property(self.node, 'distribution', value)

class GlossyBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfAnisotropic'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), roughness: InputFloat=0.5, anisotropy: InputFloat=0.0, rotation: InputFloat=0.0, normal: InputVector=None, tangent: InputVector=None, weight: InputFloat=0.0, *, distribution: Literal['BECKMANN', 'GGX', 'ASHIKHMIN_SHIRLEY', 'MULTI_GGX']='MULTI_GGX'):
        super().__init__()
        key_args = {'Color': color, 'Roughness': roughness, 'Anisotropy': anisotropy, 'Rotation': rotation, 'Normal': normal, 'Tangent': tangent, 'Weight': weight}
        self.distribution = distribution
        self._establish_links(**key_args)

    @property
    def distribution(self) -> Literal['BECKMANN', 'GGX', 'ASHIKHMIN_SHIRLEY', 'MULTI_GGX']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['BECKMANN', 'GGX', 'ASHIKHMIN_SHIRLEY', 'MULTI_GGX']) -> None:
        set_property(self.node, 'distribution', value)

class HairBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfHair'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), offset: InputFloat=0.0, roughnessu: InputFloat=0.1, roughnessv: InputFloat=1.0, tangent: InputVector=None, weight: InputFloat=0.0, *, component: Literal['Reflection', 'Transmission']='Reflection'):
        super().__init__()
        key_args = {'Color': color, 'Offset': offset, 'RoughnessU': roughnessu, 'RoughnessV': roughnessv, 'Tangent': tangent, 'Weight': weight}
        self.component = component
        self._establish_links(**key_args)

    @property
    def component(self) -> Literal['Reflection', 'Transmission']:
        return self.node.component

    @component.setter
    def component(self, value: Literal['Reflection', 'Transmission']) -> None:
        set_property(self.node, 'component', value)

class Holdout(BaseNode):
    _bl_idname = 'ShaderNodeHoldout'

    def __init__(self, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Weight': weight}
        self._establish_links(**key_args)

class MetallicBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfMetallic'

    def __init__(self, base_color: InputColor=(0.617, 0.577, 0.54, 1.0), edge_tint: InputColor=(0.695, 0.726, 0.77, 1.0), ior: InputVector=(2.757, 2.513, 2.231), extinction: InputVector=(3.867, 3.404, 3.009), roughness: InputFloat=0.5, anisotropy: InputFloat=0.0, rotation: InputFloat=0.0, normal: InputVector=None, tangent: InputVector=None, weight: InputFloat=0.0, thin_film_thickness: InputFloat=0.0, thin_film_ior: InputFloat=1.33, *, distribution: Literal['BECKMANN', 'GGX', 'MULTI_GGX']='MULTI_GGX', fresnel_type: Literal['PHYSICAL_CONDUCTOR', 'F82']='F82'):
        super().__init__()
        key_args = {'Base Color': base_color, 'Edge Tint': edge_tint, 'IOR': ior, 'Extinction': extinction, 'Roughness': roughness, 'Anisotropy': anisotropy, 'Rotation': rotation, 'Normal': normal, 'Tangent': tangent, 'Weight': weight, 'Thin Film Thickness': thin_film_thickness, 'Thin Film IOR': thin_film_ior}
        self.distribution = distribution
        self.fresnel_type = fresnel_type
        self._establish_links(**key_args)

    @classmethod
    def physical_conductor(cls, ior: InputVector=(2.757, 2.513, 2.231), extinction: InputVector=(3.867, 3.404, 3.009), roughness: InputFloat=0.5, anisotropy: InputFloat=0.0, rotation: InputFloat=0.0, normal: InputVector=None, tangent: InputVector=None, thin_film_thickness: InputFloat=0.0, thin_film_ior: InputFloat=1.33, *, distribution: Literal['BECKMANN', 'GGX', 'MULTI_GGX']='MULTI_GGX') -> 'MetallicBSDF':
        return cls(fresnel_type='PHYSICAL_CONDUCTOR', ior=ior, extinction=extinction, roughness=roughness, anisotropy=anisotropy, rotation=rotation, normal=normal, tangent=tangent, thin_film_thickness=thin_film_thickness, thin_film_ior=thin_film_ior, distribution=distribution)

    @classmethod
    def f82_tint(cls, base_color: InputColor=(0.617, 0.577, 0.54, 1.0), edge_tint: InputColor=(0.695, 0.726, 0.77, 1.0), roughness: InputFloat=0.5, anisotropy: InputFloat=0.0, rotation: InputFloat=0.0, normal: InputVector=None, tangent: InputVector=None, thin_film_thickness: InputFloat=0.0, thin_film_ior: InputFloat=1.33, *, distribution: Literal['BECKMANN', 'GGX', 'MULTI_GGX']='MULTI_GGX') -> 'MetallicBSDF':
        return cls(fresnel_type='F82', base_color=base_color, edge_tint=edge_tint, roughness=roughness, anisotropy=anisotropy, rotation=rotation, normal=normal, tangent=tangent, thin_film_thickness=thin_film_thickness, thin_film_ior=thin_film_ior, distribution=distribution)

    @property
    def distribution(self) -> Literal['BECKMANN', 'GGX', 'MULTI_GGX']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['BECKMANN', 'GGX', 'MULTI_GGX']) -> None:
        set_property(self.node, 'distribution', value)

    @property
    def fresnel_type(self) -> Literal['PHYSICAL_CONDUCTOR', 'F82']:
        return self.node.fresnel_type

    @fresnel_type.setter
    def fresnel_type(self, value: Literal['PHYSICAL_CONDUCTOR', 'F82']) -> None:
        set_property(self.node, 'fresnel_type', value)

class MixShader(BaseNode):
    _bl_idname = 'ShaderNodeMixShader'

    def __init__(self, fac: InputFloat=0.5, shader: InputShader=None, shader_001: InputShader=None):
        super().__init__()
        key_args = {'Fac': fac, 'Shader': shader, 'Shader_001': shader_001}
        self._establish_links(**key_args)

class PrincipledBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfPrincipled'

    def __init__(self, base_color: InputColor=(0.8, 0.8, 0.8, 1.0), metallic: InputFloat=0.0, roughness: InputFloat=0.5, ior: InputFloat=1.5, alpha: InputFloat=1.0, thin_wall: InputBoolean=False, normal: InputVector=None, weight: InputFloat=0.0, diffuse_roughness: InputFloat=0.0, subsurface_weight: InputFloat=0.0, subsurface_radius: InputVector=(1.0, 0.2, 0.1), subsurface_scale: InputFloat=0.005, subsurface_ior: InputFloat=1.4, subsurface_anisotropy: InputFloat=0.0, specular_ior_level: InputFloat=0.5, specular_tint: InputColor=(1.0, 1.0, 1.0, 1.0), anisotropic: InputFloat=0.0, anisotropic_rotation: InputFloat=0.0, tangent: InputVector=None, transmission_weight: InputFloat=0.0, coat_weight: InputFloat=0.0, coat_roughness: InputFloat=0.03, coat_ior: InputFloat=1.5, coat_tint: InputColor=(1.0, 1.0, 1.0, 1.0), coat_normal: InputVector=None, sheen_weight: InputFloat=0.0, sheen_roughness: InputFloat=0.5, sheen_tint: InputColor=(1.0, 1.0, 1.0, 1.0), emission_color: InputColor=(1.0, 1.0, 1.0, 1.0), emission_strength: InputFloat=0.0, thin_film_thickness: InputFloat=0.0, thin_film_ior: InputFloat=1.33, *, distribution: Literal['GGX', 'MULTI_GGX']='MULTI_GGX', subsurface_method: Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']='RANDOM_WALK'):
        super().__init__()
        key_args = {'Base Color': base_color, 'Metallic': metallic, 'Roughness': roughness, 'IOR': ior, 'Alpha': alpha, 'Thin Wall': thin_wall, 'Normal': normal, 'Weight': weight, 'Diffuse Roughness': diffuse_roughness, 'Subsurface Weight': subsurface_weight, 'Subsurface Radius': subsurface_radius, 'Subsurface Scale': subsurface_scale, 'Subsurface IOR': subsurface_ior, 'Subsurface Anisotropy': subsurface_anisotropy, 'Specular IOR Level': specular_ior_level, 'Specular Tint': specular_tint, 'Anisotropic': anisotropic, 'Anisotropic Rotation': anisotropic_rotation, 'Tangent': tangent, 'Transmission Weight': transmission_weight, 'Coat Weight': coat_weight, 'Coat Roughness': coat_roughness, 'Coat IOR': coat_ior, 'Coat Tint': coat_tint, 'Coat Normal': coat_normal, 'Sheen Weight': sheen_weight, 'Sheen Roughness': sheen_roughness, 'Sheen Tint': sheen_tint, 'Emission Color': emission_color, 'Emission Strength': emission_strength, 'Thin Film Thickness': thin_film_thickness, 'Thin Film IOR': thin_film_ior}
        self.distribution = distribution
        self.subsurface_method = subsurface_method
        self._establish_links(**key_args)

    @property
    def distribution(self) -> Literal['GGX', 'MULTI_GGX']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['GGX', 'MULTI_GGX']) -> None:
        set_property(self.node, 'distribution', value)

    @property
    def subsurface_method(self) -> Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']:
        return self.node.subsurface_method

    @subsurface_method.setter
    def subsurface_method(self, value: Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']) -> None:
        set_property(self.node, 'subsurface_method', value)

class PrincipledHairBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfHairPrincipled'

    def __init__(self, color: InputColor=(0.017513, 0.005763, 0.002059, 1.0), melanin: InputFloat=0.8, melanin_redness: InputFloat=1.0, tint: InputColor=(1.0, 1.0, 1.0, 1.0), absorption_coefficient: InputVector=(0.245531, 0.52, 1.365), aspect_ratio: InputFloat=0.85, roughness: InputFloat=0.3, radial_roughness: InputFloat=0.3, coat: InputFloat=0.0, ior: InputFloat=1.55, offset: InputFloat=0.034906585, random_color: InputFloat=0.0, random_roughness: InputFloat=0.0, random: InputFloat=None, weight: InputFloat=0.0, r_lobe: InputFloat=1.0, tt_lobe: InputFloat=1.0, trt_lobe: InputFloat=1.0, *, model: Literal['CHIANG', 'HUANG']='CHIANG', parametrization: Literal['ABSORPTION', 'MELANIN', 'COLOR']='COLOR'):
        super().__init__()
        key_args = {'Color': color, 'Melanin': melanin, 'Melanin Redness': melanin_redness, 'Tint': tint, 'Absorption Coefficient': absorption_coefficient, 'Aspect Ratio': aspect_ratio, 'Roughness': roughness, 'Radial Roughness': radial_roughness, 'Coat': coat, 'IOR': ior, 'Offset': offset, 'Random Color': random_color, 'Random Roughness': random_roughness, 'Random': random, 'Weight': weight, 'R lobe': r_lobe, 'TT lobe': tt_lobe, 'TRT lobe': trt_lobe}
        self.model = model
        self.parametrization = parametrization
        self._establish_links(**key_args)

    @property
    def model(self) -> Literal['CHIANG', 'HUANG']:
        return self.node.model

    @model.setter
    def model(self, value: Literal['CHIANG', 'HUANG']) -> None:
        set_property(self.node, 'model', value)

    @property
    def parametrization(self) -> Literal['ABSORPTION', 'MELANIN', 'COLOR']:
        return self.node.parametrization

    @parametrization.setter
    def parametrization(self, value: Literal['ABSORPTION', 'MELANIN', 'COLOR']) -> None:
        set_property(self.node, 'parametrization', value)

class RayPortalBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfRayPortal'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), position: InputVector=None, direction: InputVector=None, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Position': position, 'Direction': direction, 'Weight': weight}
        self._establish_links(**key_args)

class RefractionBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfRefraction'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), roughness: InputFloat=0.0, ior: InputFloat=1.45, normal: InputVector=None, weight: InputFloat=0.0, *, distribution: Literal['BECKMANN', 'GGX']='BECKMANN'):
        super().__init__()
        key_args = {'Color': color, 'Roughness': roughness, 'IOR': ior, 'Normal': normal, 'Weight': weight}
        self.distribution = distribution
        self._establish_links(**key_args)

    @property
    def distribution(self) -> Literal['BECKMANN', 'GGX']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['BECKMANN', 'GGX']) -> None:
        set_property(self.node, 'distribution', value)

class SheenBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfSheen'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), roughness: InputFloat=0.5, normal: InputVector=None, weight: InputFloat=0.0, *, distribution: Literal['ASHIKHMIN', 'MICROFIBER']='MICROFIBER'):
        super().__init__()
        key_args = {'Color': color, 'Roughness': roughness, 'Normal': normal, 'Weight': weight}
        self.distribution = distribution
        self._establish_links(**key_args)

    @property
    def distribution(self) -> Literal['ASHIKHMIN', 'MICROFIBER']:
        return self.node.distribution

    @distribution.setter
    def distribution(self, value: Literal['ASHIKHMIN', 'MICROFIBER']) -> None:
        set_property(self.node, 'distribution', value)

class SpecularBSDF(BaseNode):
    _bl_idname = 'ShaderNodeEeveeSpecular'

    def __init__(self, base_color: InputColor=(0.8, 0.8, 0.8, 1.0), specular: InputColor=(0.03, 0.03, 0.03, 1.0), roughness: InputFloat=0.2, emissive_color: InputColor=(0.0, 0.0, 0.0, 1.0), transparency: InputFloat=0.0, normal: InputVector=None, clear_coat: InputFloat=0.0, clear_coat_roughness: InputFloat=0.0, clear_coat_normal: InputVector=None, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Base Color': base_color, 'Specular': specular, 'Roughness': roughness, 'Emissive Color': emissive_color, 'Transparency': transparency, 'Normal': normal, 'Clear Coat': clear_coat, 'Clear Coat Roughness': clear_coat_roughness, 'Clear Coat Normal': clear_coat_normal, 'Weight': weight}
        self._establish_links(**key_args)

class SubsurfaceScattering(BaseNode):
    _bl_idname = 'ShaderNodeSubsurfaceScattering'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), scale: InputFloat=0.005, radius: InputVector=(1.0, 0.2, 0.1), ior: InputFloat=1.4, roughness: InputFloat=1.0, anisotropy: InputFloat=0.0, normal: InputVector=None, weight: InputFloat=0.0, *, falloff: Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']='RANDOM_WALK'):
        super().__init__()
        key_args = {'Color': color, 'Scale': scale, 'Radius': radius, 'IOR': ior, 'Roughness': roughness, 'Anisotropy': anisotropy, 'Normal': normal, 'Weight': weight}
        self.falloff = falloff
        self._establish_links(**key_args)

    @property
    def falloff(self) -> Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']:
        return self.node.falloff

    @falloff.setter
    def falloff(self, value: Literal['BURLEY', 'RANDOM_WALK', 'RANDOM_WALK_SKIN', 'RANDOM_WALK_LEGACY']) -> None:
        set_property(self.node, 'falloff', value)

class ToonBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfToon'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), size: InputFloat=0.5, smooth: InputFloat=0.0, normal: InputVector=None, weight: InputFloat=0.0, *, component: Literal['DIFFUSE', 'GLOSSY']='DIFFUSE'):
        super().__init__()
        key_args = {'Color': color, 'Size': size, 'Smooth': smooth, 'Normal': normal, 'Weight': weight}
        self.component = component
        self._establish_links(**key_args)

    @property
    def component(self) -> Literal['DIFFUSE', 'GLOSSY']:
        return self.node.component

    @component.setter
    def component(self, value: Literal['DIFFUSE', 'GLOSSY']) -> None:
        set_property(self.node, 'component', value)

class TranslucentBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfTranslucent'

    def __init__(self, color: InputColor=(0.8, 0.8, 0.8, 1.0), normal: InputVector=None, weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Normal': normal, 'Weight': weight}
        self._establish_links(**key_args)

class TransparentBSDF(BaseNode):
    _bl_idname = 'ShaderNodeBsdfTransparent'

    def __init__(self, color: InputColor=(1.0, 1.0, 1.0, 1.0), weight: InputFloat=0.0):
        super().__init__()
        key_args = {'Color': color, 'Weight': weight}
        self._establish_links(**key_args)
