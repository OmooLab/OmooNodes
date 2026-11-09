from bpy.types import ShaderNodeTree
from omoonodes import shader as s, TreeBuilder
from omoonodes.builder import CustomShaderGroup


class ODebugColor(CustomShaderGroup):
    _name = "O Debug Color"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        _material_output = s.MaterialOutput(surface=s.Emission(color=s.ColorAttribute(layer_name="o_color").o.color), is_active_output=True)

MATERIAL = ODebugColor
MATERIAL_NAME = "O Debug Color"

MATERIAL_PROPERTIES = {
    "use_backface_culling": True,
}
