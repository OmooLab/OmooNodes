from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class ONearbySelection(CustomGeometryGroup):
    _name = "O Nearby Selection"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        point_index = tree.inputs.integer("Point Index", 0, min_value=0)
        range = tree.inputs.float("Range", 0.1, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        exclude_self = tree.inputs.boolean("Exclude Self", True)
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        compare = g.Position().o.position.point.at(point_index).distance(g.Position()) < range
        switch = invert.switch.boolean(compare, ~compare)
        (
            exclude_self.switch.boolean(switch, switch & g.Compare.integer.not_equal(point_index, g.Index()))
            >> selection
        )

ASSET = ONearbySelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
