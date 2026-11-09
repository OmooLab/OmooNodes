from nodes.O.O_Base_Geometry.geometry.o_noise_texture import ONoiseTexture
from nodes.O.O_Base_Geometry.geometry.o_scene_time import OSceneTime
from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from nodes.O.O_Base_Geometry.geometry.o_displace import ODisplace

class ORandomJitter(CustomGeometryGroup):
    _name = 'O Random Jitter'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        strength = tree.inputs.float('Strength', 1.0, min_value=-10000.0, max_value=10000.0, structure_type='SINGLE', force_non_field=True)
        density = tree.inputs.float('Density', 2.0, description='Scale the noise across the geometry', min_value=-1000.0, max_value=1000.0, structure_type='SINGLE', force_non_field=True)
        step_size = tree.inputs.integer('Step Size', 1, min_value=1, max_value=8, structure_type='SINGLE', force_non_field=True)
        geometry_1 = tree.outputs.geometry('Geometry')
        speed = tree.inputs.float('Speed', 2.0, description='Scale the noise over time', min_value=-1000.0, max_value=1000.0, structure_type='SINGLE', force_non_field=True)
        # Move the existing socket into Options so saved modifier values keep their identifier.
        interface = tree.tree.interface
        options = interface.new_panel('Options', default_closed=True)
        interface.move_to_parent(interface.items_tree['Step Size'], options, 0)
        with tree.panel(options):
            offset = tree.inputs.float('Offset', 0.0, description='Offset the W coordinate of the noise', min_value=-1000.0, max_value=1000.0, structure_type='SINGLE', force_non_field=True)

        time = OSceneTime(Step=step_size).o.step_seconds
        position = g.Position().o.position * density
        o_noise_texture = ONoiseTexture(Strength=0.1, W=time * speed + offset, **{'Sample Position': position})
        ODisplace(Geometry=geometry, Strength=strength, Direction='Vector', Height=0.1, Vector=o_noise_texture.o.vector) >> geometry_1
ASSET = ORandomJitter

ASSET_METADATA = {
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
