from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OStoreSelection(CustomGeometryGroup):
    _name = 'O Store Selection'
    _color_tag = 'ATTRIBUTE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        menu = tree.inputs.menu('Menu', 'Point', optional_label=True)
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        name = tree.inputs.string('Name', '')
        geometry_1 = tree.outputs.geometry('Geometry')
        join_strings = g.JoinStrings((g.String(string='o_selection'), name), delimiter=':')
        store_named_attribute = g.StoreNamedAttribute.point.boolean(geometry, selection.point.evaluate(), join_strings, True)
        store_named_attribute_1 = g.StoreNamedAttribute.edge.boolean(geometry, selection.edge.evaluate(), join_strings, True)
        store_named_attribute_2 = g.StoreNamedAttribute.face.boolean(geometry, selection.face.evaluate(), join_strings, True)
        store_named_attribute_3 = g.StoreNamedAttribute.corner.boolean(geometry, selection.corner.evaluate(), join_strings, True)
        store_named_attribute_4 = g.StoreNamedAttribute.spline.boolean(geometry, selection.spline.evaluate(), join_strings, True)
        store_named_attribute_5 = g.StoreNamedAttribute.instance.boolean(geometry, selection.instance.evaluate(), join_strings, True)
        store_named_attribute_6 = g.StoreNamedAttribute.layer.boolean(geometry, selection.layer.evaluate(), join_strings, True)
        menu_switch = g.MenuSwitch.geometry(menu, {'Point': store_named_attribute, 'Edge': store_named_attribute_1, 'Face': store_named_attribute_2, 'Face Corner': store_named_attribute_3, 'Spline': store_named_attribute_4, 'Instance': store_named_attribute_5, 'Layer': store_named_attribute_6})
        (name.length() > 0).switch.geometry(geometry, menu_switch) >> geometry_1
ASSET = OStoreSelection
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
