from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OEdgeToCurve(CustomGeometryGroup):
    _name = 'O Edge to Curve'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        edge = tree.inputs.geometry('Edge')
        curve = tree.outputs.geometry('Curve')
        capture = g.CaptureAttribute.point(geometry=edge)
        mode = capture.items.integer(g.NamedAttribute.integer('o_normal_mode').o.attribute, 'Mode')
        normal = capture.items.vector(g.NamedAttribute.vector('o_normal').o.attribute, 'Normal')
        attribute = capture.items.float(g.NamedAttribute.float('o_tilt').o.attribute, 'Attribute')
        mesh_to_curve = capture.o.geometry >> g.MeshToCurve()
        set_curve_normal = g.SetCurveNormal(curve=g.SeparateGeometry.spline(mesh_to_curve, g.Compare.integer.equal(mode.output, 2)).o.selection, normal=normal.output, mode='Free')
        set_curve_normal_1 = g.SeparateGeometry.spline(mesh_to_curve, g.Compare.integer.equal(mode.output, 0)) >> g.SetCurveTilt(tilt=attribute.output) >> g.SetCurveNormal()
        set_curve_normal_2 = g.SeparateGeometry.spline(mesh_to_curve, g.Compare.integer.equal(mode.output, 1)) >> g.SetCurveTilt(tilt=attribute.output) >> g.SetCurveNormal(mode='Z Up')
        join_geometry = g.JoinGeometry(geometry=(set_curve_normal_1, set_curve_normal_2, set_curve_normal))
        join_geometry >> curve
ASSET = OEdgeToCurve
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '925722af-3fbd-4bb1-8247-dfe9a1ecd480'}
