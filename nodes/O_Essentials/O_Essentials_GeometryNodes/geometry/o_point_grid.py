# Node-group asset "O Point Grid" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OPointGrid(CustomGeometryGroup):
    _name = "O Point Grid"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        menu = tree.inputs.menu("Menu", "XY", optional_label=True)
        space = tree.inputs.float("Space", 0.10000000149011612, min_value=0.009999999776482582, max_value=1.0, subtype="DISTANCE")
        radius = tree.inputs.float("Radius", 1.0, min_value=0.10000000149011612, max_value=2.0)
        min = tree.inputs.vector("Min", (-1.0, -1.0, -1.0))
        max = tree.inputs.vector("Max", (1.0, 1.0, 1.0))
        position = tree.inputs.float("Position", 0.5, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
        inside = tree.inputs.boolean("Inside", False)
        points = tree.outputs.geometry("Points")

        index = g.Index()
        index_1 = g.Index()
        menu_switch = g.MenuSwitch.integer(menu, {"XY": 0, "XZ": 1, "YZ": 2, "XYZ": -1})
        result = g.Mix.vector(position, min, max, clamp_factor=True).o.result_vector
        vector_math = max + (9.999999747378752e-05, 9.999999747378752e-05, 9.999999747378752e-05)
        separate_xyz = g.SeparateXYZ(vector=vector_math)
        index_switch = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz.o.x, separate_xyz.o.x, separate_xyz.o.y))
        separate_xyz_1 = g.SeparateXYZ(vector=vector_math)
        index_switch_1 = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz_1.o.y, separate_xyz_1.o.z, separate_xyz_1.o.z))
        switch = inside.switch.vector(min, space * 0.5 + min)
        separate_xyz_2 = g.SeparateXYZ(vector=switch)
        index_switch_2 = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz_2.o.x, separate_xyz_2.o.x, separate_xyz_2.o.y))
        index_switch_3 = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz_2.o.y, separate_xyz_2.o.z, separate_xyz_2.o.z))
        math_1 = (index_switch_2.o.output / space).ceil() * space
        math_2 = (index_switch_3.o.output / space).ceil() * space
        index_switch_4 = g.IndexSwitch.vector(menu_switch.o.output, (g.CombineXYZ(x=math_1, y=math_2, z=result.z), g.CombineXYZ(x=math_1, y=result.y, z=math_2), g.CombineXYZ(x=result.x, y=math_1, z=math_2)))
        separate_xyz_3 = g.SeparateXYZ(vector=switch)
        index_switch_5 = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz_3.o.x, separate_xyz_3.o.x, separate_xyz_3.o.y))
        separate_xyz_4 = g.SeparateXYZ(vector=switch)
        index_switch_6 = g.IndexSwitch.float(menu_switch.o.output, (separate_xyz_4.o.y, separate_xyz_4.o.z, separate_xyz_4.o.z))
        math_3 = (index_switch_1.o.output / space).ceil() - (index_switch_6.o.output / space).ceil()
        math_4 = ((index_switch.o.output / space).ceil() - (index_switch_5.o.output / space).ceil()) * math_3
        math_5 = g.Math.truncated_modulo(index, math_3).o.value * space
        math_6 = (index.o.index / math_3).truncate() * space
        index_switch_7 = g.IndexSwitch.vector(menu_switch.o.output, (g.CombineXYZ(x=math_6, y=math_5), g.CombineXYZ(x=math_6, z=math_5), g.CombineXYZ(y=math_6, z=math_5)))
        math_7 = (g.SeparateXYZ(vector=vector_math).o.x / space).ceil() - (g.SeparateXYZ(vector=switch).o.x / space).ceil()
        math_8 = (g.SeparateXYZ(vector=vector_math).o.y / space).ceil() - (g.SeparateXYZ(vector=switch).o.y / space).ceil()
        math_9 = math_7 * math_8
        math_10 = g.Math.truncated_modulo(index_1, math_9)
        combine_xyz = g.CombineXYZ(x=(math_10.o.value / math_8).truncate() * space, y=g.Math.truncated_modulo(math_10, math_8).o.value * space, z=(index_1.o.index / math_9).truncate() * space)
        math_11 = (g.SeparateXYZ(vector=vector_math).o.z / space).ceil() - (g.SeparateXYZ(vector=switch).o.z / space).ceil()
        separate_xyz_5 = g.SeparateXYZ(vector=switch)
        combine_xyz_1 = g.CombineXYZ(x=(separate_xyz_5.o.x / space).ceil() * space, y=(separate_xyz_5.o.y / space).ceil() * space, z=(separate_xyz_5.o.z / space).ceil() * space)
        transform_geometry = g.TransformGeometry(geometry=g.Points(count=math_4, position=index_switch_7), translation=index_switch_4)
        transform_geometry_1 = g.TransformGeometry(geometry=g.Points(count=math_9 * math_11, position=combine_xyz), translation=combine_xyz_1)
        (
            (menu_switch.o.output > -1).switch.geometry(transform_geometry_1, transform_geometry)
            >> g.SetPointRadius(radius=space * radius * 0.5)
            >> g.SetPosition(offset=inside.switch.vector((0.0, 0.0, 0.0), space * -0.5))
            >> points
        )

ASSET = OPointGrid

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
