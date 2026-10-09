from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class ONormalizeAttribute(CustomGeometryGroup):
    _name = 'O Normalize Attribute '
    _color_tag = 'ATTRIBUTE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        menu = tree.inputs.menu('Menu', 'Point', optional_label=True)
        geometry = tree.inputs.geometry('Geometry')
        selection = tree.inputs.boolean('Selection', True, hide_value=True)
        attribute = tree.inputs.float('Attribute', 0.0, hide_value=True)
        result = tree.outputs.float('Result')
        attribute_statistic = g.AttributeStatistic.point.float(geometry, selection, attribute)
        attribute_statistic_1 = g.AttributeStatistic.edge.float(geometry, selection, attribute)
        attribute_statistic_2 = g.AttributeStatistic.face.float(geometry, attribute)
        attribute_statistic_3 = g.AttributeStatistic.corner.float(geometry, selection, attribute)
        attribute_statistic_4 = g.AttributeStatistic.spline.float(geometry, selection, attribute)
        attribute_statistic_5 = g.AttributeStatistic.instance.float(geometry, selection, attribute)
        menu_switch = g.MenuSwitch.integer(menu, {'Point': 0, 'Edge': 1, 'Face': 2, 'Face Corner': 3, 'Spline': 4, 'Instance': 5})
        index_switch = g.IndexSwitch.float(menu_switch.o.output, (attribute_statistic.o.min, attribute_statistic_1.o.min, attribute_statistic_2.o.min, attribute_statistic_3.o.min, attribute_statistic_4.o.min, attribute_statistic_5.o.min))
        index_switch_1 = g.IndexSwitch.float(menu_switch.o.output, (attribute_statistic.o.max, attribute_statistic_1.o.max, attribute_statistic_2.o.max, attribute_statistic_3.o.max, attribute_statistic_4.o.max, attribute_statistic_5.o.max))
        attribute.map_range(index_switch, index_switch_1) >> result
ASSET = ONormalizeAttribute
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
