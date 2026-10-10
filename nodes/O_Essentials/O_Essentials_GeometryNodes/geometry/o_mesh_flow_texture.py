# Node-group asset "O Mesh Flow Texture" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OMeshFlowTexture(CustomGeometryGroup):
    _name = "O Mesh Flow Texture"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        strength = tree.inputs.float("Strength", 1.0, min_value=0.0, max_value=100.0)
        reverse = tree.inputs.boolean("Reverse", False)
        radius = tree.inputs.float("Radius", 0.0, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        vector = tree.outputs.vector("Vector")

        geometry_proximity = g.GeometryProximity(target=mesh)
        vector_math = (geometry_proximity.o.position - g.Position()).normalize() * (strength / ((geometry_proximity.o.distance - radius).max(0.0) ** 2.0 + 1.0))
        vector_math * reverse.switch.float(1.0, -1.0) >> vector

ASSET = OMeshFlowTexture

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
