from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OIsEdgeBoundary(CustomGeometryGroup):
    _name = "O Is Edge Boundary"
    _color_tag = "INPUT"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        is_edge_boundary = tree.outputs.boolean("Is Edge Boundary")

        (
            (g.Compare.integer.equal(g.EdgeNeighbors(), 1).o.result.edge.evaluate() | g.Compare.integer.equal(g.VertexNeighbors().o.vertex_count, 1))
            >> is_edge_boundary
        )

ASSET = OIsEdgeBoundary

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
