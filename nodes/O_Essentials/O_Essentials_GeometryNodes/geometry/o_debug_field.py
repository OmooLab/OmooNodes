# Node-group asset "O Debug Field" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
import bpy
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_point_grid import OPointGrid


class ODebugField(CustomGeometryGroup):
    _name = "O Debug Field"
    _color_tag = "OUTPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        container = tree.inputs.geometry("Container")
        field = tree.inputs.vector("Field", (0.0, 0.0, 0.0), hide_value=True)
        normalize = tree.inputs.boolean("Normalize", True)
        type = tree.inputs.menu("Type", "XY", expanded=True, optional_label=True)
        position = tree.inputs.float("Position", 0.5, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Container", default_closed=True):
            min = tree.inputs.vector("Min", (-1.0, -1.0, -1.0), subtype="TRANSLATION")
            max = tree.inputs.vector("Max", (1.0, 1.0, 1.0), subtype="TRANSLATION")
            space = tree.inputs.float("Space", 0.5, min_value=0.10000000149011612, max_value=1.0, subtype="DISTANCE")
        debug = tree.outputs.geometry("Debug")
        color = tree.outputs.color("Color", (0.0, 0.0, 0.0, 1.0))

        bounding_box = g.BoundingBox(geometry=container)
        math_1 = space * 1.0
        menu_switch = g.MenuSwitch.integer(type, {"XY": 0, "XZ": 1, "YZ": 2})
        index_switch = g.IndexSwitch.rotation(menu_switch.o.output, ((0.0, 0.0, 0.0), (1.5707963705062866, 0.0, 0.0), (0.0, 1.5707963705062866, 0.0)))
        vector_math = bounding_box.o.min + min
        vector_math_1 = bounding_box.o.max + max
        o_point_grid = OPointGrid(Space=space, Radius=0.5, Min=vector_math, Max=vector_math_1, Position=position)
        o_point_grid_1 = OPointGrid(Menu="XZ", Space=space, Radius=0.5, Min=vector_math, Max=vector_math_1, Position=position)
        o_point_grid_2 = OPointGrid(Menu="YZ", Space=space, Radius=0.5, Min=vector_math, Max=vector_math_1, Position=position)
        o_point_grid_3 = OPointGrid(Menu="XYZ", Space=space, Radius=0.5, Min=vector_math, Max=vector_math_1, Position=0.23456789553165436)
        merge_by_distance = (
            g.IndexSwitch.geometry(menu_switch.o.output, (o_point_grid, o_point_grid_1, o_point_grid_2, o_point_grid_3))
            >> g.InstanceOnPoints(instance=g.Grid(size_x=math_1, size_y=math_1), rotation=index_switch)
            >> g.RealizeInstances(realize_to_point_domain=True)
            >> g.MergeByDistance(distance=space * 0.10000000149011612)
        )
        attribute_statistic = g.AttributeStatistic.point.vector(merge_by_distance, attribute=field)
        switch = normalize.switch.vector(field, field.map_range(attribute_statistic.o.min, attribute_statistic.o.max))
        (
            g.StoreNamedAttribute.point.color(merge_by_distance, name="o_color", value=switch)
            >> g.SetMaterial(material=bpy.data.materials.get("O Debug Color"))
            >> debug
        )
        viewer = g.Viewer()
        viewer.node.viewer_items.clear()
        viewer.node.viewer_items.new('GEOMETRY', 'Geometry').auto_remove = False
        o_point_grid_3 >> viewer.i[0]
        viewer.node.viewer_items.new('FLOAT', 'Value').auto_remove = False

        switch >> color

ASSET = ODebugField

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "3aee6aa4-2dd5-4adb-9bed-3676454cdeff",
}

DATABLOCK_DEPENDENCIES = {
    "materials": ("O Debug Color",),
}
