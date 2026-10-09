from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_mask_by_distance import OMaskByDistance

class OMaskBySelection(CustomGeometryGroup):
    _name = 'O Mask by Selection'
    _color_tag = 'CONVERTER'
    _tree_properties = {'default_group_node_width': 180}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        method = tree.inputs.menu('Method', 'Distance', optional_label=True)
        max_distance = tree.inputs.float('Max Distance', 1.0, min_value=0.0, max_value=10000.0)
        menu = tree.inputs.menu('Menu', 'Point', optional_label=True)
        solid = tree.inputs.boolean('Solid', False)
        smooth = tree.inputs.float('Smooth', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        smooth_iterations = tree.inputs.integer('Smooth Iterations', 5, description='How many times to blur the values for all elements', min_value=1, max_value=20)
        geometry_1 = tree.outputs.geometry('Geometry')
        mask = tree.outputs.float('Mask')
        capture = g.CaptureAttribute.point(geometry=geometry)
        selection_1 = capture.items.boolean(selection, 'Selection')
        menu_switch = g.MenuSwitch.float(menu, {'Point': g.EvaluateOnDomain.point.float(selection), 'Edge': g.EvaluateOnDomain.edge.float(selection), 'Face': g.EvaluateOnDomain.face.float(selection), 'Face Corner': g.EvaluateOnDomain.corner.float(selection)})
        capture_1 = g.CaptureAttribute.point(geometry=geometry)
        value = capture_1.items.float(menu_switch.o.output, 'Value')
        menu_switch_1 = g.MenuSwitch.integer(method, {'Distance': 0, 'Blur': 1})
        repeat_zone = g.RepeatZone(smooth_iterations)
        geometry_2 = repeat_zone.items.geometry(capture_1.o.geometry, 'Geometry')
        value_1 = repeat_zone.items.float(value.output, 'Value')
        blur_attribute = value_1.current.blur(weight=smooth)
        separate_components = capture.o.geometry >> g.SeparateComponents()
        join_geometry = g.JoinGeometry(geometry=(separate_components.o.mesh, g.CurveToMesh(curve=separate_components.o.curve)))
        o_mask_by_distance = OMaskByDistance(Geometry=geometry, Source=g.SeparateGeometry.point(join_geometry, selection_1.output).o.selection, **{'Max Distance': max_distance})
        _switch = g.Switch.float(value.output, value_1.current, 1.0)
        geometry_2.current >> geometry_2.next
        solid.switch.float(blur_attribute, g.Switch.float(value.output, blur_attribute, 1.0)) >> value_1.next
        capture_2 = g.CaptureAttribute.point(geometry=geometry_2.result)
        value_2 = capture_2.items.float(value_1.result, 'Value')
        g.IndexSwitch.geometry(menu_switch_1.o.output, (o_mask_by_distance, capture_2.o.geometry)) >> geometry_1
        g.IndexSwitch.float(menu_switch_1.o.output, (o_mask_by_distance.o.mask, value_2.output)) >> mask
ASSET = OMaskBySelection
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
