from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class ORandomInstanceIndex(CustomGeometryGroup):
    _name = 'O Random Instance Index'
    _color_tag = 'INPUT'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        a = tree.inputs.integer('A', 10, min_value=0, max_value=100000)
        b = tree.inputs.integer('B', 5, min_value=0, max_value=100000)
        c_ = tree.inputs.integer('C', 2, min_value=0, max_value=100000)
        d = tree.inputs.integer('D', 1, min_value=0, max_value=100000)
        e = tree.inputs.integer('E', 0, min_value=0, max_value=100000)
        with tree.inputs.panel('Options'):
            seed = tree.inputs.integer('Seed', 0, min_value=-10000, max_value=10000)
        instance_index = tree.outputs.integer('Instance Index')
        math_1 = g.Math(value=a, value_001=b)
        math_2 = math_1.o.value + c_
        math_3 = math_2 + d
        random_value = g.RandomValue.integer(max=math_3 + e - 1.0, seed=seed)
        switch = g.Compare.integer.greater_equal(random_value, math_2).o.result.switch.integer(2, g.Compare.integer.greater_equal(random_value, math_3).o.result.switch.integer(3, 4))
        (random_value >= a).switch.integer(true=g.Compare.integer.greater_equal(random_value, math_1).o.result.switch.integer(1, switch)) >> instance_index
ASSET = ORandomInstanceIndex
ASSET_METADATA = {'author': 'Ma Nan', 'copyright': 'Omoo Lab', 'catalog_id': '1f098c57-6187-4e3a-95ba-d7e3d187c6d5'}
