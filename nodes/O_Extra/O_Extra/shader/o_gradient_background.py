from nodes.O_Essentials.O_Essentials_ShaderNodes.shader.o_background import OBackground as OBackground
from nodes.O_Essentials.O_Essentials_ShaderNodes.shader.o_linear import OLinear as OLinear
from bpy.types import ShaderNodeTree
from nodes_tool import geometry as g, shader as s, TreeBuilder
from nodes_tool.builder import CustomShaderGroup

class OGradientBackground(CustomShaderGroup):
    _name = 'O Gradient Background'
    _color_tag = 'SHADER'
    _tree_properties = {'default_group_node_width': 160}

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        a = tree.inputs.color('A', (0.0, 0.0, 0.0, 1.0), description='Value of the first color input')
        b = tree.inputs.color('B', (1.0, 1.0, 1.0, 1.0), description='Value of the second color input')
        angle = tree.inputs.float('Angle', 0.0, description='Angle to rotate the input vector by', subtype='ANGLE')
        invert = tree.inputs.boolean('Invert', False)
        light = tree.inputs.color('Light', (0.0, 0.0, 0.0, 1.0), description='Color of the emitted light')
        strength = tree.inputs.float('Strength', 1.0, description='Strength of the emitted light', min_value=0.0, max_value=1000000.0)
        with tree.inputs.panel('Options', default_closed=True):
            transmission_cycles = tree.inputs.boolean('Transmission (Cycles)', False, description='Amount of mixing between the A and B inputs')
            location = tree.inputs.vector('Location', (0.0, 0.0), description='The amount of translation along each axis', dimensions=2, min_value=-1.0, max_value=1.0, subtype='FACTOR')
            scale = tree.inputs.float('Scale', 1.0, description='The amount of scaling along each axis', min_value=0.0, max_value=2.0)
        shader = tree.outputs.shader('Shader')
        mapping = s.Mapping.texture(s.Mapping.texture(s.TextureCoordinate().o.window, (0.5, 0.5, 0.5)), location, scale=scale)
        o_linear = OLinear(Angle=angle + 1.5707964, Vector=s.Mapping.texture(mapping, (-0.5, -0.5, -0.5)))
        mix = g.Mix.color(s.InvertColor(fac=invert, color=o_linear.o.gradient), a, b, clamp_factor=True)
        OBackground(Color=mix.o.result_color, Light=light, **{'Transmission (Cycles)': transmission_cycles}, _named_links=[('Strength', strength), ('Strength', 1.0)]) >> shader
ASSET = OGradientBackground

ASSET_METADATA = {
    "catalog_id": "90187864-01c8-45bc-99f1-66e7e746beb8",
}
