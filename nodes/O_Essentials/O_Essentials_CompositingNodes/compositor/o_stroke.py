from bpy.types import CompositorNodeTree
from nodebpy import geometry as g, compositor as c, TreeBuilder
from nodebpy.builder import CustomCompositorGroup
from .o_image_info import OImageInfo

class OStroke(CustomCompositorGroup):
    _name = 'O Stroke'
    _color_tag = 'FILTER'
    _tree_properties = {'default_group_node_width': 180, 'is_strip_modifier': True}

    def _build_group(self, tree: TreeBuilder[CompositorNodeTree]) -> None:
        image = tree.inputs.color('Image', (0.5, 0.5, 0.5, 1.0), description='Value of the first color input', hide_value=True)
        matte = tree.inputs.float('Matte', 0.0, hide_value=True)
        depth = tree.inputs.float('Depth', 0.0, hide_value=True)
        normal = tree.inputs.vector('Normal', (0.0, 0.0, 0.0), hide_value=True)
        with tree.inputs.panel('General'):
            thickness = tree.inputs.float('Thickness', 1.0, min_value=1.0, max_value=10.0)
            color = tree.inputs.color('Color', (0.0, 0.0, 0.0, 1.0), description='Value of the second color input')
            light = tree.inputs.float('Light', 1.0, description='Amount of mixing between the A and B inputs', min_value=0.0, max_value=1.0, subtype='FACTOR')
        with tree.inputs.panel('Loose', default_closed=True):
            strength = tree.inputs.float('Strength', 0.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
            frequency = tree.inputs.float('Frequency', 2.0, description='Scale of the base noise octave', min_value=0.0, max_value=10.0)
            messy = tree.inputs.float('Messy', 0.0, description='Amount of distortion', min_value=0.0, max_value=1.0)
            offset = tree.inputs.float('Offset', 0.0, min_value=-1000.0, max_value=1000.0)
        with tree.inputs.panel('Options', default_closed=True):
            exposure = tree.inputs.float('Exposure', 0.0, min_value=-10.0, max_value=10.0)
            gamma = tree.inputs.float('Gamma', 1.0, description='Gamma correction value, applied as color^gamma.\nTypically used to convert from gamma encoded to linear color space, or in the reverse direction with 1/gamma', min_value=0.0010000000474974513, max_value=10.0)
            blur = tree.inputs.float('Blur', 50.0, min_value=10.0, max_value=100.0)
            matte_weight = tree.inputs.float('Matte Weight', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
            depth_weight = tree.inputs.float('Depth Weight', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
            normal_weight = tree.inputs.float('Normal Weight', 1.0, min_value=0.0, max_value=1.0, subtype='FACTOR')
            normal_threshold = tree.inputs.float('Normal Threshold', 0.20000000298023224, min_value=0.0, max_value=1.0, subtype='FACTOR')
        image_1 = tree.outputs.color('Image', (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0))
        stroke = tree.outputs.color('Stroke', (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0))
        o_image_info = OImageInfo(Image=image)
        clamp = g.Clamp.range(g.MapRange.float(c.Filter(image=depth, type='Laplace'), 0.10000000149011612, clamp=True).o.result, max=depth_weight)
        math_1 = thickness * o_image_info
        exposure_1 = c.Exposure(image=c.Blur(image=image, size=(math_1 * 10.0).max(blur), type='Flat'), exposure=exposure)
        math_2 = strength * (o_image_info.o.relative_size * 20.0)
        map_range = g.Math.greater_than(c.Filter(image=matte, type='Laplace'), 0.10000000149011612).o.value.map_range(0.10000000149011612)
        mix = g.Mix.color(light, color, exposure_1.o.image.gamma(gamma), blend_type='MULTIPLY', clamp_factor=True)
        noise_texture = g.NoiseTexture(w=offset, scale=frequency, distortion=messy, noise_dimensions='4D', normalize=True)
        separate_color = c.SeparateColor(image=c.Filter(image=normal, type='Laplace'))
        map_range_1 = separate_color.o.red.max(separate_color.o.green).max(separate_color.o.blue).map_range(normal_threshold)
        blur_1 = c.Blur(image=(clamp.o.result + map_range_1 * normal_weight + map_range * matte_weight) * 10.0, size=math_1, type='Fast Gaussian')
        vector_math = g.MapRange.vector(noise_texture.o.color, to_min=(-1.0, -1.0, -1.0), clamp=True).o.vector * g.CombineXYZ(x=math_2, y=math_2)
        displace = c.Displace(image=g.Math.greater_than(blur_1, 0.0010000000474974513), displacement=vector_math, interpolation='Anisotropic')
        set_alpha = c.SetAlpha(image=mix.o.result_color, alpha=g.Math.multiply(c.AntiAliasing(image=displace), c.SeparateColor(image=color).o.alpha))
        alpha_over = c.AlphaOver(background=image, foreground=set_alpha)
        alpha_over >> image_1
        set_alpha >> stroke
ASSET = OStroke
ASSET_METADATA = {'catalog_id': '2cd36519-46ee-428e-a751-5c3d0312efb2'}
