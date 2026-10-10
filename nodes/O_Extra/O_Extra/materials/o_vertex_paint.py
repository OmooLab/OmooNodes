from bpy.types import ShaderNodeTree
from nodes_tool import shader as s, TreeBuilder
from nodes_tool.builder import CustomShaderGroup


class OVertexPaint(CustomShaderGroup):
    _name = "O Vertex Paint"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        attribute = s.Attribute(attribute_name="o_color")
        principled_bsdf = s.PrincipledBSDF(base_color=attribute.o.color, alpha=attribute.o.alpha, subsurface_scale=0.05)
        _material_output = s.MaterialOutput(surface=principled_bsdf, is_active_output=True)

MATERIAL = OVertexPaint
MATERIAL_NAME = "O Vertex Paint"
