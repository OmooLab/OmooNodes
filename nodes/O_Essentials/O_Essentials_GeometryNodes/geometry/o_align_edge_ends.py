from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_curve_to_edge import OCurveToEdge
from .o_edge_to_curve import OEdgeToCurve
from .o_index_selection import OIndexSelection
from .o_mask_by_distance import OMaskByDistance


class OAlignEdgeEnds(CustomGeometryGroup):
    _name = "O Align Edge Ends"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        distance_threshold = tree.inputs.float("Distance Threshold", 0.05, min_value=0.0, subtype="DISTANCE")
        iterations = tree.inputs.integer("Iterations", 5, min_value=1, max_value=10)
        edge_1 = tree.outputs.geometry("Edge")

        map_range = g.MapRange.float(iterations, 1.0, 10.0, 1.0, 0.5, clamp=True)
        position = g.Position()
        repeat_zone = g.RepeatZone(iterations)
        geometry = repeat_zone.items.geometry(OEdgeToCurve(Edge=edge), "Geometry")
        for_each = g.ForEachGeometryElementZone.curve(geometry=geometry.current)
        curve_to_mesh = g.CurveToMesh(curve=for_each.input.o.element)
        delete_geometry = g.DeleteGeometry.point(curve_to_mesh, OIndexSelection(Invert=True))
        capture = g.CaptureAttribute.point(geometry=g.DeleteGeometry.spline(geometry.current, OIndexSelection(Index=for_each.index)))
        attribute = capture.items.float(g.Radius(), "Attribute")
        curve_to_mesh_1 = capture.o.geometry >> g.CurveToMesh()
        o_index_selection = OIndexSelection(Index=g.DomainSize(geometry=curve_to_mesh).o.point_count + -1.0, Invert=True)
        delete_geometry_1 = g.DeleteGeometry.point(curve_to_mesh, o_index_selection)
        sample_nearest = g.SampleNearest.point(curve_to_mesh_1)
        sample_index = g.SampleIndex.point.vector(curve_to_mesh_1, position, sample_nearest)
        math_1 = g.Radius().o.radius.max(g.SampleIndex.point.float(curve_to_mesh_1, attribute.output, sample_nearest))
        math_2 = math_1 + distance_threshold
        o_mask_by_distance = OMaskByDistance(Geometry=for_each.input.o.element, Source=delete_geometry, **{"Max Distance": math_2})
        mix = g.Mix.vector(o_mask_by_distance.o.mask * map_range.o.result, g.Position(), g.SampleIndex.point.vector(delete_geometry, sample_index), clamp_factor=True)
        compare = sample_index.o.value.distance(position) < math_2
        set_position = (
            o_mask_by_distance
            >> g.SetPosition(selection=g.SampleIndex.point.boolean(delete_geometry, compare), position=mix.o.result_vector)
        )
        o_mask_by_distance_1 = OMaskByDistance(Geometry=set_position, Source=delete_geometry_1, **{"Max Distance": math_2})
        mix_1 = g.Mix.vector(o_mask_by_distance_1.o.mask * map_range.o.result, g.Position(), g.SampleIndex.point.vector(delete_geometry_1, sample_index), clamp_factor=True)
        set_position_1 = (
            o_mask_by_distance_1
            >> g.SetPosition(selection=g.SampleIndex.point.boolean(delete_geometry_1, compare), position=mix_1.o.result_vector)
        )
        set_position_1 >> for_each.generation.input
        for_each.generation.output >> geometry.next
        OCurveToEdge(Curve=geometry.result) >> edge_1

ASSET = OAlignEdgeEnds

ASSET_METADATA = {
    "catalog_id": "925722af-3fbd-4bb1-8247-dfe9a1ecd480",
}
