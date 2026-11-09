from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OShortestPaths(CustomGeometryGroup):
    _name = "O Shortest Paths"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        root = tree.inputs.boolean("Root", False, hide_value=True)
        cost = tree.inputs.float("Cost", 1.0, min_value=0.0, max_value=1.0)
        merged = tree.inputs.boolean("Merged", True)
        edge_1 = tree.outputs.geometry("Edge")
        total_cost = tree.outputs.float("Total Cost")
        factor = tree.outputs.float("Factor")

        edge_vertices = g.EdgeVertices()
        shortest_edge_paths = g.ShortestEdgePaths(end_vertex=root, edge_cost=cost * edge_vertices.o.position_1.distance(edge_vertices.o.position_2))
        edge_paths_to_curves = g.EdgePathsToCurves(mesh=edge, start_vertices=selection, next_vertex_index=shortest_edge_paths.o.next_vertex_index)
        capture = g.CaptureAttribute.point(geometry=edge_paths_to_curves)
        factor_1 = capture.items.float(g.SplineParameter().o.factor, "Factor")
        curve_to_mesh = capture.o.geometry >> g.CurveToMesh()
        edge_paths_to_selection = g.EdgePathsToSelection(start_vertices=selection, next_vertex_index=shortest_edge_paths.o.next_vertex_index)
        separate_geometry = g.SeparateGeometry.edge(edge, edge_paths_to_selection)
        for_each = g.ForEachGeometryElementZone(geometry=separate_geometry.o.selection)
        max = for_each.generated_items.float(name="Max")
        vector_math = g.AttributeStatistic.point.vector(for_each.input.o.element, attribute=g.Position()).o.mean.distance(g.Position())
        attribute_statistic = g.AttributeStatistic.point.float(curve_to_mesh, vector_math < 0.01, factor_1.output)
        for_each.input.o.element >> for_each.generation.input
        attribute_statistic.o.max >> max.input
        switch = merged.switch.float(factor_1.output, g.SampleIndex.point.float(for_each.generation.output, max.output, g.Index()))
        capture_1 = g.CaptureAttribute.point(geometry=merged.switch.geometry(curve_to_mesh, separate_geometry.o.selection))
        total_cost_1 = capture_1.items.float(shortest_edge_paths.o.total_cost, "Total Cost")
        factor_2 = capture_1.items.float(switch, "Factor")

        capture_1.o.geometry >> edge_1
        total_cost_1.output >> total_cost
        factor_2.output >> factor

ASSET = OShortestPaths

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "925722af-3fbd-4bb1-8247-dfe9a1ecd480",
}
