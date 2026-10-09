from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_is_uv_split import OIsUVSplit

class OUVIsland(CustomGeometryGroup):
    _name = 'O UV Island'
    _color_tag = 'INPUT'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        uv = tree.inputs.string('UV', 'UVMap')
        uv_island = tree.outputs.integer('UV Island', description='Index of the face group inside each boundary edge region')
        edges_to_face_groups = g.EdgesToFaceGroups(boundary_edges=OIsUVSplit(UV=uv).o.is_uv_split)
        edges_to_face_groups >> uv_island
ASSET = OUVIsland
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '99c91009-1ea6-4fc1-bf33-6351786a8df1'}
