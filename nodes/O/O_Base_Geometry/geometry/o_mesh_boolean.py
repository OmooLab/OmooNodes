from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_mask_by_selection import OMaskBySelection
from .o_pick_instance import OPickInstance
from .o_smooth import OSmooth
from .o_smooth_attributes import OSmoothAttributes
from .o_transfer_attributes import OTransferAttributes
from .o_voxel_remesh import OVoxelRemesh


class OMeshBoolean(CustomGeometryGroup):
    _name = "O Mesh Boolean"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        a = tree.inputs.geometry("A")
        b = tree.inputs.geometry("B")
        mode = tree.inputs.menu("Mode", "Union", optional_label=True)
        method = tree.inputs.menu("Method", "Manifold", optional_label=True)
        with tree.inputs.panel("Surface Attribute", default_closed=True):
            float = tree.inputs.string("Float", "", description="Separate with commas")
            integer = tree.inputs.string("Integer", "", description="Separate with commas")
            vector = tree.inputs.string("Vector", "", description="Separate with commas")
            color = tree.inputs.string("Color", "", description="Separate with commas")
        with tree.inputs.panel("Smooth Intersecting", default_closed=True):
            smooth_intersecting = tree.inputs.boolean("Smooth Intersecting", False, is_panel_toggle=True)
            max_distance = tree.inputs.float("Max Distance", 0.100000024, min_value=0.0, max_value=10000.0)
            iterations = tree.inputs.integer("Iterations", 10, description="How many times to blur the values for all elements", min_value=0, max_value=100)
        with tree.inputs.panel("Preview", default_closed=True):
            preview = tree.inputs.boolean("Preview", False, is_panel_toggle=True)
            resolution = tree.inputs.float("Resolution", 0.1, min_value=0.01, max_value=0.1)
            iterations_1 = tree.inputs.integer("Iterations", 1, description="How many times to blur the values for all elements", min_value=1, max_value=10)
        mesh = tree.outputs.geometry("Mesh")
        intersecting_edges = tree.outputs.boolean("Intersecting Edges")

        menu_switch = g.MenuSwitch.integer(mode, {"Intersect": 0, "Union": 1, "Difference": 2})
        menu_switch_1 = g.MenuSwitch.integer(method, {"Exact": 0, "Float": 1, "Manifold": 2})
        for_each = g.ForEachGeometryElementZone.instance(geometry=OPickInstance(Geometry=a))
        for_each_1 = g.ForEachGeometryElementZone.instance(geometry=OPickInstance(Geometry=b))
        o_transfer_attributes = OTransferAttributes(Mesh=g.RealizeInstances(geometry=for_each.input.o.element), Float=float, Integer=integer, Vector=vector, Color=color, on="Face Corner")
        g.GeometryToInstance(o_transfer_attributes) >> for_each.generation.input
        for_each_2 = g.ForEachGeometryElementZone.instance(geometry=for_each.generation.output)
        mesh_boolean = g.MeshBoolean(mesh_2=(for_each.generation.output,), operation="UNION", solver="MANIFOLD")
        o_transfer_attributes_1 = OTransferAttributes(Mesh=g.RealizeInstances(geometry=for_each_1.input.o.element), Float=float, Integer=integer, Vector=vector, Color=color, on="Face Corner")
        g.GeometryToInstance(o_transfer_attributes_1) >> for_each_1.generation.input
        for_each_3 = g.ForEachGeometryElementZone.instance(geometry=for_each_1.generation.output)
        join_geometry = g.JoinGeometry(geometry=(for_each.generation.output, for_each_1.generation.output))
        mesh_boolean_1 = g.MeshBoolean(mesh_2=(join_geometry,), operation="UNION", solver="MANIFOLD")
        mesh_boolean_2 = g.MeshBoolean(mesh_2=(join_geometry,), operation="UNION", solver="EXACT")
        index_switch = g.IndexSwitch.boolean(menu_switch_1.o.output, (mesh_boolean_2.o.intersecting_edges, False, mesh_boolean_1.o.intersecting_edges))
        index_switch_1 = g.IndexSwitch.geometry(menu_switch_1.o.output, (mesh_boolean_2, g.MeshBoolean(mesh_2=(join_geometry,), operation="UNION"), mesh_boolean_1))
        mesh_boolean_3 = g.MeshBoolean(mesh_2=(join_geometry,), operation="INTERSECT", solver="MANIFOLD")
        mesh_boolean_4 = g.MeshBoolean(mesh_2=(join_geometry,), operation="INTERSECT", solver="EXACT")
        index_switch_2 = g.IndexSwitch.boolean(menu_switch_1.o.output, (mesh_boolean_4.o.intersecting_edges, False, mesh_boolean_3.o.intersecting_edges))
        index_switch_3 = g.IndexSwitch.geometry(menu_switch_1.o.output, (mesh_boolean_4, g.MeshBoolean(mesh_2=(join_geometry,), operation="INTERSECT"), mesh_boolean_3))
        mesh_boolean_5 = g.MeshBoolean(mesh_2=(for_each_1.generation.output,), operation="UNION", solver="MANIFOLD")
        mesh_boolean_6 = (
            mesh_boolean
            >> g.MeshBoolean(mesh_2=(mesh_boolean_5,), solver="MANIFOLD")
        )
        boolean_math = mesh_boolean_6.o.intersecting_edges | (mesh_boolean.o.intersecting_edges | mesh_boolean_5.o.intersecting_edges)
        mesh_boolean_7 = g.MeshBoolean(mesh_1=g.MeshBoolean(mesh_2=(for_each.generation.output,), operation="UNION"), mesh_2=(g.MeshBoolean(mesh_2=(for_each_1.generation.output,), operation="UNION"),))
        mesh_boolean_8 = g.MeshBoolean(mesh_1=g.RealizeInstances(geometry=for_each.generation.output), mesh_2=(for_each_1.generation.output,), self_intersection=True, solver="EXACT")
        index_switch_4 = g.IndexSwitch.geometry(menu_switch_1.o.output, (mesh_boolean_8, mesh_boolean_7, mesh_boolean_6))
        index_switch_5 = g.IndexSwitch.geometry(menu_switch.o.output, (index_switch_3, index_switch_1, index_switch_4))
        index_switch_6 = g.IndexSwitch.boolean(menu_switch_1.o.output, (mesh_boolean_8.o.intersecting_edges, False, boolean_math))
        index_switch_7 = g.IndexSwitch.boolean(menu_switch.o.output, (index_switch_2, index_switch, index_switch_6))
        o_voxel_remesh = OVoxelRemesh(Mesh=g.RealizeInstances(geometry=for_each_2.input.o.element), Resolution=resolution, **{"Relax Iterations": iterations_1})
        g.GeometryToInstance(o_voxel_remesh) >> for_each_2.generation.input
        mesh_boolean_9 = g.MeshBoolean(mesh_2=(for_each_2.generation.output,), operation="UNION", solver="MANIFOLD")
        o_voxel_remesh_1 = OVoxelRemesh(Mesh=g.RealizeInstances(geometry=for_each_3.input.o.element), Resolution=resolution, **{"Relax Iterations": iterations_1})
        g.GeometryToInstance(o_voxel_remesh_1) >> for_each_3.generation.input
        join_geometry_1 = g.JoinGeometry(geometry=(for_each_2.generation.output, for_each_3.generation.output))
        mesh_boolean_10 = g.MeshBoolean(mesh_1=mesh_boolean_9, mesh_2=(for_each_3.generation.output,), solver="MANIFOLD")
        mesh_boolean_11 = g.MeshBoolean(mesh_2=(join_geometry_1,), operation="INTERSECT", solver="MANIFOLD")
        mesh_boolean_12 = g.MeshBoolean(mesh_2=(join_geometry_1,), operation="UNION", solver="MANIFOLD")
        index_switch_8 = g.IndexSwitch.geometry(menu_switch.o.output, (mesh_boolean_11, mesh_boolean_12, mesh_boolean_10))
        index_switch_9 = g.IndexSwitch.boolean(menu_switch.o.output, (mesh_boolean_11.o.intersecting_edges, mesh_boolean_12.o.intersecting_edges, mesh_boolean_10.o.intersecting_edges))
        switch = preview.switch.boolean(index_switch_7, index_switch_9)
        o_mask_by_selection = OMaskBySelection(Geometry=index_switch_5, Selection=switch, **{"Max Distance": max_distance, "Smooth Iterations": iterations})
        o_smooth_attributes = OSmoothAttributes(Mesh=o_mask_by_selection, Float=float, Vector=vector, Color=color, on="Face Corner", Iterations=iterations, Weight=o_mask_by_selection.o.mask)
        o_smooth = OSmooth(Geometry=o_smooth_attributes, Iterations=iterations, **{"Pin Sharp": 1.0, "Pin Boundary": 1.0}, Weight=o_mask_by_selection.o.mask)
        (
            preview.switch.geometry(smooth_intersecting.switch.geometry(o_mask_by_selection, o_smooth), index_switch_8)
            >> mesh
        )

        switch >> intersecting_edges

ASSET = OMeshBoolean

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
