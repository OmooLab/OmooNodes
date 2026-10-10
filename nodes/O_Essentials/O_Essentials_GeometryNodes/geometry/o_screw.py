# Node-group asset "O Screw" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OScrew(CustomGeometryGroup):
    _name = "O Screw"
    _color_tag = "GEOMETRY"
    _tree_properties = {"is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        menu = tree.inputs.menu("Menu", "Vertices", expanded=True, optional_label=True)
        angle = tree.inputs.float("Angle", 6.2831854820251465, description="Angle of revolution.", subtype="ANGLE")
        screw = tree.inputs.float("Screw", 1.0, description="Offset the revolution along its axis.", min_value=0.0, max_value=3.402820018375656e+38, subtype="DISTANCE")
        iterations = tree.inputs.integer("Iterations", 1, description="Number of times to apply the screw operation.", min_value=1, max_value=10)
        steps = tree.inputs.integer("Steps", 16, description="Number of steps in the revolution.", min_value=1, max_value=32)
        with tree.inputs.panel("Options", default_closed=True):
            center = tree.inputs.vector("Center", (0.0, 0.0, 0.0))
            axis = tree.inputs.vector("Axis", (0.0, 0.0, 1.0), description="Screw axis.", subtype="XYZ")
        mesh_1 = tree.outputs.geometry("Mesh")

        domain_size = g.DomainSize(geometry=mesh)
        math_1 = g.Math.multiply(iterations, steps)
        math_2 = g.Math.snap(g.Index().o.index / domain_size.o.point_count, 1.0)
        repeat_zone = g.RepeatZone(math_1)
        geometry = repeat_zone.items.geometry(mesh, "Geometry")
        top = repeat_zone.items.boolean(True, "Top")
        side = repeat_zone.items.boolean(name="Side")
        repeat_zone_1 = g.RepeatZone(math_1)
        geometry_1 = repeat_zone_1.items.geometry(mesh, "Geometry")
        top_1 = repeat_zone_1.items.boolean(True, "Top")
        side_1 = repeat_zone_1.items.boolean(name="Side")
        sample_index = g.SampleIndex.point.vector(mesh, g.Position(), g.Math.truncated_modulo(g.Index(), domain_size.o.point_count), clamp=True)
        vector = g.Vector(vector=(0.0, 0.0, 1.0))
        extrude_mesh = g.ExtrudeMesh.vertices(geometry.current, top.current, vector)
        extrude_mesh_1 = g.ExtrudeMesh.edges(geometry_1.current, top_1.current, vector)
        extrude_mesh >> geometry.next
        extrude_mesh.o.top >> top.next
        (side.current | extrude_mesh.o.side) >> side.next
        extrude_mesh_1 >> geometry_1.next
        extrude_mesh_1.o.top >> top_1.next
        (side_1.current | extrude_mesh_1.o.side) >> side_1.next
        vector_rotate = g.VectorRotate(vector=sample_index, center=center, axis=axis, angle=math_2.o.value * (angle / steps))
        (
            g.MenuSwitch.geometry(menu, {"Vertices": (geometry.result >> g.SeparateGeometry.edge(selection=side.result)).o.selection, "Edges": geometry_1.result >> g.SeparateGeometry.face(selection=side_1.result) >> g.FlipFaces()})
            >> g.SetPosition(position=g.VectorMath.multiply(axis.normalize() * screw / steps, math_2).o.vector + vector_rotate)
            >> mesh_1
        )

ASSET = OScrew

ASSET_METADATA = {
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
