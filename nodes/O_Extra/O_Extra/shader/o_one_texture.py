from bpy.types import ShaderNodeTree
from nodes_tool import geometry as g, shader as s, TreeBuilder
from nodes_tool.builder import CustomShaderGroup


class OOneTexture(CustomShaderGroup):
    _name = "O One Texture"
    _color_tag = "SHADER"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        color = tree.inputs.color("Color", (0.8, 0.8, 0.8, 1.0))
        alpha = tree.inputs.float("Alpha", 1.0, min_value=0.0, max_value=1.0)
        metallic = tree.inputs.float("Metallic", 0.0, description="Blends between a dielectric and metallic material model. At 0.0 the material consists of a diffuse or transmissive base layer, with a specular reflection layer on top. A value of 1.0 gives a fully specular reflection tinted with the base color, without diffuse reflection or transmission", min_value=0.0, max_value=1.0, subtype="FACTOR")
        ior = tree.inputs.float("IOR", 1.5, description="Index of Refraction (IOR) for specular reflection and transmission. For most materials, the IOR is between 1.0 (vacuum and air) and 4.0 (germanium). The default value of 1.5 is a good approximation for glass", min_value=1.0, max_value=1000.0)
        roughness_min = tree.inputs.float("Roughness Min", 0.1, description="Value of the first floating number input", min_value=0.0, max_value=1.0, subtype="FACTOR")
        roughness_max = tree.inputs.float("Roughness Max", 0.5, description="Value of the second floating number input", min_value=0.0, max_value=1.0, subtype="FACTOR")
        bump_distance = tree.inputs.float("Bump Distance", 0.05, description="Multiplier for the height value to control the overall distance for bump mapping", min_value=0.01, max_value=1.0)
        coat_weight = tree.inputs.float("Coat Weight", 0.0, description="Controls the intensity of the coat layer, both the reflection and the tinting. Typically should be zero or one for physically-based materials", min_value=0.0, max_value=1.0, subtype="FACTOR")
        sheen_weight = tree.inputs.float("Sheen Weight", 0.0, description="Intensity of the sheen layer, which simulates very small fibers on the surface", min_value=0.0, max_value=1.0, subtype="FACTOR")
        emission_strength = tree.inputs.float("Emission Strength", 0.0, description="Strength of the emitted light. A value of 1.0 ensures that the object in the image has the exact same color as the Emission Color", min_value=0.0, max_value=1000000.0)
        with tree.inputs.panel("Alpha", default_closed=True):
            alpha_min = tree.inputs.float("Alpha Min", 0.0, description="Value of the first floating number input", min_value=0.0, max_value=1.0, subtype="FACTOR")
            alpha_max = tree.inputs.float("Alpha Max", 1.0, description="Value of the second floating number input", min_value=0.0, max_value=1.0, subtype="FACTOR")
        with tree.inputs.panel("Subsurface", default_closed=True):
            subsurface_weight = tree.inputs.float("Subsurface Weight", 0.0, description="Blend between diffuse surface and subsurface scattering. Typically should be zero or one (either fully diffuse or subsurface)", min_value=0.0, max_value=1.0, subtype="FACTOR")
            subsurface_scale = tree.inputs.float("Subsurface Scale", 0.05, description="Scale factor of the subsurface scattering radius", min_value=0.0, max_value=10.0, subtype="DISTANCE")
            hue = tree.inputs.float("Hue", 0.5, description="Hue rotation offset, from 0 (-180°) to 1 (+180°). Note that 0 and 1 have the same result", min_value=0.0, max_value=1.0)
            saturation = tree.inputs.float("Saturation", 1.0, description="Value of 0 removes color from the image, making it black-and-white. A value greater than 1.0 increases saturation", min_value=0.0, max_value=2.0)
            value = tree.inputs.float("Value", 1.0, description="Value shift. 0 makes the color black, 1 keeps it the same, and higher values make it brighter", min_value=0.0, max_value=2.0)
        bsdf = tree.outputs.shader("BSDF")

        bump = s.Bump(distance=bump_distance, height=color)
        principled_bsdf = s.PrincipledBSDF(base_color=color, metallic=metallic, roughness=g.Mix.float(color, roughness_min, roughness_max, clamp_factor=True).o.result_float, ior=ior, alpha=g.Mix.float(alpha, alpha_min, alpha_max, clamp_factor=True).o.result_float, normal=bump, subsurface_weight=subsurface_weight, subsurface_radius=s.HueSaturationValue(hue=hue, saturation=saturation, value=value, color=color), subsurface_scale=subsurface_scale, coat_weight=coat_weight, coat_normal=bump, sheen_weight=sheen_weight, sheen_tint=color, emission_color=color, emission_strength=emission_strength)

        principled_bsdf >> bsdf

ASSET = OOneTexture
