from bpy.types import ShaderNodeTree
from omoonodes import geometry as g, shader as s, TreeBuilder
from omoonodes.builder import CustomShaderGroup


class OEnsureUV(CustomShaderGroup):
    _name = "O Ensure UV"
    _color_tag = "VECTOR"

    def _build_group(self, tree: TreeBuilder[ShaderNodeTree]) -> None:
        vector = tree.inputs.vector("Vector", (0.0, 0.0), dimensions=2)
        vector_1 = tree.outputs.vector("Vector", (0.0, 0.0), dimensions=2)

        mix = g.Mix.vector(g.Math.less_than(abs(vector.x) + abs(vector.y) + abs(vector.z), 0.000001), vector, s.TextureCoordinate().o.uv, clamp_factor=True)

        mix.o.result_vector >> vector_1

ASSET = OEnsureUV

ASSET_METADATA = {
    "catalog_id": "1f098c57-6187-4e3a-95ba-d7e3d187c6d5",
}
