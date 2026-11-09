from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_relax import ORelax
from .o_transfer_uv import OTransferUV
from .o_uv_island import OUVIsland


class OFastRemesh(CustomGeometryGroup):
    _name = "O Fast Remesh"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        resolution = tree.inputs.float("Resolution", 0.1, min_value=0.01, max_value=0.1)
        relax_iterations = tree.inputs.integer("Relax Iterations", 2, min_value=1, max_value=10)
        with tree.inputs.panel("Options", default_closed=True):
            shade_smooth = tree.inputs.boolean("Shade Smooth", True)
            relax_weight = tree.inputs.float("Relax Weight", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
            fix_topo_steps = tree.inputs.integer("Fix Topo Steps", 3, min_value=1, max_value=10)
            fix_uv = tree.inputs.float("Fix UV", 0.1, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
            fix_uv_range = tree.inputs.float("Fix UV Range", 0.1, min_value=0.0, max_value=0.1)
            uv = tree.inputs.string("UV", "UVMap")
        mesh_1 = tree.outputs.geometry("Mesh")

        boolean_math = g.EvaluateOnDomain.edge.float(g.EdgeNeighbors() > 2).o.value.face.evaluate() & g.EvaluateOnDomain.edge.float(g.EdgeNeighbors() < 2).o.value.face.evaluate()
        evaluate_on_domain = g.EvaluateOnDomain.edge.float(g.EdgeNeighbors() < 2).o.value.face.evaluate().edge.evaluate()
        accumulate_field = g.EdgeNeighbors().o.face_count.face.total(g.EdgesToFaceGroups(boundary_edges=evaluate_on_domain))
        capture = g.CaptureAttribute.corner(geometry=mesh)
        face_group_id = capture.items.integer(OUVIsland(), "Face Group ID")
        capture_1 = g.CaptureAttribute.face(geometry=capture.o.geometry)
        island_index = capture_1.items.integer(g.MeshIsland().o.island_index, "Island Index")
        repeat_zone = g.RepeatZone(relax_iterations)
        geometry = repeat_zone.items.geometry(g.Triangulate(mesh=capture_1.o.geometry), "Geometry")
        iter = repeat_zone.items.integer(name="Iter")
        merge_by_distance = g.MergeByDistance(geometry=geometry.current, distance=resolution * 0.5, mode="Connected")
        repeat_zone_1 = g.RepeatZone(fix_topo_steps)
        geometry_1 = repeat_zone_1.items.geometry(merge_by_distance, "Geometry")
        separate_geometry = g.SeparateGeometry.face(g.SeparateGeometry.face(geometry_1.current, boolean_math).o.inverted, accumulate_field < 2)
        separate_geometry.o.inverted >> geometry_1.next
        o_relax = ORelax(Geometry=geometry_1.result, Iterations=1, Weight=relax_weight, **{"Max Distance": resolution * 2.0, "Mesh Island": island_index.output, "Source Mesh Island": g.MeshIsland().o.island_index}, _named_links=[("Source", "Custom"), ("Source", capture_1.o.geometry)])
        o_relax >> geometry.next
        iter.current + 1.0 >> iter.next
        delete_geometry = (
            geometry.result
            >> g.DeleteGeometry.face(selection=g.FaceArea().o.area.face.total(g.MeshIsland().o.island_index) < resolution ** 2.0)
        )
        (
            OTransferUV(Mesh=delete_geometry, Source=capture.o.geometry, Fix=fix_uv, **{"Fix Range": fix_uv_range}, UV=uv, _named_links=[("UV Island", "Custom"), ("UV Island", face_group_id.output)])
            >> g.SetShadeSmooth.face(shade_smooth=shade_smooth)
            >> mesh_1
        )

ASSET = OFastRemesh

ASSET_METADATA = {
    "description": "Recreates the shape of the input surface using triangles.",
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
