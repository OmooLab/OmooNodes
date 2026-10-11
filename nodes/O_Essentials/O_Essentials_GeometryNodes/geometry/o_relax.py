from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_is_edge_boundary import OIsEdgeBoundary
from .o_project import OProject


class ORelax(CustomGeometryGroup):
    _name = "O Relax"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        iterations = tree.inputs.integer("Iterations", 5, description="How many times to blur the values for all elements", min_value=1, max_value=20)
        with tree.inputs.panel("Options", default_closed=True):
            weight = tree.inputs.float("Weight", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
            positive_weight = tree.inputs.float("Positive Weight", 1.0, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
            negative_weight = tree.inputs.float("Negative Weight", 1.0, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
            max_distance = tree.inputs.float("Max Distance", 0.1, min_value=0.0, max_value=1.0, subtype="DISTANCE")
            source = tree.inputs.menu("Source", "Original", expanded=True, optional_label=True)
            source_1 = tree.inputs.geometry("Source")
            mesh_island = tree.inputs.integer("Mesh Island", 0, hide_value=True)
            source_mesh_island = tree.inputs.integer("Source Mesh Island", 0, description="Splits the faces of the input mesh into groups which can be sampled individually", hide_value=True)
        geometry_1 = tree.outputs.geometry("Geometry")

        menu_switch = g.MenuSwitch.integer(source, {"Original": 0, "Custom": 1})
        index_switch = g.IndexSwitch.integer(menu_switch.o.output, (g.MeshIsland().o.island_index, source_mesh_island))
        index_switch_1 = g.IndexSwitch.integer(menu_switch.o.output, (g.MeshIsland().o.island_index, mesh_island))
        split_to_instances = g.SplitToInstances.face(geometry, group_id=index_switch_1)
        for_each = g.ForEachGeometryElementZone.instance(geometry=split_to_instances.o.instances)
        group_id = for_each.items.integer(split_to_instances.o.group_id, "Group ID")
        repeat_zone = g.RepeatZone(iterations)
        geometry_2 = repeat_zone.items.geometry(g.RealizeInstances(geometry=for_each.input.o.element), "Geometry")
        separate_geometry = g.SeparateGeometry.point(geometry_2.current, OIsEdgeBoundary().o.is_edge_boundary.point.evaluate())
        sample_index = g.SampleIndex.point.vector(separate_geometry.o.selection, g.Position().o.position.blur(weight=0.5), g.SampleNearest.point(separate_geometry.o.selection))
        separate_geometry_1 = (
            g.IndexSwitch.geometry(menu_switch.o.output, (geometry, source_1))
            >> g.SeparateGeometry.face(selection=g.Compare.integer.equal(group_id.output, index_switch))
        )
        switch = OIsEdgeBoundary().o.is_edge_boundary.switch.vector(g.Position().o.position.blur(), sample_index)
        mix = g.Mix.vector(weight * g.Normal().o.normal.blur(10).length(), g.Position(), switch, clamp_factor=True)
        set_position = g.SetPosition(geometry=geometry_2.current, selection=selection, position=mix.o.result_vector)
        o_project = OProject(Geometry=set_position, Selection=selection, Source=separate_geometry_1.o.selection, **{"Positive Weight": positive_weight, "Negative Weight": negative_weight, "Max Distance": max_distance, "Radius Offset": 0.0}, Custom=(0.0, 0.0, 0.0), **{"Normal Smooth": 0}, _named_links=[("Menu", "Project"), ("Menu", "Source")])
        o_project >> geometry_2.next
        geometry_2.result >> for_each.generation.input

        for_each.generation.output >> geometry_1

ASSET = ORelax

ASSET_METADATA = {
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
