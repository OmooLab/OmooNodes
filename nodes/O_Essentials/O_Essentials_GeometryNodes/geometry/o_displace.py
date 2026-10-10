from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class ODisplace(CustomGeometryGroup):
    _name = "O Displace"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        strength = tree.inputs.float("Strength", 1.0, min_value=-10000.0, max_value=10000.0)
        direction = tree.inputs.menu("Direction", "Normal", expanded=True, optional_label=True)
        height = tree.inputs.float("Height", 1.0, subtype="DISTANCE")
        vector = tree.inputs.vector("Vector", (1.0, 1.0, 1.0), subtype="TRANSLATION")
        with tree.inputs.panel("Options", default_closed=True):
            midlevel = tree.inputs.float("Midlevel", 0.0, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        geometry_1 = tree.outputs.geometry("Geometry")

        menu_switch = g.MenuSwitch.vector(direction, {"Normal": g.Normal(legacy_corner_normals=True).o.normal * ((height - midlevel) * strength), "Vector": (vector - midlevel) * strength})
        (
            geometry
            >> g.SetPosition(selection=selection, offset=menu_switch.o.output)
            >> geometry_1
        )

ASSET = ODisplace

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
