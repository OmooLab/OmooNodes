import bpy
from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_displace import ODisplace as ODisplace

class OOutline(CustomGeometryGroup):
    _name = 'O Outline'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'default_group_node_width': 160, 'node_tool_idname': 'geometry.o_outline', 'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        mesh = tree.inputs.geometry('Mesh')
        thickness = tree.inputs.float('Thickness', 0.009999999776482582, min_value=0.0010000000474974513, max_value=0.10000000149011612, structure_type='SINGLE', subtype='DISTANCE', force_non_field=True)
        color = tree.inputs.color('Color', (0.10000000149011612, 0.10000000149011612, 0.10000000149011612, 1.0))
        light = tree.inputs.float('Light', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        with tree.inputs.panel('Secondary (Eevee)', default_closed=True):
            secondary_eevee = tree.inputs.boolean('Secondary (Eevee)', False, is_panel_toggle=True)
            color_1 = tree.inputs.color('Color', (0.0, 0.0, 0.0, 1.0))
            threshold = tree.inputs.float('Threshold', 0.5, min_value=0.0, max_value=1.0)
        with tree.inputs.panel('Loose', default_closed=True):
            loose = tree.inputs.boolean('Loose', False, is_panel_toggle=True)
            weight = tree.inputs.float('Weight', 0.5, min_value=0.0, max_value=1.0, structure_type='SINGLE', subtype='FACTOR', force_non_field=True)
            frequency = tree.inputs.float('Frequency', 5.0, description='Scale of the base noise octave', min_value=0.0, max_value=10.0, structure_type='SINGLE', force_non_field=True)
            offset = tree.inputs.float('Offset', 0.0, min_value=-1000.0, max_value=1000.0, structure_type='SINGLE', force_non_field=True)
        with tree.inputs.panel('Options', default_closed=True):
            thickness_weight = tree.inputs.float('Thickness Weight', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
        geometry = tree.outputs.geometry('Geometry')
        float_curve = g.FloatCurve(value=g.NoiseTexture(w=offset, scale=frequency, noise_dimensions='4D', normalize=True).o.factor, items=((0.0, 0.0), (0.29999998211860657, 0.0), (0.699999988079071, 1.0), (1.0, 1.0)))
        float_curve.node.mapping.update()
        float_curve.node.mapping.curves[0].points[1].select = True
        store_named_attribute = mesh >> g.StoreNamedAttribute.point.color(name='o_primary', value=color) >> g.StoreNamedAttribute.point.float(name='o_light', value=light)
        set_material = g.SetMaterial(geometry=store_named_attribute, material=bpy.data.materials.get('O Outline'))
        set_material_1 = g.StoreNamedAttribute.point.color(store_named_attribute, name='o_secondary', value=color_1) >> g.StoreNamedAttribute.point.float(name='o_threshold', value=threshold) >> g.SetMaterial(material=bpy.data.materials.get('O Outline Extra'))
        switch = loose.switch.boolean(True, float_curve >= weight)
        store_named_attribute_1 = secondary_eevee.switch.geometry(set_material, set_material_1) >> g.StoreNamedAttribute.point.float(name='o_opacity', value=switch)
        vector_math = g.Normal().o.normal.face.evaluate() * (thickness * thickness_weight * switch).max(9.999999747378752e-06)
        set_shade_smooth = ODisplace(Geometry=store_named_attribute_1, Direction='Vector', Vector=vector_math) >> g.FlipFaces() >> g.SetShadeSmooth.face()
        join_geometry = g.JoinGeometry(geometry=(mesh, set_shade_smooth))
        join_geometry >> geometry
ASSET = OOutline
ASSET_METADATA = {'catalog_id': '90187864-01c8-45bc-99f1-66e7e746beb8'}
DATABLOCK_DEPENDENCIES = {'materials': ('O Outline', 'O Outline Extra')}
