# Node-group asset "O Debug Edge" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_wireframe import OWireframe


class ODebugEdge(CustomGeometryGroup):
    _name = "O Debug Edge"
    _color_tag = "OUTPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        attribute = tree.inputs.float("Attribute", 0.0)
        mesh = tree.outputs.geometry("Mesh")
        attribute_1 = tree.outputs.float("Attribute")

        capture = g.CaptureAttribute.point(geometry=edge)
        mask = capture.items.float(attribute, "Mask")
        OWireframe(Mesh=capture.o.geometry) >> mesh

        mask.output >> attribute_1

ASSET = ODebugEdge

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "3aee6aa4-2dd5-4adb-9bed-3676454cdeff",
}
