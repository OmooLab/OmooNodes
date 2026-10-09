from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from .o_is_uv_split import OIsUVSplit
from .o_mask_by_selection import OMaskBySelection
from .o_uv_island import OUVIsland

class OTransferUV(CustomGeometryGroup):
    _name = 'O Transfer UV'
    _color_tag = 'ATTRIBUTE'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        source = tree.inputs.geometry('Source')
        menu = tree.inputs.menu('Menu', 'Face Corner', optional_label=True)
        fix = tree.inputs.float('Fix', 0.0, description='Amount of mixing between the A and B inputs', min_value=0.0, max_value=1.0, subtype='FACTOR')
        with tree.inputs.panel('Options', default_closed=True):
            uv_island = tree.inputs.menu('UV Island', 'Sample Position', expanded=True, optional_label=True)
            uv_island_1 = tree.inputs.integer('UV Island', 0, hide_value=True)
            fix_range = tree.inputs.float('Fix Range', 0.10000000149011612, min_value=0.0, max_value=1.0, subtype='FACTOR')
            uv = tree.inputs.string('UV', 'UVMap')
        mesh_1 = tree.outputs.geometry('Mesh')
        menu_switch = g.MenuSwitch.integer(menu, {'Face Corner': 0, 'Point': 1})
        attribute_statistic = g.AttributeStatistic.corner.vector(source, attribute=g.NamedAttribute.vector(uv).o.attribute)
        o_mask_by_selection = OMaskBySelection(Geometry=source, Selection=OIsUVSplit().o.same_island, Menu='Edge', Solid=True, **{'Smooth Iterations': 20})
        position = g.Position()
        map_range = (o_mask_by_selection >> g.SampleNearestSurface.float(value=o_mask_by_selection.o.mask)).o.value.map_range(1.0 - fix_range, to_max=fix.map_range(to_max=0.9900000095367432))
        mix = g.Mix.vector(map_range, position, position.o.position.face.evaluate(), clamp_factor=True)
        sample_index = g.SampleIndex.face.integer(source, OUVIsland(UV=uv), g.SampleNearest.face(source))
        index_switch = g.IndexSwitch.integer(menu_switch.o.output, (sample_index.o.value.face.evaluate(), sample_index.o.value.point.evaluate()))
        menu_switch_1 = g.MenuSwitch.integer(uv_island, {'Sample Position': index_switch, 'Custom': uv_island_1})
        sample_nearest_surface = g.SampleNearestSurface.vector(source, g.NamedAttribute.vector(uv).o.attribute, OUVIsland(UV=uv), mix.o.result_vector, menu_switch_1.o.output)
        store_named_attribute = g.StoreNamedAttribute.corner.vector_2d(mesh, name='UVMap', value=sample_nearest_surface.o.value)
        store_named_attribute_1 = g.StoreNamedAttribute.point.vector_2d(mesh, name='UVMap', value=sample_nearest_surface.o.value)
        index_switch_1 = g.IndexSwitch.geometry(menu_switch.o.output, (store_named_attribute, store_named_attribute_1))
        g.Compare(a=attribute_statistic.o.mean, b=0.0).o.result.switch.geometry(mesh, index_switch_1) >> mesh_1
ASSET = OTransferUV
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '304de8ab-a7d3-4df3-b6b2-4674d8814339'}
