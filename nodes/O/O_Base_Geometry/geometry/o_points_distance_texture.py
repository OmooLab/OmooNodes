from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OPointsDistanceTexture(CustomGeometryGroup):
    _name = "O Points Distance Texture"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        points = tree.inputs.geometry("Points")
        radius_offset = tree.inputs.float("Radius Offset", 0.0, min_value=0.0, subtype="DISTANCE")
        value = tree.outputs.float("Value")

        position = g.Position()
        sample_nearest = g.SampleNearest.point(points)
        (
            g.SampleIndex.point.vector(points, position, sample_nearest).o.value.distance(position) - g.SampleIndex.point.float(points, radius_offset, sample_nearest)
            >> value
        )

ASSET = OPointsDistanceTexture

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
