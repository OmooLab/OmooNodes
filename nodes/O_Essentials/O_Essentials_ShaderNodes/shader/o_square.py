# Node-group asset "O Square" (ShaderNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import ShaderNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomShaderGroup


class OSquare(CustomShaderGroup):
    _name = "O Square"
    _color_tag = "TEXTURE"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        x = tree.inputs.float("X", 0.5, min_value=0.0, max_value=1.0, subtype="FACTOR")
        y = tree.inputs.float("Y", 0.5, min_value=0.0, max_value=1.0, subtype="FACTOR")
        vector = tree.inputs.vector("Vector", (0.0, 0.0), dimensions=2, min_value=-10000.0, max_value=10000.0, hide_value=True)
        fac = tree.outputs.float("Fac")
        gradient = tree.outputs.float("Gradient")

        vector_1 = abs(vector + (-0.5, -0.5, 0.0))
        math_1 = (vector_1.x / x).max(vector_1.y / y)
        math_2 = g.Math.less_than(math_1)
        math_1 / 2.0 >> gradient

        math_2 >> fac

ASSET = OSquare

ASSET_METADATA = {
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
