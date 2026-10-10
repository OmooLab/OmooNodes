from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_smooth_attributes import OSmoothAttributes as OSmoothAttributes
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_fast_remesh import OFastRemesh as OFastRemesh
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_transfer_uv import OTransferUV as OTransferUV
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_mask_by_selection import OMaskBySelection as OMaskBySelection
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_uv_island import OUVIsland as OUVIsland
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_is_uv_split import OIsUVSplit as OIsUVSplit
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_tube import OTube as OTube
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_solidfy import OSolidfy as OSolidfy
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_mix_color import OMixColor as OMixColor
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_quad_sphere import OQuadSphere as OQuadSphere
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry._shared.o_spherization_correction import OSpherizationCorrection as OSpherizationCorrection
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_align_edge_ends import OAlignEdgeEnds as OAlignEdgeEnds
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_mask_by_distance import OMaskByDistance as OMaskByDistance
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_index_selection import OIndexSelection as OIndexSelection
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_edge_to_curve import OEdgeToCurve as OEdgeToCurve
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_curve_to_edge import OCurveToEdge as OCurveToEdge
import bpy
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_displace import ODisplace as ODisplace
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_is_edge_boundary import OIsEdgeBoundary as OIsEdgeBoundary
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_relax import ORelax as ORelax
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_smooth import OSmooth as OSmooth
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_symmetry import OSymmetry as OSymmetry

class ODrawTubes(CustomGeometryGroup):
    _name = 'O Draw Tubes'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        grease_pencil = tree.inputs.geometry('Grease Pencil')
        resolution = tree.inputs.integer('Resolution', 8, description='Number of points on the circle', min_value=4, max_value=16)
        radius_scale = tree.inputs.float('Radius Scale', 1.0, description='Distance of the points from the origin', min_value=0.10000000149011612, max_value=2.0)
        thickness = tree.inputs.float('Thickness', 0.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        fill_caps = tree.inputs.boolean('Fill Caps', False, description='If the profile spline is cyclic, fill the ends of the generated mesh with N-gons')
        with tree.inputs.panel('Symmetry', default_closed=True):
            symmetry = tree.inputs.boolean('Symmetry', False, is_panel_toggle=True)
            menu = tree.inputs.menu('Menu', 'Mirror', expanded=True, optional_label=True)
            menu_1 = tree.inputs.menu('Menu', 'X', expanded=True, optional_label=True)
            radial = tree.inputs.integer('Radial', 3, min_value=3, max_value=8)
        with tree.inputs.panel('Align Ends', default_closed=True):
            align_ends = tree.inputs.boolean('Align Ends', False, is_panel_toggle=True)
            align_threshold = tree.inputs.float('Align Threshold', 0.05000000074505806, min_value=0.0, structure_type='SINGLE', subtype='DISTANCE', force_non_field=True)
            align_iterations = tree.inputs.integer('Align Iterations', 5, min_value=1, max_value=10)
        with tree.inputs.panel('Remesh', default_closed=True):
            remesh = tree.inputs.boolean('Remesh', False, is_panel_toggle=True)
            connect_distance = tree.inputs.float('Connect Distance', 0.009999999776482582, min_value=0.0, structure_type='SINGLE', subtype='DISTANCE', force_non_field=True)
            resolution_1 = tree.inputs.float('Resolution', 0.009999999776482582, min_value=0.009999999776482582, max_value=0.10000000149011612)
            relax_iterations = tree.inputs.integer('Relax Iterations', 1, min_value=1, max_value=10)
            smooth_iterations = tree.inputs.integer('Smooth Iterations', 1, description='How many times to blur the values for all elements', min_value=1, max_value=20)
        mesh = tree.outputs.geometry('Mesh')
        with tree.panel('Options', reuse=False):
            pass
        attribute = g.NamedAttribute.color('vertex_color').o.attribute
        combine_color = g.CombineColor(red=attribute.r, green=attribute.g, blue=attribute.b, alpha=g.NamedAttribute.float('opacity').o.attribute)
        separate_components = g.SeparateComponents(geometry=grease_pencil)
        grease_pencil_to_curves = g.GreasePencilToCurves(grease_pencil=separate_components.o.grease_pencil, layers_as_instances=False)
        store_named_attribute = g.StoreNamedAttribute.point.color(g.JoinGeometry(geometry=(separate_components.o.curve, grease_pencil_to_curves)), name='o_color', value=combine_color)
        o_curve_to_edge = OCurveToEdge(Curve=store_named_attribute)
        o_symmetry = OSymmetry(Geometry=o_curve_to_edge, Radial=radial, _named_links=[('Menu', menu), ('Menu', menu_1)])
        switch = symmetry.switch.geometry(o_curve_to_edge, o_symmetry)
        o_align_edge_ends = OAlignEdgeEnds(Edge=switch, **{'Distance Threshold': align_threshold}, Iterations=align_iterations)
        o_tube = OTube(Edge=align_ends.switch.geometry(switch, o_align_edge_ends), Resolution=resolution, **{'Radius Scale': radius_scale}, Thickness=thickness, **{'Fill Caps': fill_caps}, Connect=remesh & align_ends, **{'Distance Threshold': connect_distance}, Color='o_color')
        o_fast_remesh = OFastRemesh(Mesh=o_tube, Resolution=resolution_1, **{'Relax Iterations': relax_iterations})
        o_smooth_attributes = OSmoothAttributes(Mesh=o_fast_remesh, Float='radius', Color='o_color', Iterations=smooth_iterations)
        o_smooth = OSmooth(Geometry=o_smooth_attributes, Iterations=smooth_iterations, **{'Pin Sharp': 1.0, 'Pin Boundary': 0.9998999834060669})
        remesh.switch.geometry(o_tube, o_smooth) >> g.SetMaterial(material=bpy.data.materials.get('O Vertex Paint')) >> mesh
ASSET = ODrawTubes
ASSET_METADATA = {'catalog_id': '90187864-01c8-45bc-99f1-66e7e746beb8'}
DATABLOCK_DEPENDENCIES = {'materials': ('O Vertex Paint',)}
