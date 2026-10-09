from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OSmoothAttributes(CustomGeometryGroup):
    _name = 'O Smooth Attributes'
    _color_tag = 'ATTRIBUTE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        float = tree.inputs.string('Float', '', description='Separate with commas')
        vector = tree.inputs.string('Vector', '', description='Separate with commas')
        color = tree.inputs.string('Color', '', description='Separate with commas')
        on = tree.inputs.menu('on', 'Point', optional_label=True)
        iterations = tree.inputs.integer('Iterations', 1, description='How many times to blur the values for all elements', min_value=1, max_value=10)
        weight = tree.inputs.float('Weight', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        mesh_1 = tree.outputs.geometry('Mesh')
        menu_switch = g.MenuSwitch.integer(on, {'Point': 0, 'Edge': 1, 'Face': 2, 'Face Corner': 3})
        repeat_zone = g.RepeatZone(float.find(',').count + 1.0)
        rest = repeat_zone.items.string(float, 'Rest')
        mesh_2 = repeat_zone.items.geometry(mesh, 'Mesh')
        find_in_string = rest.current.find(',')
        switch = (find_in_string.count > 0).switch.string(rest.current, rest.current.slice(length=find_in_string.first_found))
        replace_string = switch.replace(' ', '')
        blur_attribute = g.NamedAttribute.float(replace_string).o.attribute.blur(iterations, weight)
        store_named_attribute = g.StoreNamedAttribute.point.float(mesh_2.current, selection, replace_string, blur_attribute)
        store_named_attribute_1 = g.StoreNamedAttribute.edge.float(mesh_2.current, selection, replace_string, blur_attribute)
        store_named_attribute_2 = g.StoreNamedAttribute.face.float(mesh_2.current, selection, replace_string, blur_attribute)
        store_named_attribute_3 = g.StoreNamedAttribute.corner.float(mesh_2.current, selection, replace_string, blur_attribute)
        index_switch = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute, store_named_attribute_1, store_named_attribute_2, store_named_attribute_3))
        rest.current.slice(find_in_string.first_found + 1.0, rest.current.length()) >> rest.next
        index_switch >> mesh_2.next
        switch_1 = (float.length() > 0).switch.geometry(mesh, mesh_2.result)
        repeat_zone_1 = g.RepeatZone(vector.find(',').count + 1.0)
        rest_1 = repeat_zone_1.items.string(vector, 'Rest')
        mesh_3 = repeat_zone_1.items.geometry(switch_1, 'Mesh')
        find_in_string_1 = rest_1.current.find(',')
        switch_2 = (find_in_string_1.count > 0).switch.string(rest_1.current, rest_1.current.slice(length=find_in_string_1.first_found))
        replace_string_1 = switch_2.replace(' ', '')
        blur_attribute_1 = g.NamedAttribute.vector(replace_string_1).o.attribute.blur(iterations, weight)
        store_named_attribute_4 = g.StoreNamedAttribute.point.vector(mesh_3.current, selection, replace_string_1, blur_attribute_1)
        store_named_attribute_5 = g.StoreNamedAttribute.edge.vector(mesh_3.current, selection, replace_string_1, blur_attribute_1)
        store_named_attribute_6 = g.StoreNamedAttribute.face.vector(mesh_3.current, selection, replace_string_1, blur_attribute_1)
        store_named_attribute_7 = g.StoreNamedAttribute.corner.vector(mesh_3.current, selection, replace_string_1, blur_attribute_1)
        index_switch_1 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute_4, store_named_attribute_5, store_named_attribute_6, store_named_attribute_7))
        rest_1.current.slice(find_in_string_1.first_found + 1.0, rest_1.current.length()) >> rest_1.next
        index_switch_1 >> mesh_3.next
        switch_3 = (vector.length() > 0).switch.geometry(switch_1, mesh_3.result)
        repeat_zone_2 = g.RepeatZone(color.find(',').count + 1.0)
        rest_2 = repeat_zone_2.items.string(color, 'Rest')
        mesh_4 = repeat_zone_2.items.geometry(switch_3, 'Mesh')
        find_in_string_2 = rest_2.current.find(',')
        switch_4 = (find_in_string_2.count > 0).switch.string(rest_2.current, rest_2.current.slice(length=find_in_string_2.first_found))
        replace_string_2 = switch_4.replace(' ', '')
        blur_attribute_2 = g.NamedAttribute.color(replace_string_2).o.attribute.blur(iterations, weight)
        store_named_attribute_8 = g.StoreNamedAttribute.point.color(mesh_4.current, selection, replace_string_2, blur_attribute_2)
        store_named_attribute_9 = g.StoreNamedAttribute.edge.color(mesh_4.current, selection, replace_string_2, blur_attribute_2)
        store_named_attribute_10 = g.StoreNamedAttribute.face.color(mesh_4.current, selection, replace_string_2, blur_attribute_2)
        store_named_attribute_11 = g.StoreNamedAttribute.corner.color(mesh_4.current, selection, replace_string_2, blur_attribute_2)
        index_switch_2 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute_8, store_named_attribute_9, store_named_attribute_10, store_named_attribute_11))
        rest_2.current.slice(find_in_string_2.first_found + 1.0, rest_2.current.length()) >> rest_2.next
        index_switch_2 >> mesh_4.next
        (color.length() > 0).switch.geometry(switch_3, mesh_4.result) >> mesh_1
ASSET = OSmoothAttributes
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
