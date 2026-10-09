from bpy.types import ShaderNodeTree
from nodebpy import geometry as g, shader as s, TreeBuilder
from nodebpy.builder import CustomShaderGroup

class OOutline2(CustomShaderGroup):
    _name = 'Shader Nodetree'

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        attribute = s.Attribute(attribute_name='o_primary')
        attribute_1 = s.Attribute(attribute_name='o_light')
        emission = s.Emission(color=attribute.o.color)
        math_1 = g.Math.subtract(1.0, s.LightPath().o.is_shadow_ray, use_clamp=True).o.value * g.Math.subtract(1.0, s.LightPath().o.is_diffuse_ray, use_clamp=True)
        math_2 = math_1 * g.Math.subtract(1.0, s.Geometry().o.backfacing, use_clamp=True) * s.Attribute(attribute_name='o_opacity').o.factor
        math_3 = math_2 * attribute.o.alpha
        mix_shader = s.MixShader(fac=attribute_1.o.factor, shader=emission, shader_001=s.TranslucentBSDF(color=attribute.o.color))
        transparent_bsdf = s.TransparentBSDF()
        _material_output = s.MaterialOutput(surface=s.MixShader(fac=math_3, shader=transparent_bsdf, shader_001=mix_shader), is_active_output=True, target='CYCLES')
        mix_shader_1 = s.MixShader(fac=attribute_1.o.factor, shader=emission, shader_001=s.DiffuseBSDF(color=attribute.o.color, normal=s.Geometry().o.normal * -1.0))
        _material_output_1 = s.MaterialOutput(surface=s.MixShader(fac=math_3, shader=transparent_bsdf, shader_001=mix_shader_1), target='EEVEE')
MATERIAL = OOutline2
MATERIAL_NAME = 'O Outline'
MATERIAL_PROPERTIES = {'surface_render_method': 'BLENDED', 'use_backface_culling': True, 'use_transparency_overlap': False, 'blend_method': 'BLEND'}
