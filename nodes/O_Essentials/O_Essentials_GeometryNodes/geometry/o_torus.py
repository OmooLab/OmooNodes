# Node-group asset "O Torus" (GeometryNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup


class OTorus(CustomGeometryGroup):
    _name = "O Torus"
    _color_tag = "GEOMETRY"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        major_segments = tree.inputs.integer("Major Segments", 32, min_value=3, max_value=128)
        minor_segments = tree.inputs.integer("Minor Segments", 16, min_value=3, max_value=64)
        major_radius = tree.inputs.float("Major Radius", 1.0, min_value=0.0, subtype="DISTANCE")
        minor_radius = tree.inputs.float("Minor Radius", 0.5, min_value=0.0, subtype="DISTANCE")
        mesh = tree.outputs.geometry("Mesh")
        uv_map = tree.outputs.vector("UV Map")

        endpoint_selection = g.EndpointSelection(end_size=0)
        math_1 = g.Math.truncated_modulo(g.Index(), 4.0)
        spline_parameter = g.SplineParameter()
        capture = g.CaptureAttribute.point(geometry=g.CurveCircle(resolution=major_segments, radius=major_radius))
        value = capture.items.float(spline_parameter.o.factor, "Value")
        selection = capture.items.boolean(endpoint_selection, "Selection")
        transform_geometry = g.TransformGeometry(geometry=g.CurveCircle(resolution=minor_segments, radius=minor_radius), rotation=(0.0, 0.0, 3.1415927410125732))
        capture_1 = g.CaptureAttribute.point(geometry=transform_geometry)
        value_1 = capture_1.items.float(spline_parameter.o.factor, "Value")
        selection_1 = capture_1.items.boolean(endpoint_selection, "Selection")
        set_shade_smooth = (
            capture.o.geometry
            >> g.CurveToMesh(profile_curve=capture_1.o.geometry)
            >> g.SetShadeSmooth.face(shade_smooth=False)
        )
        switch = (selection_1.output & g.Compare.float.equal(math_1, 1.5, 1.0)).switch.float(value_1.output, 1.0)
        combine_xyz = g.CombineXYZ(x=(selection.output & (math_1 > 1.5)).switch.float(value.output, 1.0), y=1.0 - switch)
        capture_2 = g.CaptureAttribute.corner(geometry=set_shade_smooth)
        value_2 = capture_2.items.vector(combine_xyz, "Value")

        capture_2.o.geometry >> mesh
        value_2.output >> uv_map

ASSET = OTorus

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "0218b41f-9d3f-4dd0-9491-5c56e57678db",
}
