from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class OSceneTime(CustomGeometryGroup):
    _name = "O Scene Time"
    _color_tag = "INPUT"

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        step = tree.inputs.integer("Step", 4, min_value=1, max_value=8)
        step_seconds = tree.outputs.float("Step Seconds")

        scene_time = g.SceneTime()
        frame = scene_time.o.frame
        stepped_frame = (frame / step).truncate() * step
        seconds_per_frame = scene_time.o.seconds / frame
        stepped_frame * seconds_per_frame >> step_seconds

ASSET = OSceneTime

ASSET_METADATA = {
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
