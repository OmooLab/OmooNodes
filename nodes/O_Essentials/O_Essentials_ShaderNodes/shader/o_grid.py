# Node-group asset "O Grid" (ShaderNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import ShaderNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomShaderGroup


class OGrid(CustomShaderGroup):
    _name = "O Grid"
    _color_tag = "VECTOR"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        x = tree.inputs.integer("X", 10, min_value=1, max_value=8192)
        y = tree.inputs.integer("Y", 10, min_value=1, max_value=8192)
        vector = tree.inputs.vector("Vector", (0.0, 0.0), dimensions=2, hide_value=True)
        vector_1 = tree.outputs.vector("Vector", (0.0, 0.0), dimensions=2)

        combine_xyz = g.CombineXYZ(x=g.Math.truncated_modulo((x - g.Math.truncated_modulo(x, 1.0)) * vector.x, 1.0), y=g.Math.truncated_modulo(vector.y * (y - g.Math.truncated_modulo(y, 1.0)), 1.0))

        combine_xyz >> vector_1

ASSET = OGrid

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
