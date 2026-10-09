from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_curve_to_edge import OCurveToEdge

class OCurveDistanceTexture(CustomGeometryGroup):
    _name = 'O Curve Distance Texture'
    _color_tag = 'TEXTURE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        curve_edge = tree.inputs.geometry('Curve (Edge)')
        radius_offset = tree.inputs.float('Radius Offset', 0.0, min_value=0.0, subtype='DISTANCE')
        value = tree.outputs.float('Value')
        (OCurveToEdge(Curve=curve_edge) >> g.GeometryProximity(target_element='EDGES')).o.distance - radius_offset >> value
ASSET = OCurveDistanceTexture
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '2e34744f-a050-4efb-a7b7-c052b449fc5d'}
