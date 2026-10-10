# Material "O Debug Color", dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
# The class is a recipe for the material's shader tree — build recreates the material and runs it into material.node_tree.
from bpy.types import ShaderNodeTree
from nodebpy import shader as s, TreeBuilder
from nodebpy.builder import CustomShaderGroup


class ODebugColor(CustomShaderGroup):
    _name = "Shader Nodetree"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        _material_output = s.MaterialOutput(surface=s.Emission(color=s.ColorAttribute(layer_name="o_color").o.color), is_active_output=True)

MATERIAL = ODebugColor
MATERIAL_NAME = "O Debug Color"

MATERIAL_PROPERTIES = {
    "use_backface_culling": True,
}
