from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class OMaskByDistance(CustomGeometryGroup):
    _name = "O Mask by Distance"
    _color_tag = "CONVERTER"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        source = tree.inputs.geometry("Source")
        max_distance = tree.inputs.float("Max Distance", 1.0, min_value=0.0, max_value=10000.0)
        geometry_1 = tree.outputs.geometry("Geometry")
        mask = tree.outputs.float("Mask")
        distance = tree.outputs.float("Distance")

        geometry_proximity = g.GeometryProximity(target=source, target_element="POINTS")
        (
            (geometry_proximity.o.is_valid & max_distance).switch.float(true=geometry_proximity.o.distance.map_range(from_max=max_distance, to_min=1.0, to_max=0.0))
            >> mask
        )

        geometry >> geometry_1
        geometry_proximity.o.distance >> distance

ASSET = OMaskByDistance

ASSET_METADATA = {
    "catalog_id": "304de8ab-a7d3-4df3-b6b2-4674d8814339",
}
