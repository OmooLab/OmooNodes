from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OMeshDistanceTexture(CustomGeometryGroup):
    _name = 'O Mesh Distance Texture'
    _color_tag = 'TEXTURE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        unsigned = tree.inputs.boolean('Unsigned', True)
        offset = tree.inputs.float('Offset', 0.0, subtype='DISTANCE')
        value = tree.outputs.float('Value')
        geometry_proximity = g.GeometryProximity(target=mesh)
        switch = g.Switch.float(g.VectorMath.dot_product((0.0, 0.0, -1.0), g.Raycast.float(mesh).o.hit_normal).o.value, 1.0, -1.0)
        switch_1 = unsigned.switch.float(geometry_proximity.o.distance, geometry_proximity.o.distance * switch)
        switch_1 - offset >> value
ASSET = OMeshDistanceTexture
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '2e34744f-a050-4efb-a7b7-c052b449fc5d'}
