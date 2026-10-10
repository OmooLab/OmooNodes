from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_edge_to_curve import OEdgeToCurve
from .o_mix_color import OMixColor
from .o_quad_sphere import OQuadSphere
from .o_solidfy import OSolidfy


class OTube(CustomGeometryGroup):
    _name = "O Tube"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        resolution = tree.inputs.integer("Resolution", 8, description="Number of points on the circle", min_value=4, max_value=16)
        radius_scale = tree.inputs.float("Radius Scale", 1.0, description="Distance of the points from the origin", min_value=0.1, max_value=2.0)
        thickness = tree.inputs.float("Thickness", 0.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        shade_smooth = tree.inputs.boolean("Shade Smooth", True)
        fill_caps = tree.inputs.boolean("Fill Caps", True, description="If the profile spline is cyclic, fill the ends of the generated mesh with N-gons")
        with tree.inputs.panel("Connect", default_closed=True):
            connect = tree.inputs.boolean("Connect", False, is_panel_toggle=True)
            distance_threshold = tree.inputs.float("Distance Threshold", 0.01, min_value=0.0, subtype="DISTANCE")
            color = tree.inputs.string("Color", "")
        mesh = tree.outputs.geometry("Mesh")

        curve_circle = g.CurveCircle(resolution=resolution, radius=radius_scale)
        _index = g.Index()
        capture = g.CaptureAttribute.point(geometry=edge)
        index_1 = capture.items.integer(g.MeshIsland().o.island_index, "Index")
        named_attribute = g.NamedAttribute.color(color)
        position = g.Position()
        math_1 = radius_scale * g.Radius()
        math_2 = (math_1 * (1.0 + thickness) * 6.2831855 / resolution).max(0.001)
        radius = g.Radius()
        radius_1 = g.Radius()
        resample_curve = (
            OEdgeToCurve(Edge=edge)
            >> g.ResampleCurve(length=math_2, mode="Length", keep_last_segment=True)
        )
        set_shade_smooth = (
            OQuadSphere(Segments=(resolution * 0.2).max(4.0), Radius=1.1)
            >> g.SetShadeSmooth.face()
        )
        separate_geometry = (
            capture.o.geometry
            >> g.SeparateGeometry.point(selection=g.VertexNeighbors().o.vertex_count < 2)
        )
        for_each = g.ForEachGeometryElementZone(geometry=separate_geometry.o.selection)
        index_2 = for_each.items.integer(index_1.output, "Index")
        separate_geometry_1 = g.SeparateGeometry.point(edge, g.Compare.integer.not_equal(index_2.output, g.MeshIsland().o.island_index))
        sample_nearest = g.SampleNearest.point(separate_geometry_1.o.selection)
        sample_index = g.SampleIndex.point.float(separate_geometry_1.o.selection, radius_1, sample_nearest)
        math_3 = sample_index.o.value + radius_1
        sample_index_1 = g.SampleIndex.point.vector(separate_geometry_1.o.selection, position, sample_nearest)
        sample_index_2 = g.SampleIndex.point.color(separate_geometry_1.o.selection, named_attribute.o.attribute, sample_nearest)
        o_mix_color = OMixColor(Factor=sample_index.o.value / math_3, A=sample_index_2, B=named_attribute.o.attribute)
        store_named_attribute = (
            g.SetPosition(geometry=for_each.input.o.element, position=(g.Position().o.position + sample_index_1) * 0.5)
            >> g.StoreNamedAttribute.point.float(name="radius", value=g.Mix.float(0.5, sample_index.o.value.max(radius_1), math_3 * 0.5, clamp_factor=True).o.result_float)
            >> g.StoreNamedAttribute.point.color(name=color, value=o_mix_color)
        )
        sample_index_3 = g.SampleIndex.point.boolean(for_each.input.o.element, sample_index_1.o.value.distance(position) < distance_threshold)
        (
            sample_index_3.o.value.switch.geometry(true=store_named_attribute)
            >> for_each.generation.input
        )
        merge_by_distance = g.MergeByDistance(geometry=for_each.generation.output)
        capture_1 = g.CaptureAttribute.point(geometry=merge_by_distance)
        radius_2 = capture_1.items.float(math_1, "Radius")
        geometry_proximity = g.GeometryProximity(target=merge_by_distance, target_element="POINTS")
        boolean_math = ~(geometry_proximity.o.is_valid & (geometry_proximity.o.distance < math_2)) & g.EndpointSelection()
        capture_2 = g.CaptureAttribute.point(geometry=resample_curve)
        radius_3 = capture_2.items.float(math_1, "Radius")
        boolean = capture_2.items.boolean(boolean_math, "Boolean")
        curve_to_mesh = g.CurveToMesh(curve=capture_2.o.geometry, profile_curve=curve_circle, scale=radius, fill_caps=True)
        curve_to_mesh_1 = g.CurveToMesh(curve=capture_2.o.geometry, profile_curve=curve_circle, scale=radius, fill_caps=fill_caps)
        capture_3 = g.CaptureAttribute.face(geometry=g.StoreNamedAttribute.point.float(curve_to_mesh, name="radius", value=radius_3.output))
        result = capture_3.items.boolean(boolean.output, "Result")
        store_named_attribute_1 = (
            capture_1.o.geometry
            >> g.InstanceOnPoints(instance=set_shade_smooth, scale=radius_2.output)
            >> g.StoreNamedAttribute.instance.float(name="radius", value=radius_2.output)
            >> g.RealizeInstances()
            >> g.StoreNamedAttribute.corner.color(name=color, value=g.NamedAttribute.color(color).o.attribute.point.evaluate())
        )
        split_to_instances = g.SplitToInstances.face(g.JoinGeometry(geometry=(store_named_attribute_1, capture_3.o.geometry)), group_id=g.MeshIsland().o.island_index)
        delete_geometry = g.DeleteGeometry.face(g.MeshBoolean(mesh_2=(split_to_instances,), operation="UNION", solver="MANIFOLD"), g.BooleanMath.subtract(result.output, fill_caps))
        switch = connect.switch.geometry(g.StoreNamedAttribute.point.float(curve_to_mesh_1, name="radius", value=radius_3.output), delete_geometry)
        (
            (thickness > 0.0).switch.geometry(switch, OSolidfy(Mesh=switch, Thickness=g.Radius().o.radius * thickness, Offset=0.5))
            >> g.SetShadeSmooth.face(shade_smooth=shade_smooth)
            >> g.SetShadeSmooth.edge(shade_smooth=shade_smooth)
            >> mesh
        )

ASSET = OTube

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
