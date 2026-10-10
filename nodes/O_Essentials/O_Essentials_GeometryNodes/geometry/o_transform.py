from bpy.types import GeometryNodeTree
from nodes_tool import geometry as g, TreeBuilder
from nodes_tool.builder import CustomGeometryGroup
from .o_mask_by_selection import OMaskBySelection


class OTransform(CustomGeometryGroup):
    _name = "O Transform"
    _color_tag = "GEOMETRY"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        geometry = tree.inputs.geometry("Geometry")
        selection = tree.inputs.boolean("Selection", True, hide_value=True, hide_in_modifier=True)
        mode = tree.inputs.menu("Mode", "Components", optional_label=True)
        translation = tree.inputs.vector("Translation", (0.0, 0.0, 0.0), subtype="TRANSLATION")
        rotation = tree.inputs.rotation("Rotation", (0.0, 0.0, 0.0))
        scale = tree.inputs.vector("Scale", (1.0, 1.0, 1.0), subtype="XYZ")
        transform = tree.inputs.matrix("Transform")
        soft = tree.inputs.float("Soft", 0.0, min_value=0.0, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Options", default_closed=True):
            soft_iterations = tree.inputs.integer("Soft Iterations", 5, description="How many times to blur the values for all elements", min_value=1, max_value=20)
        geometry_1 = tree.outputs.geometry("Geometry")

        menu_switch = g.MenuSwitch.matrix(mode, {"Components": g.CombineTransform(translation=translation, rotation=rotation, scale=scale), "Matrix": transform})
        o_mask_by_selection = OMaskBySelection(Geometry=geometry, Selection=selection, Smooth=soft, **{"Smooth Iterations": soft_iterations})
        transform_point = g.Position().o.position.transform(menu_switch.o.output)
        mix = g.Mix.vector(o_mask_by_selection.o.mask, g.Position(), transform_point, clamp_factor=True)
        (
            (soft > 0.0).switch.geometry(g.SetPosition(geometry=geometry, selection=selection, position=transform_point), o_mask_by_selection >> g.SetPosition(position=mix.o.result_vector))
            >> geometry_1
        )

ASSET = OTransform

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "f223bfa5-ce4b-4f80-838a-eff17d3cf085",
}
