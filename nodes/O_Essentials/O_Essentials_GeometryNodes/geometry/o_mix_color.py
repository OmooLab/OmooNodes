# Node-group asset "O Mix Color" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OMixColor(CustomGeometryGroup):
    _name = "O Mix Color"
    _color_tag = "COLOR"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        factor = tree.inputs.float("Factor", 0.5, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
        a = tree.inputs.color("A", (0.5, 0.5, 0.5, 1.0))
        b = tree.inputs.color("B", (0.5, 0.5, 0.5, 1.0))
        color = tree.outputs.color("Color", (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0))

        result = g.Mix.color(factor, a, b, clamp_factor=True).o.result_color
        combine_color = g.CombineColor(red=result.r, green=result.g, blue=result.b, alpha=g.SeparateColor(color=a).o.alpha)
        combine_color >> color

ASSET = OMixColor

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
