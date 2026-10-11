from math import pi

from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from .o_is_edge_boundary import OIsEdgeBoundary


class OSharpen(CustomGeometryGroup):
    _name = "O Sharpen"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 220, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        iterations = tree.inputs.integer("Iterations", 5, min_value=1, max_value=20)
        pin_boundary = tree.inputs.float("Pin Boundary", 1.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Options", default_closed=True):
            weight = tree.inputs.float("Weight", 0.5, min_value=0.0, max_value=1.0, subtype="FACTOR")
            curvature_type = tree.inputs.menu("Curvature Type", "Mean")
            report = tree.inputs.menu("Report", "Smaller")
            sign = tree.inputs.menu("Sign", "Signed")
            independent = tree.inputs.boolean("Make Scale Independent", True)
            exponent = tree.inputs.float("Curvature Exponent", 1.0, min_value=0.0, max_value=10.0)
        output = tree.outputs.geometry("Geometry")

        boundary = OIsEdgeBoundary().o.is_edge_boundary.point.evaluate()
        degree = g.VertexNeighbors().o.vertex_count
        vertex = g.VertexOfCorner(g.Index()).o.vertex_index
        corner_area = (g.FaceArea().o.area / g.FaceNeighbors().o.vertex_count).face.evaluate()
        area = corner_area.corner.total(vertex).point.evaluate()
        position = g.Position().o.position
        previous = position.point.at(g.VertexOfCorner(g.OffsetCornerInFace(g.Index(), offset=-1)))
        following = position.point.at(g.VertexOfCorner(g.OffsetCornerInFace(g.Index(), offset=1)))
        center = position.point.at(vertex)
        corner_angle = (previous - center).normalize().dot((following - center).normalize()).max(-1.0).min(1.0).acos()
        angle_sum = corner_angle.corner.total(vertex).point.evaluate()
        gaussian = (boundary.switch.float(2.0 * pi, pi) - angle_sum) / area
        edges = g.EdgeVertices()
        edge_length = edges.o.position_1.distance(edges.o.position_2)
        mean = (edge_length * g.EdgeAngle().o.signed_angle).edge.evaluate().point.evaluate() * degree / (4.0 * area)
        mean = independent.switch.float(mean, mean * area.sqrt())
        gaussian = independent.switch.float(gaussian, gaussian * area)
        difference = (mean ** 2.0 - gaussian).max(0.0).sqrt()
        principal = g.MenuSwitch.float(report, {"Smaller": mean - difference, "Larger": mean + difference}).o.output
        principal = g.MenuSwitch.float(sign, {"Signed": principal, "Absolute": principal.abs()}).o.output
        curvature = g.MenuSwitch.float(curvature_type, {
            "Gaussian": gaussian,
            "Mean": mean,
            "Principal": principal,
            "Curvedness": (2.0 * mean ** 2.0 - gaussian).max(0.0).sqrt(),
        }).o.output

        capture = g.CaptureAttribute.point(geometry)
        curvature_weight = capture.items.float((curvature.abs() ** exponent).max(1e-9), "Curvature").output
        affected = capture.items.boolean(selection, "Selection").output
        boundary_weight = capture.items.float(boundary.switch.float(1.0, 1.0 - pin_boundary), "Boundary Weight").output
        repeat = g.RepeatZone(iterations)
        mesh = repeat.items.geometry(capture.o.geometry, "Geometry")
        position = g.Position().o.position
        # Blur includes the current vertex; subtract it to average only edge neighbors.
        weighted_sum = (position * curvature_weight).blur() * (degree + 1) - position * curvature_weight
        weight_sum = curvature_weight.blur() * (degree + 1) - curvature_weight
        target = (weight_sum > 0.0).switch.vector(position, weighted_sum / weight_sum)
        offset = (target - position) * weight * boundary_weight
        g.SetPosition(mesh.current, selection=affected & (degree > 0), offset=offset) >> mesh.next

        mesh.result >> output


ASSET = OSharpen

ASSET_METADATA = {
    "description": "Sharpen mesh features using curvature-weighted neighbors",
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
