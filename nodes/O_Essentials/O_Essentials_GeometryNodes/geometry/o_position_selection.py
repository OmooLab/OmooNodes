from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OPositionSelection(CustomGeometryGroup):
    _name = "O Position Selection"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        menu = tree.inputs.menu("Menu", "X", optional_label=True)
        vector = tree.inputs.vector("Vector", (0.0, 0.0, 0.0), min_value=-10000.0, max_value=10000.0, subtype="TRANSLATION")
        menu_1 = tree.inputs.menu("Menu", "Less Than", optional_label=True)
        n = tree.inputs.float("N", 0.0, min_value=-10000.0, max_value=10000.0, subtype="DISTANCE")
        a = tree.inputs.float("A", 0.0, min_value=-10000.0, max_value=10000.0, subtype="DISTANCE")
        b = tree.inputs.float("B", 1.0, min_value=-10000.0, max_value=10000.0, subtype="DISTANCE")
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        position = g.Position()
        menu_switch = g.MenuSwitch.float(menu, {"X": position.o.position.x, "Y": position.o.position.y, "Z": position.o.position.z, "Distance": position.o.position.distance(vector)})
        menu_switch_1 = g.MenuSwitch.boolean(menu_1, {"Less Than": menu_switch.o.output < n, "In Range": (menu_switch.o.output > a) & (menu_switch.o.output < b)})
        invert.switch.boolean(menu_switch_1.o.output, ~menu_switch_1.o.output) >> selection

ASSET = OPositionSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
