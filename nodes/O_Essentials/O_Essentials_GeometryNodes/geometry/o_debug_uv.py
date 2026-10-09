import bpy
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_debug_integer import ODebugInteger
from .o_is_edge_boundary import OIsEdgeBoundary
from .o_is_uv_split import OIsUVSplit
from .o_wireframe import OWireframe

class ODebugUV(CustomGeometryGroup):
    _name = 'O Debug UV'
    _color_tag = 'OUTPUT'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        uvmap = tree.inputs.vector('UVMap', (0.0, 0.0), dimensions=2, hide_value=True, subtype='XYZ')
        flat = tree.inputs.boolean('Flat', False)
        uv_seam = tree.inputs.boolean('UV Seam', True)
        with tree.inputs.panel('Transform', default_closed=True):
            translation = tree.inputs.vector('Translation', (0.0, 0.0, 0.0), min_value=-1.0, max_value=1.0)
            rotation = tree.inputs.rotation('Rotation', (0.0, 0.0, 0.0))
            scale = tree.inputs.float('Scale', 1.0, min_value=0.10000000149011612, max_value=10.0)
        with tree.inputs.panel('Options', default_closed=True):
            uv = tree.inputs.string('UV', 'UVMap')
            seam = tree.inputs.color('Seam', (1.0, 0.0, 0.0, 1.0))
            seed = tree.inputs.integer('Seed', 0, min_value=-10000, max_value=10000)
        debug = tree.outputs.geometry('Debug')
        o_is_uv_split = OIsUVSplit(UV=uv)
        set_position = g.SetPosition(geometry=g.SplitEdges(mesh=mesh, selection=o_is_uv_split.o.is_uv_split), position=g.NamedAttribute.vector(uv).o.attribute)
        o_debug_integer = ODebugInteger(Mesh=flat.switch.geometry(mesh, set_position), Integer=g.EdgesToFaceGroups(boundary_edges=o_is_uv_split.o.is_uv_split), Seed=seed)
        transform_point = uvmap.transform(g.CombineTransform(translation=translation, rotation=rotation, scale=scale))
        set_material = o_debug_integer >> g.StoreNamedAttribute.corner.color(name='o_uvisland', value=o_debug_integer.o.color) >> g.StoreNamedAttribute.corner.vector_2d(name=uv, value=transform_point) >> g.StoreNamedAttribute.corner.boolean(name='o_show_uvisland', value=True) >> g.SetMaterial(material=bpy.data.materials.get('O Debug UV'))
        mesh_to_curve = g.MeshToCurve(mesh=set_material, selection=flat.switch.boolean(OIsUVSplit(UV=uv).o.is_uv_split, OIsEdgeBoundary()))
        set_material_1 = OWireframe(Mesh=g.CurveToMesh(curve=mesh_to_curve)) >> g.StoreNamedAttribute.corner.color(name='o_color', value=seam) >> g.SetMaterial(material=bpy.data.materials.get('O Debug Color'))
        join_geometry = g.JoinGeometry(geometry=(set_material, uv_seam.switch.geometry(true=set_material_1)))
        join_geometry >> debug
ASSET = ODebugUV
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '3aee6aa4-2dd5-4adb-9bed-3676454cdeff'}
DATABLOCK_DEPENDENCIES = {'materials': ('O Debug Color', 'O Debug UV')}
