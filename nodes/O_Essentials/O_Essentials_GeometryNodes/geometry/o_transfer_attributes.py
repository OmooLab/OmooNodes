from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OTransferAttributes(CustomGeometryGroup):
    _name = 'O Transfer Attributes'
    _color_tag = 'ATTRIBUTE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        source = tree.inputs.geometry('Source')
        float = tree.inputs.string('Float', '', description='Separate with commas')
        integer = tree.inputs.string('Integer', '', description='Separate with commas')
        vector = tree.inputs.string('Vector', '', description='Separate with commas')
        color = tree.inputs.string('Color', '', description='Separate with commas')
        on = tree.inputs.menu('on', 'Point', optional_label=True)
        evaluate_on = tree.inputs.menu('Evaluate on', 'Same', optional_label=True)
        with tree.inputs.panel('Options', default_closed=True):
            group_id = tree.inputs.integer('Group ID', 0, description='Splits the faces of the input mesh into groups which can be sampled individually', hide_value=True)
            sample_position = tree.inputs.vector('Sample Position', (0.0, 0.0, 0.0), hide_value=True, default_input='POSITION')
            sample_group_id = tree.inputs.integer('Sample Group ID', 0, hide_value=True)
        mesh_1 = tree.outputs.geometry('Mesh')
        menu_switch = g.MenuSwitch.integer(on, {'Point': 0, 'Edge': 1, 'Face': 2, 'Face Corner': 3})
        menu_switch_1 = g.MenuSwitch.integer(evaluate_on, {'Same': menu_switch.o.output, 'Eval on Point': 0, 'Eval on Edge': 1, 'Eval on Face': 2, 'Eval on Face Corner': 3})
        repeat_zone = g.RepeatZone(float.find(',').count + 1.0)
        rest = repeat_zone.items.string(float, 'Rest')
        mesh_2 = repeat_zone.items.geometry(mesh, 'Mesh')
        find_in_string = rest.current.find(',')
        switch = (g.DomainSize(geometry=source).o.point_count > 0).switch.geometry(mesh, source)
        switch_1 = (find_in_string.count > 0).switch.string(rest.current, rest.current.slice(length=find_in_string.first_found))
        replace_string = switch_1.replace(' ', '')
        sample_nearest_surface = g.SampleNearestSurface.float(switch, g.NamedAttribute.float(replace_string).o.attribute, group_id, sample_position, sample_group_id)
        index_switch = g.IndexSwitch.float(menu_switch_1.o.output, (sample_nearest_surface.o.value.point.evaluate(), sample_nearest_surface.o.value.edge.evaluate(), sample_nearest_surface.o.value.face.evaluate(), sample_nearest_surface.o.value.corner.evaluate()))
        store_named_attribute = g.StoreNamedAttribute.point.float(mesh_2.current, selection, replace_string, index_switch)
        store_named_attribute_1 = g.StoreNamedAttribute.edge.float(mesh_2.current, selection, replace_string, index_switch)
        store_named_attribute_2 = g.StoreNamedAttribute.face.float(mesh_2.current, selection, replace_string, index_switch)
        store_named_attribute_3 = g.StoreNamedAttribute.corner.float(mesh_2.current, selection, replace_string, index_switch)
        index_switch_1 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute, store_named_attribute_1, store_named_attribute_2, store_named_attribute_3))
        rest.current.slice(find_in_string.first_found + 1.0, rest.current.length()) >> rest.next
        index_switch_1 >> mesh_2.next
        switch_2 = (float.length() > 0).switch.geometry(mesh, mesh_2.result)
        repeat_zone_1 = g.RepeatZone(integer.find(',').count + 1.0)
        rest_1 = repeat_zone_1.items.string(integer, 'Rest')
        mesh_3 = repeat_zone_1.items.geometry(switch_2, 'Mesh')
        find_in_string_1 = rest_1.current.find(',')
        switch_3 = (find_in_string_1.count > 0).switch.string(rest_1.current, rest_1.current.slice(length=find_in_string_1.first_found))
        replace_string_1 = switch_3.replace(' ', '')
        sample_nearest_surface_1 = g.SampleNearestSurface.integer(switch, g.NamedAttribute.integer(replace_string_1).o.attribute, group_id, sample_position, sample_group_id)
        index_switch_2 = g.IndexSwitch.integer(menu_switch_1.o.output, (sample_nearest_surface_1.o.value.point.evaluate(), sample_nearest_surface_1.o.value.edge.evaluate(), sample_nearest_surface_1.o.value.face.evaluate(), sample_nearest_surface_1.o.value.corner.evaluate()))
        store_named_attribute_4 = g.StoreNamedAttribute.point.integer(mesh_3.current, selection, replace_string_1, index_switch_2)
        store_named_attribute_5 = g.StoreNamedAttribute.edge.integer(mesh_3.current, selection, replace_string_1, index_switch_2)
        store_named_attribute_6 = g.StoreNamedAttribute.face.integer(mesh_3.current, selection, replace_string_1, index_switch_2)
        store_named_attribute_7 = g.StoreNamedAttribute.corner.integer(mesh_3.current, selection, replace_string_1, index_switch_2)
        index_switch_3 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute_4, store_named_attribute_5, store_named_attribute_6, store_named_attribute_7))
        rest_1.current.slice(find_in_string_1.first_found + 1.0, rest_1.current.length()) >> rest_1.next
        index_switch_3 >> mesh_3.next
        switch_4 = (integer.length() > 0).switch.geometry(switch_2, mesh_3.result)
        repeat_zone_2 = g.RepeatZone(vector.find(',').count + 1.0)
        rest_2 = repeat_zone_2.items.string(vector, 'Rest')
        mesh_4 = repeat_zone_2.items.geometry(switch_4, 'Mesh')
        find_in_string_2 = rest_2.current.find(',')
        switch_5 = (find_in_string_2.count > 0).switch.string(rest_2.current, rest_2.current.slice(length=find_in_string_2.first_found))
        replace_string_2 = switch_5.replace(' ', '')
        sample_nearest_surface_2 = g.SampleNearestSurface.vector(switch, g.NamedAttribute.vector(replace_string_2).o.attribute, group_id, sample_position, sample_group_id)
        index_switch_4 = g.IndexSwitch.vector(menu_switch_1.o.output, (sample_nearest_surface_2.o.value.point.evaluate(), sample_nearest_surface_2.o.value.edge.evaluate(), sample_nearest_surface_2.o.value.face.evaluate(), sample_nearest_surface_2.o.value.corner.evaluate()))
        store_named_attribute_8 = g.StoreNamedAttribute.point.vector(mesh_4.current, selection, replace_string_2, index_switch_4)
        store_named_attribute_9 = g.StoreNamedAttribute.edge.vector(mesh_4.current, selection, replace_string_2, index_switch_4)
        store_named_attribute_10 = g.StoreNamedAttribute.face.vector(mesh_4.current, selection, replace_string_2, index_switch_4)
        store_named_attribute_11 = g.StoreNamedAttribute.corner.vector(mesh_4.current, selection, replace_string_2, index_switch_4)
        index_switch_5 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute_8, store_named_attribute_9, store_named_attribute_10, store_named_attribute_11))
        rest_2.current.slice(find_in_string_2.first_found + 1.0, rest_2.current.length()) >> rest_2.next
        index_switch_5 >> mesh_4.next
        switch_6 = (vector.length() > 0).switch.geometry(switch_4, mesh_4.result)
        repeat_zone_3 = g.RepeatZone(color.find(',').count + 1.0)
        rest_3 = repeat_zone_3.items.string(color, 'Rest')
        mesh_5 = repeat_zone_3.items.geometry(switch_6, 'Mesh')
        find_in_string_3 = rest_3.current.find(',')
        switch_7 = (find_in_string_3.count > 0).switch.string(rest_3.current, rest_3.current.slice(length=find_in_string_3.first_found))
        replace_string_3 = switch_7.replace(' ', '')
        sample_nearest_surface_3 = g.SampleNearestSurface.color(switch, g.NamedAttribute.color(replace_string_3).o.attribute, group_id, sample_position, sample_group_id)
        index_switch_6 = g.IndexSwitch.color(menu_switch_1.o.output, (sample_nearest_surface_3.o.value.point.evaluate(), sample_nearest_surface_3.o.value.edge.evaluate(), sample_nearest_surface_3.o.value.face.evaluate(), sample_nearest_surface_3.o.value.corner.evaluate()))
        store_named_attribute_12 = g.StoreNamedAttribute.point.color(mesh_5.current, selection, replace_string_3, index_switch_6)
        store_named_attribute_13 = g.StoreNamedAttribute.edge.color(mesh_5.current, selection, replace_string_3, index_switch_6)
        store_named_attribute_14 = g.StoreNamedAttribute.face.color(mesh_5.current, selection, replace_string_3, index_switch_6)
        store_named_attribute_15 = g.StoreNamedAttribute.corner.color(mesh_5.current, selection, replace_string_3, index_switch_6)
        index_switch_7 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute_12, store_named_attribute_13, store_named_attribute_14, store_named_attribute_15))
        rest_3.current.slice(find_in_string_3.first_found + 1.0, rest_3.current.length()) >> rest_3.next
        index_switch_7 >> mesh_5.next
        (color.length() > 0).switch.geometry(switch_6, mesh_5.result) >> mesh_1
ASSET = OTransferAttributes
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
