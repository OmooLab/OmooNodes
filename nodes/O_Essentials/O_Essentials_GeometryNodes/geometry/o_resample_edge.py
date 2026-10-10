from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_curve_to_edge import OCurveToEdge
from .o_edge_to_curve import OEdgeToCurve


class OResampleEdge(CustomGeometryGroup):
    _name = "O Resample Edge"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry("Edge")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        length = tree.inputs.float("Length", 0.1, min_value=0.01, subtype="DISTANCE")
        with tree.inputs.panel("Options", default_closed=True):
            _merge_distance = tree.inputs.float("Merge Distance", 0.001, min_value=0.0, subtype="DISTANCE")
        edge_1 = tree.outputs.geometry("Edge")

        capture = g.CaptureAttribute.point(geometry=edge)
        selection_1 = capture.items.boolean(selection, "Selection")
        resample_curve = (
            OEdgeToCurve(Edge=capture.o.geometry)
            >> g.ResampleCurve(selection=selection_1.output, length=length, mode="Length", keep_last_segment=True)
        )
        OCurveToEdge(Curve=resample_curve) >> edge_1

ASSET = OResampleEdge

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "925722af-3fbd-4bb1-8247-dfe9a1ecd480",
}
