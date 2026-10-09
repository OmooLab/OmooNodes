from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class ODeleteSmallParts(CustomGeometryGroup):
    _name = 'O Delete Small Parts'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'node_tool_idname': 'geometry.o_delete_small_parts', 'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        threshold = tree.inputs.float('Threshold', 1.0, min_value=0.0, structure_type='SINGLE', force_non_field=True)
        mesh_1 = tree.outputs.geometry('Mesh')
        mesh >> g.DeleteGeometry.point(selection=g.FaceArea().o.area.point.total(g.MeshIsland().o.island_index) < threshold) >> mesh_1
ASSET = ODeleteSmallParts
ASSET_METADATA = {'catalog_id': '1f098c57-6187-4e3a-95ba-d7e3d187c6d5'}
