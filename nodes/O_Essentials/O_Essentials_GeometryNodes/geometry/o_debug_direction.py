from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class ODebugDirection(CustomGeometryGroup):
    _name = "O Debug Direction"
    _color_tag = "OUTPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        direction = tree.inputs.vector("Direction", (0.0, 0.0, 0.0), hide_value=True, default_input="NORMAL")
        menu = tree.inputs.menu("Menu", "Point", optional_label=True)
        normalize = tree.inputs.boolean("Normalize", True)
        size = tree.inputs.float("Size", 1.0, min_value=0.1, max_value=2.0, subtype="FACTOR")
        debug = tree.outputs.geometry("Debug")
        direction_1 = tree.outputs.vector("Direction")

        capture = g.CaptureAttribute.point(geometry=geometry)
        vector = capture.items.vector(direction, "Vector")
        capture_1 = g.CaptureAttribute.corner(geometry=capture.o.geometry)
        vector_1 = capture_1.items.vector(direction, "Vector")
        menu_switch = g.MenuSwitch.integer(menu, {"Point": 0, "Face Corner": 1})
        index_switch = g.IndexSwitch.vector(menu_switch.o.output, (vector.output, vector_1.output))
        math_1 = size * g.Radius()
        separate_components = capture_1.o.geometry >> g.SeparateComponents()
        instances_to_points = g.InstancesToPoints(instances=separate_components.o.instances, radius=0.1)
        separate_components_1 = g.SeparateComponents(geometry=geometry)
        set_shade_smooth = g.SetShadeSmooth.face(g.Cube(size=(0.2, 0.2, 0.2)))
        mesh_to_points = (
            g.IndexSwitch.geometry(menu_switch.o.output, (separate_components.o.mesh, g.SplitEdges(mesh=separate_components.o.mesh)))
            >> g.MeshToPoints(radius=0.1)
        )
        join_geometry = g.JoinGeometry(geometry=(mesh_to_points, g.CurveToPoints.evaluated(separate_components.o.curve), separate_components.o.point_cloud, instances_to_points))
        set_point_radius = g.SetPointRadius(points=join_geometry, radius=0.1)
        set_shade_smooth_1 = (
            g.Cylinder(vertices=3, radius=0.04)
            >> g.TransformGeometry(translation=(0.0, 0.0, 1.0))
            >> g.SetShadeSmooth.face()
        )
        switch = normalize.switch.vector(index_switch.o.output * size, index_switch.o.output.normalize())
        align_rotation_to_vector = g.AlignRotationToVector(vector=switch)
        instance_on_points = g.InstanceOnPoints(points=set_point_radius, instance=set_shade_smooth, rotation=align_rotation_to_vector, scale=math_1)
        instance_on_points_1 = g.InstanceOnPoints(points=set_point_radius, instance=set_shade_smooth_1, rotation=align_rotation_to_vector, scale=g.CombineXYZ(x=math_1, y=math_1, z=switch.length() * math_1))
        join_geometry_1 = g.JoinGeometry(geometry=(separate_components_1.o.mesh, separate_components_1.o.curve, instance_on_points, instance_on_points_1))

        join_geometry_1 >> debug
        index_switch >> direction_1

ASSET = ODebugDirection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "3aee6aa4-2dd5-4adb-9bed-3676454cdeff",
}
