from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OIDSelection(CustomGeometryGroup):
    _name = "O ID Selection"
    _color_tag = "INPUT"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        id = tree.inputs.integer("ID", 0)
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        compare = g.Compare.integer.equal(id, g.ID())
        invert.switch.boolean(compare, ~compare.o.result) >> selection

ASSET = OIDSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
