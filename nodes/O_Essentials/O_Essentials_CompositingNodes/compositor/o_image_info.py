# Node-group asset "O Image Info" (CompositorNodeTree), dumped by nodebpy.assets.dump_library.
# Rebuild the library with nodebpy.assets.build_library (nodebpy build).
from bpy.types import CompositorNodeTree
from nodebpy import geometry as g, compositor as c, TreeBuilder
from nodebpy.builder import CustomCompositorGroup


class OImageInfo(CustomCompositorGroup):
    _name = "O Image Info"
    _color_tag = "INPUT"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[CompositorNodeTree]) -> None:
        image = tree.inputs.color("Image", (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0), hide_value=True)
        relative_size = tree.outputs.float("Relative Size", min_value=0.0)

        _image_info = c.ImageInfo(image=image)
        separate_xyz = g.SeparateXYZ()
        separate_xyz.o.x.max(separate_xyz.o.y) / 1024.0 >> relative_size

ASSET = OImageInfo

ASSET_METADATA = {
    "catalog_id": "99c91009-1ea6-4fc1-bf33-6351786a8df1",
}
