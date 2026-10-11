from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OCurveDeform(CustomGeometryGroup):
    _name = "O Curve Deform"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160, "is_modifier": True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        curve = tree.inputs.geometry("Curve")
        offset = tree.inputs.float("Offset", 0.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        tilt = tree.inputs.float("Tilt", 0.0, subtype="ANGLE")
        fit_to_curve = tree.inputs.boolean("Fit to Curve", False)
        with tree.inputs.panel("Orient", default_closed=True):
            primary_axis = tree.inputs.vector("Primary Axis", (0.0, 0.0, 1.0))
            secondary_axis = tree.inputs.vector("Secondary Axis", (1.0, 0.0, 0.0))
        with tree.inputs.panel("Options", default_closed=True):
            weight = tree.inputs.float("Weight", 1.0, description="Amount of mixing between the A and B inputs", min_value=0.0, max_value=1.0, subtype="FACTOR")
            center = tree.inputs.menu("Center", "Center", expanded=True, optional_label=True)
            offset_1 = tree.inputs.vector("Offset", (0.0, 0.0, 0.0))
            custom = tree.inputs.vector("Custom", (0.0, 0.0, 0.0))
        geometry_1 = tree.outputs.geometry("Geometry")

        bounding_box = g.BoundingBox(geometry=geometry)
        curve_length = g.CurveLength(curve=curve)
        rotate_rotation = g.AxesToRotation(primary_axis=primary_axis, secondary_axis=secondary_axis).o.rotation.rotate((0.0, 0.0, 1.5707964), rotation_space="LOCAL")
        set_curve_tilt = g.SetCurveTilt(curve=curve, tilt=tilt)
        sample_index = g.SampleIndex.point.boolean(set_curve_tilt, g.IsSplineCyclic(), g.Index(), clamp=True)
        menu_switch = g.MenuSwitch.vector(center, {"Center": (bounding_box.o.min + bounding_box.o.max) * 0.5 + offset_1, "Custom": custom})
        vector_rotate = g.VectorRotate.euler(g.Position().o.position - menu_switch.o.output, rotation=rotate_rotation)
        attribute_statistic = g.AttributeStatistic.point.float(geometry, attribute=vector_rotate.o.vector.z)
        map_range = vector_rotate.o.vector.z.map_range(attribute_statistic.o.min, attribute_statistic.o.max, to_max=attribute_statistic.o.range)
        map_range_1 = vector_rotate.o.vector.z.map_range(attribute_statistic.o.min, attribute_statistic.o.max, to_max=curve_length)
        switch = sample_index.o.value.switch.float(curve_length.o.length - attribute_statistic.o.range, curve_length)
        math_1 = switch * offset
        math_2 = map_range + math_1
        switch_1 = sample_index.o.value.switch.float(map_range_1, g.Math.truncated_modulo(map_range_1 + math_1, curve_length))
        switch_2 = fit_to_curve.switch.float(sample_index.o.value.switch.float(math_2, g.Math.truncated_modulo(math_2, curve_length)), switch_1)
        sample_curve = g.SampleCurve.length.float(set_curve_tilt, length=switch_2, use_all_curves=True)
        vector_math = sample_curve.o.normal * vector_rotate.o.vector.y + sample_curve.o.normal.cross(sample_curve.o.tangent) * vector_rotate.o.vector.x
        (
            geometry
            >> g.SetPosition(selection=selection, position=weight.mix.vector(g.Position(), sample_curve.o.position + vector_math))
            >> geometry_1
        )

ASSET = OCurveDeform

ASSET_METADATA = {
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
