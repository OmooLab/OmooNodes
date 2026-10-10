from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OBlend(CustomGeometryGroup):
    _name = "O Blend"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        source = tree.inputs.geometry("Source")
        factor = tree.inputs.float("Factor", 0.5, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
        geometry_1 = tree.outputs.geometry("Geometry")

        mix = g.Mix.vector(factor, g.Position(), g.SampleIndex.point.vector(source, g.Position(), g.Index()), clamp_factor=True)
        (
            geometry
            >> g.SetPosition(selection=selection, position=mix.o.result_vector)
            >> geometry_1
        )

ASSET = OBlend

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
