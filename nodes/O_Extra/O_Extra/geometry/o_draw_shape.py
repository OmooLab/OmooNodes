from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_transfer_attributes import OTransferAttributes as OTransferAttributes
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_voxel_remesh import OVoxelRemesh as OVoxelRemesh
import bpy
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_displace import ODisplace as ODisplace
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_relax import ORelax as ORelax
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_smooth import OSmooth as OSmooth
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_symmetry import OSymmetry as OSymmetry

class ODrawShape(CustomGeometryGroup):
    _name = 'O Draw Shape'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'node_tool_idname': 'geometry.o_draw_shape', 'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        grease_pencil = tree.inputs.geometry('Grease Pencil')
        resolution = tree.inputs.integer('Resolution', 8, description='Number of points on the circle', min_value=4, max_value=16)
        inflate = tree.inputs.float('Inflate', 0.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        with tree.inputs.panel('Symmetry', default_closed=True):
            symmetry = tree.inputs.boolean('Symmetry', False, is_panel_toggle=True)
            menu = tree.inputs.menu('Menu', 'Mirror', expanded=True, optional_label=True)
            menu_1 = tree.inputs.menu('Menu', 'X', expanded=True, optional_label=True)
            radial = tree.inputs.integer('Radial', 3, description='Number of vertices on the circle', min_value=3, max_value=8)
        with tree.inputs.panel('Remesh', default_closed=True):
            remesh = tree.inputs.boolean('Remesh', False, is_panel_toggle=True)
            resolution_1 = tree.inputs.float('Resolution', 0.10000000149011612, min_value=0.009999999776482582, max_value=0.10000000149011612)
            relax_iterations = tree.inputs.integer('Relax Iterations', 1, min_value=1, max_value=10)
            smooth_iterations = tree.inputs.integer('Smooth Iterations', 1, description='How many times to blur the values for all elements', min_value=1, max_value=20)
        mesh = tree.outputs.geometry('Mesh')
        _radius = g.Radius()
        radius_1 = g.Radius()
        attribute = g.NamedAttribute.color('vertex_color').o.attribute
        combine_color = g.CombineColor(red=attribute.r, green=attribute.g, blue=attribute.b, alpha=g.NamedAttribute.float('opacity').o.attribute)
        separate_components = g.SeparateComponents(geometry=grease_pencil)
        grease_pencil_to_curves = g.GreasePencilToCurves(grease_pencil=separate_components.o.grease_pencil, layers_as_instances=False)
        store_named_attribute = g.StoreNamedAttribute.point.color(g.JoinGeometry(geometry=(separate_components.o.curve, grease_pencil_to_curves)), name='o_color', value=combine_color)
        capture = g.CaptureAttribute.point(geometry=store_named_attribute)
        radius_2 = capture.items.float(radius_1, 'Radius')
        curve_to_mesh = capture.o.geometry >> g.CurveToMesh(profile_curve=g.CurveCircle(resolution=resolution), scale=radius_1, fill_caps=True)
        o_symmetry = OSymmetry(Geometry=curve_to_mesh, Radial=radial, _named_links=[('Menu', menu), ('Menu', menu_1)])
        o_displace = ODisplace(Geometry=symmetry.switch.geometry(curve_to_mesh, o_symmetry), Height=radius_2.output * inflate)
        o_voxel_remesh = OVoxelRemesh(Mesh=o_displace, Resolution=resolution_1, **{'Relax Iterations': relax_iterations})
        o_smooth = OSmooth(Geometry=o_voxel_remesh, Iterations=smooth_iterations, **{'Pin Sharp': 1.0, 'Pin Boundary': 1.0})
        remesh.switch.geometry(o_displace, OTransferAttributes(Mesh=o_smooth, Source=o_displace, Color='o_color')) >> g.SetMaterial(material=bpy.data.materials.get('O Vertex Paint')) >> mesh
ASSET = ODrawShape
ASSET_METADATA = {'catalog_id': '90187864-01c8-45bc-99f1-66e7e746beb8'}
DATABLOCK_DEPENDENCIES = {'materials': ('O Vertex Paint',)}
