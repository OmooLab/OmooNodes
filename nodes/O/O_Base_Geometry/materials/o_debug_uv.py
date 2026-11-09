from bpy.types import ShaderNodeTree
from omoonodes import geometry as g, shader as s, TreeBuilder
from omoonodes.builder import CustomShaderGroup


class ODebugUV(CustomShaderGroup):
    _name = "O Debug UV"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        color_attribute = s.ColorAttribute(layer_name="o_uvisland")
        image_texture = s.ImageTexture()
        mix = g.Mix.color(a=image_texture.o.color, b=color_attribute.o.color, blend_type="ADD", clamp_factor=True)
        mix_1 = g.Mix.color(a=image_texture.o.color, b=color_attribute.o.color, blend_type="COLOR", clamp_factor=True)
        mix_2 = g.Mix.color(s.Attribute(attribute_name="o_show_uvisland").o.factor, image_texture.o.color, g.Mix.color(0.5, mix.o.result_color, mix_1.o.result_color, clamp_factor=True).o.result_color, clamp_factor=True)
        _material_output = s.MaterialOutput(surface=s.Emission(color=mix_2.o.result_color), is_active_output=True)

MATERIAL = ODebugUV
MATERIAL_NAME = "O Debug UV"

MATERIAL_PROPERTIES = {
    "use_backface_culling": True,
}
