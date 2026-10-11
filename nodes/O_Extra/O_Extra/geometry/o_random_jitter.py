from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_noise_texture import ONoiseTexture as ONoiseTexture
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_scene_time import OSceneTime as OSceneTime
from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup
from nodes.O_Essentials.O_Essentials_GeometryNodes.geometry.o_displace import ODisplace as ODisplace

class ORandomJitter(CustomGeometryGroup):
    _name = 'O Random Jitter'
    _color_tag = 'GEOMETRY'
    _tree_properties = {'is_modifier': True}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry('Geometry')
        strength = tree.inputs.float('Strength', 1.0, min_value=-10000.0, max_value=10000.0, structure_type='SINGLE', force_non_field=True)
        frequency = tree.inputs.float('Frequency', 2.0, description='Scale of the base noise octave', min_value=-1000.0, max_value=1000.0, structure_type='SINGLE', force_non_field=True)
        step_size = tree.inputs.integer('Step Size', 4, min_value=1, max_value=8, structure_type='SINGLE', force_non_field=True)
        geometry_1 = tree.outputs.geometry('Geometry')
        o_noise_texture = ONoiseTexture(Strength=0.1, W=OSceneTime(Step=step_size), Scale=frequency)
        ODisplace(Geometry=geometry, Strength=strength, Direction='Vector', Height=0.1, Vector=o_noise_texture.o.vector) >> geometry_1
ASSET = ORandomJitter

ASSET_METADATA = {
    "catalog_id": "90187864-01c8-45bc-99f1-66e7e746beb8",
}
