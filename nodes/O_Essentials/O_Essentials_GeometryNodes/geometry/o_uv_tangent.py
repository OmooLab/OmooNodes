from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_is_uv_split import OIsUVSplit
from .o_rest_position import ORestPosition


class OUVTangent(CustomGeometryGroup):
    _name = "O UV Tangent"
    _color_tag = "ATTRIBUTE"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        with tree.inputs.panel("Options", default_closed=True):
            uv = tree.inputs.string("UV", "UVMap")
        mesh_1 = tree.outputs.geometry("Mesh")
        uv_tangent = tree.outputs.vector("UV Tangent")

        capture = g.CaptureAttribute.point(geometry=mesh)
        index = capture.items.integer(g.Index(), "Index")
        index_of_nearest = g.IndexOfNearest(group_id=g.MeshIsland().o.island_index)
        normal = g.Normal(legacy_corner_normals=True)
        position = g.Position()
        position_1 = g.Position()
        o_rest_position = ORestPosition(Geometry=capture.o.geometry >> g.SplitEdges(selection=OIsUVSplit(UV=uv).o.is_uv_split))
        set_position = (
            o_rest_position
            >> g.SetPosition(position=g.NamedAttribute.vector(uv).o.attribute)
        )
        vector_math = g.SampleIndex.point.vector(set_position, position, index_of_nearest.o.index).o.value - position
        vector_math_1 = vector_math.normalize()
        math_1 = vector_math_1.dot(g.Vector(vector=(1.0, 0.0, 0.0))).acos()
        switch = (vector_math_1.y < 0.0).switch.float(math_1 * -1.0, (g.Math.to_radians(360.0).o.value - math_1) * -1.0)
        capture_1 = g.CaptureAttribute.point(geometry=set_position)
        indexofneighbourvertex = capture_1.items.integer(index_of_nearest.o.index, "IndexOfNeighbourVertex")
        angle = capture_1.items.float(switch, "Angle")
        set_position_1 = (
            capture_1.o.geometry
            >> g.SetPosition(position=o_rest_position.o.rest_positon)
        )
        vector_math_2 = g.SampleIndex.point.vector(set_position_1, position_1, indexofneighbourvertex.output).o.value - position_1
        vector_math_3 = normal.o.normal.cross(g.VectorRotate(vector=vector_math_2, axis=normal.o.normal, angle=angle.output))
        vector_math_4 = vector_math_3.normalize()
        capture_2 = g.CaptureAttribute.point(geometry=set_position_1)
        bitangent = capture_2.items.vector(vector_math_4, "Bitangent")
        capture_3 = g.CaptureAttribute.point(geometry=mesh)
        capture_3.items.vector(g.SampleIndex.point.vector(set_position_1, vector_math_4, index.output), "Bitangent")

        capture_2.o.geometry >> mesh_1
        bitangent.output >> uv_tangent

ASSET = OUVTangent

ASSET_METADATA = {
    "catalog_id": "304de8ab-a7d3-4df3-b6b2-4674d8814339",
}
