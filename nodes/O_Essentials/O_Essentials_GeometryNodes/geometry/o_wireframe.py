from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OWireframe(CustomGeometryGroup):
    _name = 'O Wireframe'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 180, 'node_tool_idname': 'geometry.o_wireframe', 'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        selection = tree.inputs.boolean('Selection', True, hide_value=True, hide_in_modifier=True)
        resolution = tree.inputs.integer('Resolution', 4, description='Number of points on the circle', min_value=3, max_value=16)
        radius = tree.inputs.float('Radius', 1.0, description='Distance of the points from the origin', min_value=0.009999999776482582, max_value=10.0)
        mesh_1 = tree.outputs.geometry('Mesh')
        mesh >> g.MeshToCurve(selection=selection) >> g.CurveToMesh(profile_curve=g.CurveCircle(resolution=resolution, radius=radius), scale=0.009999999776482582, fill_caps=True) >> mesh_1
ASSET = OWireframe
ASSET_METADATA = {'description': "Converts the model to a wireframe, highlighting the model's framework structure.", 'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '0218b41f-9d3f-4dd0-9491-5c56e57678db'}
