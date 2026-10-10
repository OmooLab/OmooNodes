# Node-group asset "O Timing" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OTiming(CustomGeometryGroup):
    _name = "O Timing"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        menu = tree.inputs.menu("Menu", "At N Frame", optional_label=True, structure_type="SINGLE", force_non_field=True)
        n = tree.inputs.integer("N", 1, min_value=1, structure_type="SINGLE", force_non_field=True)
        boolean = tree.outputs.boolean("Boolean")

        scene_time = g.SceneTime()
        compare = g.Compare.float.equal(g.Math.truncated_modulo(scene_time.o.frame, n), 0.0, 0.0010000000474974513)
        (
            g.MenuSwitch.boolean(menu, {"Every N Frames": compare, "At N Frame": g.Compare.integer.equal(scene_time.o.frame, n), "After N Frame": g.Compare.integer.greater_than(scene_time.o.frame, n), "Before N Frame": g.Compare.integer.less_than(scene_time.o.frame, n)})
            >> boolean
        )

ASSET = OTiming

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
