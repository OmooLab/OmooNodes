from bpy.types import ShaderNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomShaderGroup


class OCircle(CustomShaderGroup):
    _name = "O Circle"
    _color_tag = "TEXTURE"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        radius = tree.inputs.float("Radius", 0.5, min_value=0.0, max_value=1.0, subtype="FACTOR")
        vector = tree.inputs.vector("Vector", (0.0, 0.0), dimensions=2, min_value=-10000.0, max_value=10000.0, hide_value=True)
        fac = tree.outputs.float("Fac")
        gradient = tree.outputs.float("Gradient")

        vector_math = (vector + (-0.5, -0.5, 0.0)).length()
        math_1 = g.Math.less_than(vector_math, radius * 0.5)

        math_1 >> fac
        vector_math >> gradient

ASSET = OCircle

ASSET_METADATA = {
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
