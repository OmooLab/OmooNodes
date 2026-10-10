# Node-group asset "O Tension" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OTension(CustomGeometryGroup):
    _name = "O Tension"
    _color_tag = "INPUT"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        rest_position = tree.inputs.vector("Rest Position", (0.0, 0.0, 0.0), default_input="POSITION")
        o_tension = tree.outputs.float("O Tension")

        edge_vertices = g.EdgeVertices()
        edge_vertices_1 = g.EdgeVertices()
        vector_math = rest_position.point.at(edge_vertices.o.vertex_index_1).distance(rest_position.point.at(edge_vertices.o.vertex_index_2))
        evaluate_on_domain = (edge_vertices_1.o.position_1.distance(edge_vertices_1.o.position_2) / vector_math - 1.0).edge.evaluate()
        evaluate_on_domain.point.evaluate() >> o_tension

ASSET = OTension

ASSET_METADATA = {
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
