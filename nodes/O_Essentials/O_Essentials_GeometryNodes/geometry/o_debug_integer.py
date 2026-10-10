import bpy
from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class ODebugInteger(CustomGeometryGroup):
    _name = "O Debug Integer"
    _color_tag = "OUTPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        integer = tree.inputs.integer("Integer", 0, hide_value=True, default_input="ID_OR_INDEX")
        menu = tree.inputs.menu("Menu", "Color", expanded=True, optional_label=True)
        with tree.inputs.panel("Options", default_closed=True):
            seed = tree.inputs.integer("Seed", 0, min_value=-10000, max_value=10000)
        debug = tree.outputs.geometry("Debug")
        color = tree.outputs.color("Color", (0.8, 0.8, 0.8, 1.0))

        random_value = g.RandomValue.float(id=integer, seed=seed)
        _color_ramp = g.ColorRamp(fac=random_value, items=((0.0, (1.0, 0.27505708, 0.0025564549, 1.0)), (0.25, (0.013605382, 1.0, 0.94014776, 1.0)), (0.5, (0.18099567, 1.0, 0.0, 1.0)), (0.75, (0.12998807, 0.0, 1.0, 1.0)), (1.0, (1.0, 0.6487455, 0.0019993638, 1.0))), color_interpolation="EASE")
        _color_ramp_1 = g.ColorRamp(fac=random_value, items=((0.0, (1.0, 0.6627054, 0.0024691364, 1.0)), (0.5, (0.0, 0.9679999, 1.0, 1.0)), (1.0, (0.36785817, 0.0037836304, 1.0, 1.0))), color_interpolation="EASE")
        menu_switch = g.MenuSwitch.color(menu, {"Color": g.RandomValue.vector((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), integer, seed), "Grayscale": g.ColorRamp(fac=random_value).o.color})
        (
            mesh
            >> g.StoreNamedAttribute.point.color(name="o_color", value=menu_switch.o.output)
            >> g.SetMaterial(material=bpy.data.materials.get("O Debug Color"))
            >> debug
        )

        menu_switch >> color

ASSET = ODebugInteger

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "3aee6aa4-2dd5-4adb-9bed-3676454cdeff",
}
