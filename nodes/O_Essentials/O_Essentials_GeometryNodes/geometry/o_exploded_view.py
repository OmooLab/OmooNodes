from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OExplodedView(CustomGeometryGroup):
    _name = "O Exploded View"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        scale = tree.inputs.float("Scale", 1.0, min_value=0.0, max_value=10.0, subtype="DISTANCE")
        group_id = tree.inputs.integer("Group ID", -123456, hide_value=True)
        geometry_1 = tree.outputs.geometry("Geometry")

        _group = g.Group()
        switch = g.Compare.integer.equal(group_id, -123456).o.result.switch.integer(group_id, g.MeshIsland().o.island_index)
        for_each = g.ForEachGeometryElementZone.instance(geometry=g.SplitToInstances.face(geometry, group_id=switch).o.instances)
        vector = for_each.generated_items.vector(name="Vector", domain="INSTANCE")
        capture = g.CaptureAttribute.instance(geometry=for_each.input.o.element)
        vector_1 = capture.items.vector(name="Vector")
        capture.o.geometry >> for_each.generation.input
        vector_1.output >> vector.input
        vector_math = vector.output.instance.total() / g.DomainSize(geometry=for_each.generation.output, component="INSTANCES").o.instance_count
        set_position = g.SetPosition(geometry=for_each.generation.output, offset=(vector.output - vector_math).normalize() * scale)

        set_position >> geometry_1

ASSET = OExplodedView

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
