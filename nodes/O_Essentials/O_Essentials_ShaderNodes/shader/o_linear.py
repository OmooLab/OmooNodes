# Node-group asset "O Linear" (ShaderNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import ShaderNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomShaderGroup


class OLinear(CustomShaderGroup):
    _name = "O Linear"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        angle = tree.inputs.float("Angle", 0.0, description="Angle to rotate the input vector by", subtype="ANGLE")
        vector = tree.inputs.vector("Vector", (0.0, 0.0, 0.0), min_value=0.0, max_value=1.0, hide_value=True)
        fac = tree.outputs.float("Fac")
        gradient = tree.outputs.float("Gradient")

        vector_1 = g.VectorRotate(vector=vector, angle=angle, center=(0.5, 0.5, 0.5)).o.vector
        math_1 = g.Math.less_than(vector_1.x, g.Math.multiply(1.0))

        math_1 >> fac
        vector_1.x >> gradient

ASSET = OLinear

ASSET_METADATA = {
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
