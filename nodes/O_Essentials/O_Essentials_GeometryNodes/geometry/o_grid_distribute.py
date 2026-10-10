# Node-group asset "O Grid Distribute" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_random_selection import ORandomSelection


class OGridDistribute(CustomGeometryGroup):
    _name = "O Grid Distribute"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry("Mesh")
        spacing = tree.inputs.float("Spacing", 0.20000000298023224, min_value=0.05000000074505806, subtype="DISTANCE")
        radius = tree.inputs.float("Radius", 1.0, min_value=0.10000000149011612, max_value=2.0)
        random = tree.inputs.float("Random", 0.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Options", default_closed=True):
            random_selection = tree.inputs.float("Random Selection", 1.0, description="Number of points to sample per unit volume", min_value=0.0, max_value=1.0, subtype="FACTOR")
            relax_iterations = tree.inputs.integer("Relax Iterations", 5, min_value=1, max_value=10)
            seed = tree.inputs.integer("Seed", 0, min_value=-10000, max_value=10000)
        points = tree.outputs.geometry("Points")

        flip_faces = g.FlipFaces(mesh=mesh)
        geometry_proximity = g.GeometryProximity(target=flip_faces)
        math_1 = spacing * (random * 0.5)
        sample_nearest_surface = g.SampleNearestSurface.vector(flip_faces, g.Normal().o.normal)
        raycast = g.Raycast.vector(flip_faces, (0.0, 0.0, 0.0), ray_direction=sample_nearest_surface.o.value, ray_length=10.0)
        compare = g.Compare(a=sample_nearest_surface.o.value, b=raycast.o.hit_normal, data_type="VECTOR", mode="DOT_PRODUCT", c=0.0)
        separate_geometry = (
            mesh
            >> g.MeshToVolume(voxel_size=spacing, interior_band_width=spacing * 5.0, resolution_mode="Size")
            >> g.DistributePointsInVolume(spacing=spacing, mode="Grid")
            >> g.SetPointRadius(radius=spacing * radius * 0.5)
            >> g.SetPosition(offset=g.RandomValue.vector(math_1 * -1.0, math_1, seed=seed))
            >> g.SeparateGeometry.point(selection=ORandomSelection(Factor=random_selection, Seed=seed))
        )
        repeat_zone = g.RepeatZone((relax_iterations * random).ceil())
        geometry = repeat_zone.items.geometry(separate_geometry.o.selection, "Geometry")
        switch = compare.o.result.switch.float(1.0, -1.0)
        math_2 = spacing * 0.5 - geometry_proximity.o.distance * switch
        vector_math = g.Position().o.position.point.at(g.IndexOfNearest().o.index) - g.Position()
        math_3 = spacing - vector_math.length()
        set_position = g.SetPosition(geometry=geometry.current, offset=(math_3 > 0.0).switch.vector((0.0, 0.0, 0.0), vector_math.normalize() * math_3 * -1.0))
        switch_1 = (math_2 > 0.0).switch.vector((0.0, 0.0, 0.0), (g.Position().o.position - geometry_proximity.o.position).normalize() * switch * math_2)
        set_position_1 = g.SetPosition(geometry=set_position, offset=(geometry_proximity.o.distance < 1.0).switch.vector((0.0, 0.0, 0.0), switch_1))
        set_position_1 >> geometry.next

        geometry.result >> points

ASSET = OGridDistribute

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
