from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_displace import ODisplace
from .o_is_edge_boundary import OIsEdgeBoundary


class OSolidfy(CustomGeometryGroup):
    _name = "O Solidfy"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        thickness = tree.inputs.float("Thickness", 0.100000024, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        offset = tree.inputs.float("Offset", 0.0, min_value=-1.0, max_value=1.0, subtype="FACTOR")
        geometry = tree.outputs.geometry("Geometry")
        side = tree.outputs.boolean("Side")

        vector_math = g.Normal().o.normal.face.evaluate() * (thickness * offset.map_range(-1.0, to_min=-1.0, to_max=0.0))
        o_displace = ODisplace(Geometry=mesh, Direction="Vector", Height=thickness, Vector=vector_math)
        extrude_mesh = g.ExtrudeMesh(mesh=o_displace, offset_scale=thickness, individual=False)
        (
            g.JoinGeometry(geometry=(g.FlipFaces(mesh=o_displace), extrude_mesh))
            >> g.MergeByDistance(selection=OIsEdgeBoundary(), distance=0.000001)
            >> geometry
        )

        extrude_mesh.o.side >> side

ASSET = OSolidfy

ASSET_METADATA = {
    "description": "Adds thickness to a model, transforming it from a surface to a solid.",
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
