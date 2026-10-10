from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class ORestPosition(CustomGeometryGroup):
    _name = "O Rest Position"
    _color_tag = "ATTRIBUTE"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        geometry_1 = tree.outputs.geometry("Geometry")
        rest_positon = tree.outputs.vector("Rest Positon")

        capture = g.CaptureAttribute.point(geometry=geometry)
        position = capture.items.vector(g.Position(), "Position")

        capture.o.geometry >> geometry_1
        position.output >> rest_positon

ASSET = ORestPosition

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "304de8ab-a7d3-4df3-b6b2-4674d8814339",
}
