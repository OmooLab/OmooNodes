from bpy.types import ShaderNodeTree
from nodebpy import shader as s, TreeBuilder
from nodebpy.builder import CustomShaderGroup

class OVertexPaint(CustomShaderGroup):
    _name = 'Shader Nodetree'

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        attribute = s.Attribute(attribute_name='o_color')
        principled_bsdf = s.PrincipledBSDF(base_color=attribute.o.color, alpha=attribute.o.alpha, subsurface_scale=0.05000000074505806, subsurface_method='RANDOM_WALK_LEGACY')
        _material_output = s.MaterialOutput(surface=principled_bsdf, is_active_output=True)
MATERIAL = OVertexPaint
MATERIAL_NAME = 'O Vertex Paint'
