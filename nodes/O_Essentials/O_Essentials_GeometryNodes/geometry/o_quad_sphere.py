# Node-group asset "O Quad Sphere" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from ._shared.o_spherization_correction import OSpherizationCorrection


class OQuadSphere(CustomGeometryGroup):
    _name = "O Quad Sphere"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        segments = tree.inputs.integer("Segments", 8, min_value=3, max_value=64)
        radius = tree.inputs.float("Radius", 1.0, min_value=0.0, subtype="DISTANCE")
        mesh = tree.outputs.geometry("Mesh")
        uv_map = tree.outputs.vector("UV Map")

        cube = g.Cube(vertices_x=segments, vertices_y=segments, vertices_z=segments, size=(2.0, 2.0, 2.0))
        position = g.Position().o.position
        combine_xyz = g.CombineXYZ(x=OSpherizationCorrection(Value=position.x, A=position.y, B=position.z), y=OSpherizationCorrection(Value=position.y, A=position.z, B=position.x), z=OSpherizationCorrection(Value=position.z, A=position.x, B=position.y))
        cube >> g.SetPosition(position=combine_xyz.o.vector * radius) >> mesh

        cube.o.uv_map >> uv_map

ASSET = OQuadSphere

ASSET_METADATA = {
    "description": "Generates a sphere mesh composed of quadrilateral faces.",
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
