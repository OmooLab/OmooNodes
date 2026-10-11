from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_center import OCenter
from .o_geometry_info import OGeometryInfo


class OMatchSize(CustomGeometryGroup):
    _name = "O Match Size"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        size = tree.inputs.float("Size", 1.0, min_value=0.1, max_value=10.0, subtype="DISTANCE")
        center = tree.inputs.vector("Center", (0.0, 0.0, 0.0), min_value=-1.0, max_value=1.0, subtype="FACTOR")
        geometry_1 = tree.outputs.geometry("Geometry")

        (
            OCenter(Geometry=geometry, Center=center)
            >> g.TransformGeometry(scale=size / OGeometryInfo(Geometry=geometry).o.size)
            >> geometry_1
        )

ASSET = OMatchSize

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
