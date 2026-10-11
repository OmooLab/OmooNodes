from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OCenter(CustomGeometryGroup):
    _name = "O Center"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        center = tree.inputs.vector("Center", (0.0, 0.0, 0.0), min_value=-1.0, max_value=1.0, subtype="FACTOR")
        geometry_1 = tree.outputs.geometry("Geometry")

        bounding_box = g.BoundingBox(geometry=geometry)
        vector_math = (bounding_box.o.min + bounding_box.o.max) * -0.5 + (bounding_box.o.max - bounding_box.o.min) * 0.5 * center
        geometry >> g.TransformGeometry(translation=vector_math) >> geometry_1

ASSET = OCenter

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
