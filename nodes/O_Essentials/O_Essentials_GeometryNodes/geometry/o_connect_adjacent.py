from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_nearby_selection import ONearbySelection


class OConnectAdjacent(CustomGeometryGroup):
    _name = "O Connect Adjacent"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry", description="Geometry whose elements are iterated over")
        selection = tree.inputs.boolean("Selection", True, description="Selection on the iteration domain", hide_value=True, hide_in_modifier=True)
        range = tree.inputs.float("Range", 0.5, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        geometry_1 = tree.outputs.geometry("Geometry")

        for_each = g.ForEachGeometryElementZone(geometry=geometry, selection=selection)
        separate_geometry = g.SeparateGeometry.point(geometry, ONearbySelection(**{"Point Index": for_each.index}, Range=range))
        for_each_1 = g.ForEachGeometryElementZone(geometry=separate_geometry.o.selection)
        mean = for_each_1.items.vector(g.AttributeStatistic.point.vector(for_each.input.o.element, attribute=g.Position()).o.mean, "Mean")
        mesh_line = g.MeshLine.end_points(2, g.AttributeStatistic.point.vector(for_each_1.input.o.element, attribute=g.Position()).o.mean, mean.output)
        mesh_line >> for_each_1.generation.input
        for_each_1.generation.output >> for_each.generation.input
        merge_by_distance = g.MergeByDistance(geometry=for_each.generation.output, distance=0.0001)

        merge_by_distance >> geometry_1

ASSET = OConnectAdjacent

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
