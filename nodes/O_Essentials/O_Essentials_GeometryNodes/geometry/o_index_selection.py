# Node-group asset "O Index Selection" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OIndexSelection(CustomGeometryGroup):
    _name = "O Index Selection"
    _color_tag = "INPUT"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        index = tree.inputs.integer("Index", 0)
        invert = tree.inputs.boolean("Invert", False)
        selection = tree.outputs.boolean("Selection")

        compare = g.Compare.integer.equal(index, g.Index())
        invert.switch.boolean(compare, ~compare.o.result) >> selection

ASSET = OIndexSelection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
