from bpy.types import GeometryNodeTree
from nodebpy import geometry as g, TreeBuilder
from nodebpy.builder import CustomGeometryGroup

class OSceneTime(CustomGeometryGroup):
    _name = 'O Scene Time'
    _color_tag = 'INPUT'

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        step = tree.inputs.integer('Step', 4, min_value=1, max_value=8)
        step_seconds = tree.outputs.float('Step Seconds')
        scene_time = g.SceneTime()
        math_1 = scene_time.o.seconds / scene_time.o.frame * step
        (scene_time.o.seconds / math_1).truncate() * math_1 >> step_seconds
ASSET = OSceneTime
ASSET_METADATA = {'catalog_id': '99c91009-1ea6-4fc1-bf33-6351786a8df1'}
