from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OExplodedView(CustomGeometryGroup):
    _name = "O Exploded View"
    _color_tag = "GEOMETRY"
    _tree_properties = {"is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        scale = tree.inputs.float("Scale", 1.0, min_value=0.0, max_value=10.0, subtype="DISTANCE")
        group_id = tree.inputs.integer("Group ID", -123456, hide_value=True, hide_in_modifier=True)
        geometry_1 = tree.outputs.geometry("Geometry")

        part_id = g.Compare.integer.equal(group_id, -123456).o.result.switch.integer(group_id, g.MeshIsland().o.island_index)
        parts = g.SplitToInstances.face(geometry, group_id=part_id).o.instances
        for_each = g.ForEachGeometryElementZone.instance(geometry=parts)
        part = for_each.input.o.element
        center = for_each.generated_items.vector(name="Center", domain="INSTANCE")
        # Measure the realized part while keeping the original instance in the result.
        bounds = g.BoundingBox(geometry=g.RealizeInstances(geometry=part))
        (bounds.o.min + bounds.o.max) * 0.5 >> center.input
        part >> for_each.generation.input

        instances = for_each.generation.output
        instance_count = g.DomainSize(geometry=instances, component="INSTANCES").o.instance_count
        average_center = center.output.instance.total() / instance_count
        offset = (center.output - average_center).normalize() * scale
        g.SetPosition(geometry=instances, offset=offset) >> geometry_1

ASSET = OExplodedView

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
