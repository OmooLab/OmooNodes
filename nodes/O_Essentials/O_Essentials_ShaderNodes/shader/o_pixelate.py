from bpy.types import ShaderNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomShaderGroup


class OPixelate(CustomShaderGroup):
    _name = "O Pixelate"
    _color_tag = "VECTOR"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        x = tree.inputs.integer("X", 256, min_value=1, max_value=8192)
        y = tree.inputs.integer("Y", 256, min_value=1, max_value=8192)
        vector = tree.inputs.vector("Vector", (0.0, 0.0), dimensions=2, min_value=0.0, max_value=1.0, hide_value=True)
        vector_1 = tree.outputs.vector("Vector", min_value=0.0, max_value=0.0)

        math_1 = vector.x * (x - g.Math.truncated_modulo(x, 1.0))
        math_2 = vector.y * (y - g.Math.truncated_modulo(y, 1.0))
        combine_xyz = g.CombineXYZ(x=(math_1 - g.Math.truncated_modulo(math_1, 1.0)) / (x - g.Math.truncated_modulo(x, 1.0)), y=(math_2 - g.Math.truncated_modulo(math_2, 1.0)) / (y - g.Math.truncated_modulo(y, 1.0)))

        combine_xyz >> vector_1

ASSET = OPixelate

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
