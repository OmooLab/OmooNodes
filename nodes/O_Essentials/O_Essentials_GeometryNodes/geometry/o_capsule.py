from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OCapsule(CustomGeometryGroup):
    _name = 'O Capsule'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'node_tool_idname': 'geometry.o_capsule'}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        segments = tree.inputs.integer('Segments', 32, min_value=3, max_value=128)
        rings = tree.inputs.integer('Rings', 16, min_value=2, max_value=64)
        side_segments = tree.inputs.integer('Side Segments', 1, min_value=1, max_value=512)
        radius = tree.inputs.float('Radius', 1.0, min_value=0.0, subtype='DISTANCE')
        height = tree.inputs.float('Height', 2.0, min_value=0.0, subtype='DISTANCE')
        with tree.inputs.panel('Options', default_closed=True):
            top_cap = tree.inputs.boolean('Top Cap', True)
            bottom_cap = tree.inputs.boolean('Bottom Cap', True)
        mesh = tree.outputs.geometry('Mesh')
        top = tree.outputs.boolean('Top')
        side = tree.outputs.boolean('Side')
        bottom = tree.outputs.boolean('Bottom')
        uv_map = tree.outputs.vector('UV Map')
        cylinder = g.Cylinder.triangles(segments, side_segments, rings / 2.0, radius, height)
        boolean_math = ~cylinder.o.side
        boolean_math_1 = cylinder.o.top & boolean_math
        boolean_math_2 = cylinder.o.bottom & boolean_math
        math_1 = height / 2.0
        combine_xyz = g.CombineXYZ(z=g.MapRange.float(cylinder.o.top, to_min=math_1 * -1.0, to_max=math_1, clamp=True).o.result)
        switch = g.BooleanMath.subtract(top_cap, bottom_cap).o.boolean.switch.boolean(boolean_math_2, boolean_math_1)
        switch_1 = g.BooleanMath.nor(top_cap, bottom_cap).o.boolean.switch.boolean((top_cap & bottom_cap).switch.boolean(switch, boolean_math), boolean_math_1 & boolean_math_2)
        vector_math = g.Position().o.position * (1.0, 1.0, 0.0)
        math_2 = ((vector_math / radius).length() - 1.0) * 1.5707963705062866
        math_3 = (math_2 * g.MapRange.float(cylinder.o.top, to_min=1.0, to_max=-1.0, clamp=True).o.result).sin()
        cylinder >> g.SetPosition(selection=switch_1, position=(vector_math.normalize() * math_2.cos() + g.CombineXYZ(z=math_3)) * radius + combine_xyz) >> mesh
        cylinder.o.top >> top
        cylinder.o.side >> side
        cylinder.o.bottom >> bottom
        cylinder.o.uv_map >> uv_map
ASSET = OCapsule
ASSET_METADATA = {'catalog_id': '0218b41f-9d3f-4dd0-9491-5c56e57678db'}
