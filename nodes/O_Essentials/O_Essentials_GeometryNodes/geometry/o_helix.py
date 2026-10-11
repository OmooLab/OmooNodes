from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_screw import OScrew


class OHelix(CustomGeometryGroup):
    _name = "O Helix"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        segments = tree.inputs.integer("Segments", 32, description="Number of steps in the revolution.", min_value=1, max_value=64)
        angle = tree.inputs.float("Angle", 12.56638, description="Angle of revolution.", subtype="ANGLE")
        radius = tree.inputs.float("Radius", 0.1, description="The radii of the new points", min_value=0.0, subtype="DISTANCE")
        height = tree.inputs.float("Height", 2.0, description="Offset the revolution along its axis.", min_value=0.0, max_value=340282000000000000000000000000000000000.0, subtype="DISTANCE")
        edge = tree.outputs.geometry("Edge")

        (
            OScrew(Mesh=g.PointsToVertices(points=g.Points(position=g.CombineXYZ(x=radius))), Angle=angle, Screw=height, Steps=segments)
            >> edge
        )

ASSET = OHelix

ASSET_METADATA = {
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
