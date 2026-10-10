from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_debug_direction import ODebugDirection

class OProject(CustomGeometryGroup):
    _name = 'O Project'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        selection = tree.inputs.boolean('Selection', True, hide_value=True, hide_in_modifier=True)
        source = tree.inputs.geometry('Source')
        menu = tree.inputs.menu('Menu', 'Minimum Distance', optional_label=True)
        positive_weight = tree.inputs.float('Positive Weight', 1.0, description='Amount of mixing between the A and B inputs', min_value=0.0, max_value=1.0, subtype='FACTOR')
        negative_weight = tree.inputs.float('Negative Weight', 1.0, description='Amount of mixing between the A and B inputs', min_value=0.0, max_value=1.0, subtype='FACTOR')
        max_distance = tree.inputs.float('Max Distance', 0.10000000149011612, min_value=0.0, max_value=1.0, subtype='DISTANCE')
        with tree.inputs.panel('Options', default_closed=True):
            weight = tree.inputs.float('Weight', 1.0, description='Amount of mixing between the A and B inputs', min_value=0.0, max_value=1.0, subtype='FACTOR')
            radius_offset = tree.inputs.float('Radius Offset', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
            menu_1 = tree.inputs.menu('Menu', 'Source', expanded=True, optional_label=True)
            custom = tree.inputs.vector('Custom', (0.0, 0.0, 1.0), hide_value=True)
            normal_smooth = tree.inputs.integer('Normal Smooth', 1, description='How many times to blur the values for all elements', min_value=0, max_value=20)
        geometry_1 = tree.outputs.geometry('Geometry')
        normal = g.Normal()
        position = g.Position()
        menu_switch = g.MenuSwitch.vector(menu_1, {'Source': g.SampleNearestSurface.vector(source, normal.o.normal).o.value, 'Normal': normal.o.normal, 'Custom': custom})
        blur_attribute = menu_switch.o.output.blur(normal_smooth)
        raycast = g.Raycast.float(source, ray_direction=blur_attribute, ray_length=max_distance)
        raycast_1 = g.Raycast.float(source, ray_direction=blur_attribute * -1.0, ray_length=max_distance)
        math_1 = (raycast_1.o.is_hit & (raycast_1.o.hit_normal.dot(blur_attribute) > 0.0)) * negative_weight
        mix = g.Mix.vector((raycast.o.is_hit & (raycast.o.hit_normal.dot(blur_attribute) > 0.0)) * positive_weight, position, raycast.o.hit_position, clamp_factor=True)
        switch = raycast.o.is_hit.switch.vector(g.Mix.vector(math_1, position, raycast_1.o.hit_position, clamp_factor=True).o.result_vector, mix.o.result_vector)
        menu_switch_1 = g.MenuSwitch.vector(menu, {'Minimum Distance': g.GeometryProximity(target=source).o.position, 'Project': switch})
        vector_math = menu_switch_1.o.output + blur_attribute.normalize() * (g.Radius().o.radius * radius_offset)
        set_position = g.SetPosition(geometry=geometry, selection=selection, position=weight.mix.vector(g.Position(), vector_math))
        viewer = g.Viewer()
        viewer.node.viewer_items.clear()
        viewer.node.viewer_items.new('GEOMETRY', 'Geometry').auto_remove = False
        ODebugDirection(Geometry=geometry, Direction=blur_attribute) >> viewer.i[0]
        viewer.node.viewer_items.new('BOOLEAN', 'Value').auto_remove = False
        raycast_1 >> viewer.i[1]
        set_position >> geometry_1
ASSET = OProject
ASSET_METADATA = {'description': 'Projecting details from source', 'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': 'f223bfa5-ce4b-4f80-838a-eff17d3cf085'}
