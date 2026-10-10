# Node-group asset "O Relight" (CompositorNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import CompositorNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomCompositorGroup


class ORelight(CustomCompositorGroup):
    _name = "O Relight"
    _color_tag = "FILTER"
    _tree_properties = {"is_strip_modifier": True}

    def _build_group(self, tree: TreeBuilder[CompositorNodeTree]) -> None:
        image = tree.inputs.color("Image", (0.0, 0.0, 0.0, 1.0), description="Value of the first color input", hide_value=True)
        normal = tree.inputs.vector("Normal", (0.0, 0.0, 0.0), min_value=-10000.0, max_value=10000.0)
        mask = tree.inputs.float("Mask", 1.0, min_value=0.0, max_value=1.0, hide_value=True, subtype="FACTOR")
        direction = tree.inputs.vector("Direction", (1.0, 0.0, 0.0), min_value=-10000.0, max_value=10000.0, subtype="DIRECTION")
        color = tree.inputs.color("Color", (1.0, 1.0, 1.0, 1.0))
        image_1 = tree.outputs.color("Image", (0.0, 0.0, 0.0, 1.0))
        light = tree.outputs.color("Light", (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0))

        vector_math = g.VectorMath.scale(color, normal.dot(direction).max(0.0) * mask)
        mix = g.Mix.color(a=image, b=vector_math.o.vector, blend_type="ADD")

        mix.o.result_color >> image_1
        vector_math >> light

ASSET = ORelight

ASSET_METADATA = {
    "catalog_id": "2cd36519-46ee-428e-a751-5c3d0312efb2",
}
