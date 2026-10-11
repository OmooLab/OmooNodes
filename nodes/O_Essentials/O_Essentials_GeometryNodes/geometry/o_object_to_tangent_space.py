from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OObjectToTangentSpace(CustomGeometryGroup):
    _name = "O Object to Tangent Space"
    _color_tag = "VECTOR"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        uv_tangent = tree.inputs.vector("UV Tangent", (0.0, 0.0, 0.0), hide_value=True)
        normal = tree.inputs.vector("Normal", (0.0, 0.0, 0.0), hide_value=True, default_input="NORMAL")
        normal_1 = tree.outputs.vector("Normal", (0.0, 0.0), dimensions=2)

        invert_rotation = g.AlignRotationToVector(vector=g.Normal(legacy_corner_normals=True).o.normal).o.rotation.invert()
        invert_rotation_1 = g.AlignRotationToVector(vector=uv_tangent.rotate(invert_rotation), axis="Y").o.rotation.invert()
        vector_math = normal.rotate(invert_rotation.rotate(invert_rotation_1)).mul_add((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        _combine_xyz = g.CombineXYZ(x=vector_math.x, y=vector_math.y)

        vector_math >> normal_1

ASSET = OObjectToTangentSpace

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
