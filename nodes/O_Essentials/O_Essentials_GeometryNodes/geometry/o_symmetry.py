# Node-group asset "O Symmetry" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OSymmetry(CustomGeometryGroup):
    _name = "O Symmetry"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        menu = tree.inputs.menu("Menu", "Mirror", expanded=True, optional_label=True)
        menu_1 = tree.inputs.menu("Menu", "X", expanded=True, optional_label=True)
        radial = tree.inputs.integer("Radial", 3, min_value=3, max_value=8)
        geometry_1 = tree.outputs.geometry("Geometry")

        menu_switch = g.MenuSwitch.integer(menu_1, {"X": 0, "Y": 1, "Z": 2})
        repeat_zone = g.RepeatZone(radial)
        output = repeat_zone.items.geometry(name="Output")
        math_1 = 6.2831854820251465 / radial * repeat_zone.iteration
        separate_components = g.SeparateComponents(geometry=geometry)
        join_geometry = g.JoinGeometry(geometry=(separate_components >> g.FlipFaces(), separate_components.o.curve, separate_components.o.grease_pencil, separate_components.o.point_cloud, separate_components.o.volume, separate_components.o.instances))
        index_switch = g.IndexSwitch.geometry(menu_switch.o.output, (g.TransformGeometry(geometry=join_geometry, scale=(-1.0, 1.0, 1.0)), g.TransformGeometry(geometry=join_geometry, scale=(1.0, -1.0, 1.0)), g.TransformGeometry(geometry=join_geometry, scale=(1.0, 1.0, -1.0))))
        join_geometry_1 = g.JoinGeometry(geometry=(g.TransformGeometry(geometry=join_geometry, scale=(1.0, -1.0, 1.0)), geometry))
        join_geometry_2 = g.JoinGeometry(geometry=(g.TransformGeometry(geometry=join_geometry, scale=(-1.0, 1.0, 1.0)), geometry))
        join_geometry_3 = g.JoinGeometry(geometry=(g.TransformGeometry(geometry=join_geometry, scale=(-1.0, 1.0, 1.0)), geometry))
        index_switch_1 = g.IndexSwitch.geometry(menu_switch.o.output, (g.TransformGeometry(geometry=join_geometry_1, rotation=g.CombineXYZ(x=math_1)), g.TransformGeometry(geometry=join_geometry_2, rotation=g.CombineXYZ(y=math_1)), g.TransformGeometry(geometry=join_geometry_3, rotation=g.CombineXYZ(z=math_1))))
        g.JoinGeometry(geometry=(index_switch_1, output.current)) >> output.next
        (
            g.MenuSwitch.geometry(menu, {"Mirror": g.JoinGeometry(geometry=(index_switch, geometry)), "Radial": output.result})
            >> geometry_1
        )

ASSET = OSymmetry

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
