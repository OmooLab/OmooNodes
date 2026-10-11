from bpy.types import GeometryNodeTree
from omoonodes import geometry as g, TreeBuilder
from omoonodes.builder import CustomGeometryGroup


class ONoiseTexture(CustomGeometryGroup):
    _name = "O Noise Texture"
    _color_tag = "TEXTURE"
    _tree_properties = {"default_group_node_width": 160}

    def _build_group(self, tree: TreeBuilder[GeometryNodeTree]) -> None:
        menu = tree.inputs.menu("Menu", "Mid-Range", optional_label=True)
        strength = tree.inputs.float("Strength", 2.0, min_value=0.0, max_value=10000.0)
        midlevel = tree.inputs.float("Midlevel", 0.0, min_value=-10000.0, max_value=10000.0)
        min = tree.inputs.float("Min", 0.0)
        max = tree.inputs.float("Max", 1.0)
        with tree.inputs.panel("Options", default_closed=True):
            w = tree.inputs.float("W", 0.0, min_value=-1000.0, max_value=1000.0)
            scale = tree.inputs.float("Scale", 1.0, description="Scale of the base noise octave", min_value=-1000.0, max_value=1000.0)
            detail = tree.inputs.float("Detail", 2.0, description="The number of noise octaves. Higher values give more detailed noise but increase render time", min_value=0.0, max_value=15.0)
            roughness = tree.inputs.float("Roughness", 0.5, description="Blend factor between an octave and its previous one. A value of zero corresponds to zero detail", min_value=0.0, max_value=1.0, subtype="FACTOR")
            lacunarity = tree.inputs.float("Lacunarity", 2.0, description="The difference between the scale of each two consecutive octaves. Larger values corresponds to larger scale for higher octaves", min_value=0.0, max_value=1000.0)
            distortion = tree.inputs.float("Distortion", 0.0, description="Amount of distortion", min_value=-1000.0, max_value=1000.0)
            sample_position = tree.inputs.vector("Sample Position", (0.0, 0.0, 0.0), hide_value=True, default_input="POSITION")
        vector = tree.outputs.vector("Vector")
        value = tree.outputs.float("Value")

        menu_switch = g.MenuSwitch.integer(menu, {"Mid-Range": 0, "Min-Max": 1})
        index_switch = g.IndexSwitch.float(menu_switch.o.output, (midlevel - strength, min))
        index_switch_1 = g.IndexSwitch.float(menu_switch.o.output, (midlevel + strength, max))
        noise_texture = g.NoiseTexture(vector=sample_position, w=w, scale=scale, detail=detail, roughness=roughness, lacunarity=lacunarity, distortion=distortion, noise_dimensions="4D", normalize=True)
        map_range = g.MapRange.vector(noise_texture.o.color, to_min=index_switch, to_max=index_switch_1, clamp=True)
        (
            noise_texture.o.factor.map_range(to_min=index_switch, to_max=index_switch_1)
            >> value
        )

        map_range.o.vector >> vector

ASSET = ONoiseTexture

ASSET_METADATA = {
    "author": "Ma Nan",
    "copyright": "Omoo Lab",
    "catalog_id": "2e34744f-a050-4efb-a7b7-c052b449fc5d",
}
