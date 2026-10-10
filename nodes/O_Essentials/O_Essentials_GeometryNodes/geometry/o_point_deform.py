# Node-group asset "O Point Deform" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OPointDeform(CustomGeometryGroup):
    _name = "O Point Deform"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        source = tree.inputs.geometry("Source")
        rest_positon = tree.inputs.vector("Rest Positon", (0.0, 0.0, 0.0), hide_value=True, default_input="POSITION")
        with tree.inputs.panel("Options", default_closed=True):
            weight = tree.inputs.float("Weight", 1.0, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
            smooth_iterations = tree.inputs.integer("Smooth Iterations", 10, description="How many times to blur the values for all elements", min_value=0)
            smooth_weight = tree.inputs.float("Smooth Weight", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
        geometry_1 = tree.outputs.geometry("Geometry")

        sample_nearest = g.SampleNearest.point(source)
        vector_math = g.SampleIndex.point.vector(source, g.Position(), sample_nearest).o.value - g.SampleIndex.point.vector(source, rest_positon, sample_nearest)
        (
            geometry
            >> g.SetPosition(selection=selection, offset=weight.mix.vector((0.0, 0.0, 0.0), vector_math.blur(smooth_iterations, smooth_weight)))
            >> geometry_1
        )

ASSET = OPointDeform

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
