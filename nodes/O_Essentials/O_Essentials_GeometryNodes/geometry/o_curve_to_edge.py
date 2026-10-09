from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OCurveToEdge(CustomGeometryGroup):
    _name = 'O Curve to Edge'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        curve = tree.inputs.geometry('Curve')
        edge = tree.outputs.geometry('Edge')
        capture = g.CaptureAttribute.curve(geometry=curve)
        attribute = capture.items.integer(g.NamedAttribute.integer('normal_mode').o.attribute, 'Attribute')
        capture_1 = g.CaptureAttribute.point(geometry=capture.o.geometry)
        radius = capture_1.items.float(g.Radius(), 'Radius')
        normal = capture_1.items.vector(g.Normal().o.normal, 'Normal')
        tangent = capture_1.items.vector(g.CurveTangent(), 'Tangent')
        tilt = capture_1.items.float(g.CurveTilt(), 'Tilt')
        capture_1.o.geometry >> g.CurveToMesh() >> g.StoreNamedAttribute.point.integer(name='o_normal_mode', value=attribute.output) >> g.StoreNamedAttribute.point.float(name='radius', value=radius.output) >> g.StoreNamedAttribute.point.vector(name='o_normal', value=normal.output) >> g.StoreNamedAttribute.point.vector(name='o_tangent', value=tangent.output) >> g.StoreNamedAttribute.point.float(name='o_tilt', value=tilt.output) >> edge
ASSET = OCurveToEdge
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '925722af-3fbd-4bb1-8247-dfe9a1ecd480'}
