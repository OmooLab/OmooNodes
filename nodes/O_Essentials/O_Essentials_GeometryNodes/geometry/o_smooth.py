from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_is_edge_boundary import OIsEdgeBoundary

class OSmooth(CustomGeometryGroup):
    _name = 'O Smooth'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 160, 'node_tool_idname': 'geometry.o_smooth', 'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        iterations = tree.inputs.integer('Iterations', 5, description='How many times to blur the values for all elements', min_value=1, max_value=20)
        pin_sharp = tree.inputs.float('Pin Sharp', 0.0, description='Relative mix weight of neighboring elements', min_value=0.0, max_value=1.0, subtype='FACTOR')
        pin_boundary = tree.inputs.float('Pin Boundary', 0.0, description='Relative mix weight of neighboring elements', min_value=0.0, max_value=0.9998999834060669, subtype='FACTOR')
        with tree.inputs.panel('Options', default_closed=True):
            weight = tree.inputs.float('Weight', 1.0, description='Relative mix weight of neighboring elements', min_value=0.0, max_value=1.0, subtype='FACTOR')
        geometry_1 = tree.outputs.geometry('Geometry')
        blur_attribute = g.Position().o.position.blur()
        repeat_zone = g.RepeatZone(iterations)
        geometry_2 = repeat_zone.items.geometry(geometry, 'Geometry')
        separate_geometry = g.SeparateGeometry.point(geometry_2.current, OIsEdgeBoundary().o.is_edge_boundary.point.evaluate())
        sample_index = g.SampleIndex.point.vector(separate_geometry.o.selection, g.Position().o.position.blur(weight=0.5), g.SampleNearest.point(separate_geometry.o.selection))
        mix = g.Mix.vector(pin_boundary, blur_attribute, OIsEdgeBoundary().o.is_edge_boundary.switch.vector(blur_attribute, sample_index), clamp_factor=True)
        math_1 = weight * g.Switch.float(pin_sharp, 1.0, g.Normal().o.normal.blur(10, pin_sharp).length())
        mix_1 = g.Mix.vector(math_1, g.Position(), g.Switch.vector(pin_boundary, blur_attribute, mix.o.result_vector), clamp_factor=True)
        set_position = g.SetPosition(geometry=geometry_2.current, selection=selection, position=mix_1.o.result_vector)
        set_position >> geometry_2.next
        geometry_2.result >> geometry_1
ASSET = OSmooth
ASSET_METADATA = {'description': 'Smart smooth surface', 'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': 'f223bfa5-ce4b-4f80-838a-eff17d3cf085'}
