# Node-group asset "O Debug Direction Field" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_point_grid import OPointGrid


class ODebugDirectionField(CustomGeometryGroup):
    _name = "O Debug Direction Field"
    _color_tag = "OUTPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        container = tree.inputs.geometry("Container")
        direction = tree.inputs.vector("Direction", (0.0, 0.0, 0.0), hide_value=True, default_input="NORMAL")
        normalize = tree.inputs.boolean("Normalize", True)
        type = tree.inputs.menu("Type", "XY", expanded=True, optional_label=True)
        position = tree.inputs.float("Position", 0.5, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
        size = tree.inputs.float("Size", 0.5, min_value=0.10000000149011612, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Container", default_closed=True):
            space = tree.inputs.float("Space", 0.5, min_value=0.10000000149011612, max_value=1.0, subtype="DISTANCE")
            min = tree.inputs.vector("Min", (-1.0, -1.0, -1.0), subtype="TRANSLATION")
            max = tree.inputs.vector("Max", (1.0, 1.0, 1.0), subtype="TRANSLATION")
        debug = tree.outputs.geometry("Debug")

        bounding_box = g.BoundingBox(geometry=container)
        math_1 = space * size
        menu_switch = g.MenuSwitch.integer(type, {"XY": 0, "XZ": 1, "YZ": 2})
        set_shade_smooth = g.SetShadeSmooth.face(g.Cube(size=(0.20000000298023224, 0.20000000298023224, 0.20000000298023224)))
        set_shade_smooth_1 = (
            g.Cylinder(vertices=3, radius=0.07500000298023224)
            >> g.TransformGeometry(translation=(0.0, 0.0, 1.0))
            >> g.SetShadeSmooth.face()
        )
        vector_math = direction.length()
        vector_math_1 = bounding_box.o.min + min
        vector_math_2 = bounding_box.o.max + max
        o_point_grid = OPointGrid(Space=space, Radius=0.5, Min=vector_math_1, Max=vector_math_2, Position=position)
        o_point_grid_1 = OPointGrid(Menu="XZ", Space=space, Radius=0.5, Min=vector_math_1, Max=vector_math_2, Position=position)
        o_point_grid_2 = OPointGrid(Menu="YZ", Space=space, Radius=0.5, Min=vector_math_1, Max=vector_math_2, Position=position)
        o_point_grid_3 = OPointGrid(Menu="XYZ", Space=space, Radius=0.5, Min=vector_math_1, Max=vector_math_2, Position=0.23456789553165436)
        index_switch = g.IndexSwitch.geometry(menu_switch.o.output, (o_point_grid, o_point_grid_1, o_point_grid_2, o_point_grid_3))
        attribute_statistic = g.AttributeStatistic.point.float(index_switch, attribute=vector_math)
        compare = g.Compare.float.not_equal(attribute_statistic.o.min, attribute_statistic.o.max, 0.0010000000474974513)
        switch = compare.o.result.switch.float(1.0, vector_math.map_range(attribute_statistic.o.min, attribute_statistic.o.max))
        switch_1 = normalize.switch.vector(direction, direction.normalize() * switch)
        index_switch_1 = g.IndexSwitch.vector(menu_switch.o.output, (g.CombineXYZ(x=switch_1.x, y=switch_1.y), g.CombineXYZ(x=switch_1.x, z=switch_1.z), g.CombineXYZ(y=switch_1.y, z=switch_1.z), switch_1))
        align_rotation_to_vector = g.AlignRotationToVector(vector=index_switch_1)
        instance_on_points = g.InstanceOnPoints(points=index_switch, instance=set_shade_smooth, rotation=align_rotation_to_vector, scale=math_1)
        instance_on_points_1 = g.InstanceOnPoints(points=index_switch, instance=set_shade_smooth_1, rotation=align_rotation_to_vector, scale=g.CombineXYZ(x=math_1, y=math_1, z=index_switch_1.o.output.length() * math_1))
        join_geometry = g.JoinGeometry(geometry=(instance_on_points_1, instance_on_points))

        join_geometry >> debug

ASSET = ODebugDirectionField

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "3aee6aa4-2dd5-4adb-9bed-3676454cdeff",
}
