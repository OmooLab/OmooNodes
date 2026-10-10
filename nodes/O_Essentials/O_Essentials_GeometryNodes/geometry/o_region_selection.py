# Node-group asset "O Region Selection" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class ORegionSelection(CustomGeometryGroup):
    _name = "O Region Selection"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        region_mesh = tree.inputs.geometry("Region Mesh")
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        vector_math = g.VectorMath.dot_product((0.0, 0.0, -1.0), g.Raycast.float(region_mesh).o.hit_normal)
        invert.switch.boolean(vector_math.o.value, ~vector_math.o.value) >> selection

ASSET = ORegionSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
