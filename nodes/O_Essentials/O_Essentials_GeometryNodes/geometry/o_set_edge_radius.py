from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OSetEdgeRadius(CustomGeometryGroup):
    _name = "O Set Edge Radius"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        radius = tree.inputs.float("Radius", 0.1, min_value=0.0, subtype="DISTANCE")
        edge_1 = tree.outputs.geometry("Edge")

        (
            edge
            >> g.StoreNamedAttribute.point.float(selection=selection, name="radius", value=radius)
            >> edge_1
        )

ASSET = OSetEdgeRadius

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "925722af-3fbd-4bb1-8247-dfe9a1ecd480",
}
