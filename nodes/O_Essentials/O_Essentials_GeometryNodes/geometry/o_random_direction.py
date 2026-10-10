from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup


class ORandomDirection(CustomGeometryGroup):
    _name = "O Random Direction"
    _color_tag = "VECTOR"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        direction = tree.inputs.vector("Direction", (0.0, 0.0, 1.0), min_value=-10000.0, max_value=10000.0)
        spread = tree.inputs.float("Spread", 0.5, min_value=0.0, max_value=1.0, structure_type="SINGLE", subtype="FACTOR", force_non_field=True)
        axial_spread = tree.inputs.float("Axial Spread", 1.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        id = tree.inputs.integer("ID", 0, hide_value=True, default_input="ID_OR_INDEX")
        seed = tree.inputs.integer("Seed", 0, structure_type="SINGLE", force_non_field=True)
        direction_1 = tree.outputs.vector("Direction")
        rotation = tree.outputs.rotation("Rotation")

        math_1 = g.RandomValue.float(-3.1415927, 3.14159, id, seed).o.value * axial_spread
        vector_math = g.RandomValue.vector((-1.0, -1.0, -1.0), (1.0, 1.0, 1.0), id, seed).o.value.normalize() * (spread * 2.0)
        vector_math_1 = (direction.normalize() + vector_math).normalize() * direction.length()
        (
            g.AxesToRotation(primary_axis=vector_math_1).o.rotation.rotate(g.CombineXYZ(z=math_1), rotation_space="LOCAL")
            >> rotation
        )

        vector_math_1 >> direction_1

ASSET = ORandomDirection

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
