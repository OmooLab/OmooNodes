from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OPickInstance(CustomGeometryGroup):
    _name = "O Pick Instance"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        instance = tree.outputs.geometry("Instance")

        separate_components = g.SeparateComponents(geometry=geometry)
        compare = g.DomainSize(geometry=separate_components.o.grease_pencil, component="GREASEPENCIL").o.layer_count > 0
        compare_1 = g.DomainSize(geometry=separate_components.o.point_cloud, component="POINTCLOUD").o.layer_count > 0
        switch = (g.DomainSize(geometry=separate_components.o.mesh).o.point_count > 0).switch.geometry(true=g.GeometryToInstance(separate_components.o.mesh))
        switch_1 = (g.DomainSize(geometry=separate_components.o.curve, component="CURVE").o.point_count > 0).switch.geometry(true=g.GeometryToInstance(separate_components.o.curve))
        join_geometry = g.JoinGeometry(geometry=(switch, switch_1, compare.switch.geometry(true=g.GeometryToInstance(separate_components.o.grease_pencil)), compare_1.switch.geometry(true=g.GeometryToInstance(separate_components.o.point_cloud)), separate_components.o.instances))

        join_geometry >> instance

ASSET = OPickInstance

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
