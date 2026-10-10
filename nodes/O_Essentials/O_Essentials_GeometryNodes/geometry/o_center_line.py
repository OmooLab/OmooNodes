from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_blend import OBlend
from .o_curve_to_edge import OCurveToEdge
from .o_project import OProject
from .o_region_selection import ORegionSelection
from .o_resample_edge import OResampleEdge
from .o_smooth import OSmooth


class OCenterLine(CustomGeometryGroup):
    _name = "O Center Line"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        resolution = tree.inputs.float("Resolution", 0.05, min_value=0.02, max_value=0.2, subtype="DISTANCE")
        iterations = tree.inputs.integer("Iterations", 10, min_value=5, max_value=20)
        ray = tree.inputs.boolean("Ray", False)
        with tree.inputs.panel("Options", default_closed=True):
            smooth_iterations = tree.inputs.integer("Smooth Iterations", 10, description="How many times to blur the values for all elements", min_value=1, max_value=20)
            smooth_weight = tree.inputs.float("Smooth Weight", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
        edge = tree.outputs.geometry("Edge")

        raycast = (
            mesh
            >> g.ExtrudeMesh(offset_scale=0.0001, individual=False)
            >> g.Raycast.float(ray_direction=g.Normal().o.normal * -1.0)
        )
        set_position = g.SetPosition(geometry=mesh, selection=raycast.o.is_hit, position=raycast.o.hit_position)
        o_smooth = OSmooth(Geometry=set_position, Iterations=smooth_iterations, **{"Pin Sharp": 1.0}, Weight=smooth_weight)
        o_blend = OBlend(Geometry=mesh, Source=o_smooth)
        repeat_zone = g.RepeatZone(iterations)
        geometry = repeat_zone.items.geometry(o_blend, "Geometry")
        merge_by_distance = (
            g.SubdivisionSurface(mesh=geometry.current, edge_crease=1.0, limit_surface=False, uv_smooth="None", boundary_smooth="Keep Corners")
            >> g.MergeByDistance(selection=g.Compare(a=g.FaceNeighbors().o.vertex_count, b=0.0), distance=resolution, mode="Connected")
            >> g.MergeByDistance(distance=resolution, mode="Connected")
        )
        o_project = OProject(Geometry=merge_by_distance, Selection=ray & ORegionSelection(**{"Region Mesh": o_blend}, Invert=True), Source=o_blend, **{"Max Distance": 5.0, "Radius Offset": 0.5}, Custom=(0.0, 0.0, 0.0), **{"Normal Smooth": 0}, _named_links=[("Menu", "Minimum Distance"), ("Menu", "Normal")])
        o_smooth_1 = OSmooth(Geometry=o_project, Iterations=1, **{"Pin Sharp": 1.0, "Pin Boundary": 0.9999})
        o_smooth_1 >> geometry.next
        (
            OResampleEdge(Edge=OCurveToEdge(Curve=geometry.result >> g.MeshToCurve()), Length=resolution)
            >> edge
        )

ASSET = OCenterLine

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
