from bpy.types import CompositorNodeTree
from omoonodes import geometry as g, compositor as c, TreeBuilder
from omoonodes.builder import CustomCompositorGroup


class OImageInfo(CustomCompositorGroup):
    _name = "O Image Info"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[CompositorNodeTree]) -> None:
        image = tree.inputs.color("Image", (0.8, 0.8, 0.8, 1.0), hide_value=True)
        relative_size = tree.outputs.float("Relative Size", min_value=0.0)

        _image_info = c.ImageInfo(image=image)
        separate_xyz = g.SeparateXYZ(vector=_image_info.o.dimensions)
        separate_xyz.o.x.max(separate_xyz.o.y) / 1024.0 >> relative_size

ASSET = OImageInfo

ASSET_METADATA = {
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
