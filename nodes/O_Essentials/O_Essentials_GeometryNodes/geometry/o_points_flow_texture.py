# Node-group asset "O Points Flow Texture" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OPointsFlowTexture(CustomGeometryGroup):
    _name = "O Points Flow Texture"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        points = tree.inputs.geometry("Points")
        strength = tree.inputs.float("Strength", 1.0, min_value=0.0, max_value=100.0)
        reverse = tree.inputs.boolean("Reverse", False)
        radius = tree.inputs.float("Radius", 0.0, min_value=0.0, max_value=10.0, subtype="DISTANCE")
        vector = tree.outputs.vector("Vector")

        position = g.Position()
        separate_components = g.SeparateComponents(geometry=points)
        join_geometry = g.JoinGeometry(geometry=(separate_components >> g.MeshToPoints(), separate_components.o.point_cloud))
        repeat_zone = g.RepeatZone(g.DomainSize(geometry=join_geometry, component="POINTCLOUD").o.point_count)
        iteration = repeat_zone.items.integer(name="Iteration")
        flow = repeat_zone.items.vector(name="Flow")
        math_1 = radius + g.SampleIndex.point.float(join_geometry, g.Radius(), iteration.current, clamp=True)
        sample_index = g.SampleIndex.point.vector(join_geometry, g.Position(), iteration.current, clamp=True)
        vector_math = (sample_index.o.value - position).normalize() * (strength / ((sample_index.o.value.distance(position) - math_1).max(0.0) ** 2.0 + 1.0))
        iteration.current + 1.0 >> iteration.next
        flow.current + vector_math * reverse.switch.float(1.0, -1.0) >> flow.next

        flow.result >> vector

ASSET = OPointsFlowTexture

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
