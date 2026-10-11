from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_is_edge_boundary import OIsEdgeBoundary


class OIsUVSplit(CustomGeometryGroup):
    _name = "O Is UV Split"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        uv = tree.inputs.string("UV", "UVMap")
        is_uv_split = tree.outputs.boolean("Is UV Split")
        same_island = tree.outputs.boolean("Same Island")
        different_island = tree.outputs.boolean("Different Island")

        corners_of_edge = g.CornersOfEdge()
        corners_of_edge_1 = g.CornersOfEdge(sort_index=1)
        named_attribute = g.NamedAttribute.vector(uv)
        evaluate_at_index = named_attribute.o.attribute.corner.at(g.OffsetCornerInFace(corner_index=corners_of_edge.o.corner_index, offset=1))
        compare = g.Compare(a=named_attribute.o.attribute.corner.at(corners_of_edge_1.o.corner_index), b=evaluate_at_index, epsilon=0.001, operation="NOT_EQUAL", data_type="VECTOR", mode="ELEMENT")
        evaluate_at_index_1 = named_attribute.o.attribute.corner.at(g.OffsetCornerInFace(corner_index=corners_of_edge_1.o.corner_index, offset=1))
        compare_1 = g.Compare(a=named_attribute.o.attribute.corner.at(corners_of_edge.o.corner_index), b=evaluate_at_index_1, epsilon=0.001, operation="NOT_EQUAL", data_type="VECTOR", mode="ELEMENT")
        boolean_math = ~OIsEdgeBoundary().o.is_edge_boundary & (compare_1.o.result | compare)
        edges_to_face_groups = g.EdgesToFaceGroups(boundary_edges=boolean_math)
        evaluate_at_index_2 = edges_to_face_groups.o.face_group_id.corner.at(g.CornersOfEdge(sort_index=1).o.corner_index)
        compare_2 = g.Compare.integer.equal(edges_to_face_groups.o.face_group_id.corner.at(g.CornersOfEdge().o.corner_index), evaluate_at_index_2)
        (boolean_math & compare_2) >> same_island
        boolean_math_1 = g.BooleanMath.subtract(boolean_math, compare_2)

        boolean_math >> is_uv_split
        boolean_math_1 >> different_island

ASSET = OIsUVSplit

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
