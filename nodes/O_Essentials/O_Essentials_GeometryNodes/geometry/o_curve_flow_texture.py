from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_edge_to_curve import OEdgeToCurve
from .o_resample_edge import OResampleEdge
from .o_smooth import OSmooth


class OCurveFlowTexture(CustomGeometryGroup):
    _name = "O Curve Flow Texture"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        curve_edge = tree.inputs.geometry("Curve (Edge)")
        strength = tree.inputs.float("Strength", 1.0, min_value=0.0, max_value=100.0)
        reverse = tree.inputs.boolean("Reverse", False)
        normal_twist_tangent = tree.inputs.vector("Normal/Twist/Tangent", (0.0, 0.0, 1.0), min_value=-1.0, max_value=1.0)
        radius = tree.inputs.float("Radius", 0.0, min_value=0.0, max_value=1.0, subtype="DISTANCE")
        with tree.inputs.panel("Options", default_closed=True):
            resample_length = tree.inputs.float("Resample Length", 0.1, min_value=0.01, max_value=1.0, subtype="DISTANCE")
            smooth_iterations = tree.inputs.integer("Smooth Iterations", 10, description="How many times to blur the values for all elements", min_value=1, max_value=10)
            smooth = tree.inputs.float("Smooth", 1.0, description="Relative mix weight of neighboring elements", min_value=0.0, max_value=1.0, subtype="FACTOR")
        vector = tree.outputs.vector("Vector")

        o_smooth = OSmooth(Geometry=OResampleEdge(Edge=curve_edge, Length=resample_length), Iterations=smooth_iterations, **{"Pin Boundary": 0.9999}, Weight=smooth)
        o_edge_to_curve = OEdgeToCurve(Edge=o_smooth)
        position = g.Position()
        capture = g.CaptureAttribute.point(geometry=reverse.switch.geometry(o_edge_to_curve, g.ReverseCurve(curve=o_edge_to_curve)))
        tangent = capture.items.vector(g.CurveTangent(), "Tangent")
        radius_1 = capture.items.float(g.Radius(), "Radius")
        curve_to_mesh = capture.o.geometry >> g.CurveToMesh()
        geometry_proximity = g.GeometryProximity(target=curve_to_mesh, source_position=position, target_element="EDGES")
        sample_nearest = g.SampleNearest.edge(curve_to_mesh, position)
        sample_index = g.SampleIndex.edge.vector(curve_to_mesh, tangent.output, sample_nearest)
        math_1 = geometry_proximity.o.distance - (radius + g.SampleIndex.edge.float(curve_to_mesh, radius_1.output, sample_nearest))
        vector_math = geometry_proximity.o.position - position
        vector_math_1 = vector_math.cross(sample_index) * normal_twist_tangent.y + sample_index.o.value * normal_twist_tangent.z
        (
            (vector_math * normal_twist_tangent.x + vector_math_1).normalize() * (strength / (math_1.max(0.0) ** 2.0 + 1.0))
            >> vector
        )

ASSET = OCurveFlowTexture

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
