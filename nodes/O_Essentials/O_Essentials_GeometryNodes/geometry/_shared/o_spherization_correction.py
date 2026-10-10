# Node group "O Spherization Correction" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
# Shared by several assets, which import it; not an asset itself.
from bpy.types import GeometryNodeTree
from nodebpy import TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OSpherizationCorrection(CustomGeometryGroup):
    _name = "O Spherization Correction"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        value = tree.inputs.float("Value", 0.5, min_value=-10000.0, max_value=10000.0)
        a = tree.inputs.float("A", 0.5, min_value=-10000.0, max_value=10000.0)
        b = tree.inputs.float("B", 0.5, min_value=-10000.0, max_value=10000.0)
        value_1 = tree.outputs.float("Value")

        math_1 = a ** 2.0
        math_2 = b ** 2.0
        (1.0 - (math_1 + math_2) / 2.0 + math_1 * math_2 / 3.0).sqrt() * value >> value_1
