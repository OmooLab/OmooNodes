from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OGrid(CustomGeometryGroup):
    _name = "O Grid"
    _color_tag = "GEOMETRY"
    _tree_properties = {"description": "Build an aspect-adaptive grid with optional centered thickness.", "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        size_x = tree.inputs.float("Size X", 1.0, min_value=0.0, structure_type="SINGLE", subtype="DISTANCE", force_non_field=True)
        size_y = tree.inputs.float("Size Y", 1.0, min_value=0.0, structure_type="SINGLE", subtype="DISTANCE", force_non_field=True)
        subdivide = tree.inputs.integer("Subdivide", 0, description="Increase mesh density to represent finer shapes. Higher levels create more vertices and require more processing time.", min_value=0, max_value=8, structure_type="SINGLE", force_non_field=True)
        thickness = tree.inputs.float("Thickness", 0.0, min_value=0.0, max_value=10000.0, structure_type="SINGLE", subtype="DISTANCE", force_non_field=True)
        geometry = tree.outputs.geometry("Geometry")
        uv_map = tree.outputs.vector("UV Map", attribute_domain="CORNER")

        segments = 2.0 ** subdivide
        segments_x = (segments * (size_x / size_y).max(1.0)).round()
        segments_y = (segments * (size_y / size_x).max(1.0)).round()
        segment_size = (size_x / segments_x * (size_y / segments_y)).sqrt()
        segments_z = (thickness / segment_size).round().max(3.0)
        grid = g.Grid(size_x=size_x, size_y=size_y, vertices_x=segments_x + 1.0, vertices_y=segments_y + 1.0)
        solid = g.Cube(
            size=g.CombineXYZ(x=size_x, y=size_y, z=thickness),
            vertices_x=segments_x + 1.0, vertices_y=segments_y + 1.0, vertices_z=segments_z + 1.0,
        )
        position = g.Position().o.position
        projected_uv = g.CombineXYZ(x=position.x / size_x + 0.5, y=position.y / size_y + 0.5)
        has_thickness = thickness > 0.0
        uv = has_thickness.switch.vector(grid.o.uv_map, projected_uv)
        (
            has_thickness.switch.geometry(grid, solid)
            >> g.StoreNamedAttribute.corner.vector_2d(name="UVMap", value=uv)
            >> geometry
        )
        uv >> uv_map

ASSET = OGrid

ASSET_METADATA = {
    "description": "Build an aspect-adaptive grid with optional centered thickness.",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
