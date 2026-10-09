from bpy.types import ShaderNodeTree
from nodebpy import geometry as g, shader as s, TreeBuilder
from nodebpy.builder import CustomShaderGroup

class OOutlineExtra(CustomShaderGroup):
    _name = 'Shader Nodetree'

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        attribute = s.Attribute(attribute_name='o_primary')
        attribute_1 = s.Attribute(attribute_name='o_light')
        attribute_2 = s.Attribute(attribute_name='o_secondary')
        math_1 = g.Math.subtract(1.0, s.LightPath().o.is_shadow_ray, use_clamp=True).o.value * g.Math.subtract(1.0, s.LightPath().o.is_diffuse_ray, use_clamp=True)
        math_2 = math_1 * g.Math.subtract(1.0, s.Geometry().o.backfacing, use_clamp=True) * s.Attribute(attribute_name='o_opacity').o.factor
        transparent_bsdf = s.TransparentBSDF()
        vector_math = s.Geometry().o.normal * -1.0
        math_3 = g.Math.greater_than(s.ShaderToRGB(shader=s.DiffuseBSDF(normal=vector_math)).o.color, s.Attribute(attribute_name='o_threshold').o.factor, use_clamp=True)
        math_4 = math_2 * g.Mix.float(math_3, attribute_2.o.alpha, attribute.o.alpha, clamp_factor=True).o.result_float
        mix = g.Mix.color(math_3, attribute_2.o.color, attribute.o.color, clamp_factor=True)
        mix_shader = s.MixShader(fac=attribute_1.o.factor, shader=s.Emission(color=mix.o.result_color), shader_001=s.DiffuseBSDF(color=mix.o.result_color, normal=vector_math))
        _material_output = s.MaterialOutput(surface=s.MixShader(fac=math_4, shader=transparent_bsdf, shader_001=mix_shader), is_active_output=True, target='EEVEE')
        mix_shader_1 = s.MixShader(fac=attribute_1.o.factor, shader=s.Emission(color=mix.o.result_color), shader_001=s.TranslucentBSDF(color=attribute.o.color))
        mix_shader_2 = s.MixShader(fac=math_2 * attribute.o.alpha, shader=transparent_bsdf, shader_001=mix_shader_1)
        _material_output_1 = s.MaterialOutput(surface=mix_shader_2, target='CYCLES')
MATERIAL = OOutlineExtra
MATERIAL_NAME = 'O Outline Extra'
MATERIAL_PROPERTIES = {'surface_render_method': 'BLENDED', 'use_backface_culling': True, 'use_transparency_overlap': False, 'blend_method': 'BLEND'}
