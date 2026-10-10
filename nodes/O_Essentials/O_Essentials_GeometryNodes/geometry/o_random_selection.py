from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class ORandomSelection(CustomGeometryGroup):
    _name = "O Random Selection"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        factor = tree.inputs.float("Factor", 0.5, min_value=0.0, max_value=1.0, subtype="FACTOR")
        id = tree.inputs.integer("ID", 0, hide_value=True, default_input="ID_OR_INDEX")
        seed = tree.inputs.integer("Seed", 0, min_value=-10000, max_value=10000)
        selection = tree.outputs.boolean("Selection")

        (g.RandomValue.float(id=id, seed=seed) < factor) >> selection

ASSET = ORandomSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
