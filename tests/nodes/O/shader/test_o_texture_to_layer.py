import bpy
import pytest

from tests.nodes.evaluation import close, mesh_object, render_pixels, render_scene


@pytest.mark.parametrize(
    "port,brightness,expected",
    [
        ("Color", 0.25, (0.25, 0.25, 0.25)),
        ("Alpha", 0.0, (0.0, 0.0, 0.0)),
        ("Alpha", 0.25, (0.4, 0.4, 0.4)),
        ("Roughness", 0.4, (0.3865535, 0.3865535, 0.3865535)),
        ("Normal", 0.25, (0.0, 0.0, 1.0)),
        ("Emission", 1.0, (0.0, 0.0, 0.0)),
        ("Emission", 6.0, (4.0, 4.0, 4.0)),
    ],
)
def test_o_texture_to_layer(port, brightness, expected, tmp_path):
    scene = render_scene(8)
    plane = mesh_object(
        [(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)],
        faces=[(0, 1, 2, 3)],
    )
    material = bpy.data.materials.new("Texture Layer")
    material.use_nodes = True
    plane.data.materials.append(material)
    tree = material.node_tree
    tree.nodes.clear()
    layer = tree.nodes.new("ShaderNodeGroup")
    layer.node_tree = bpy.data.node_groups["O Texture to Layer"]
    layer.inputs["Color Texture"].default_value = (brightness, brightness, brightness, 1)
    layer.inputs["Alpha Texture"].default_value = 0.8
    layer.inputs["Alpha Scale"].default_value = 0.5
    layer.inputs["Alpha Background"].default_value = 0
    emission = tree.nodes.new("ShaderNodeEmission")
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(layer.outputs[port], emission.inputs["Color"])
    tree.links.new(emission.outputs[0], out.inputs["Surface"])

    pixels = render_pixels(scene, tmp_path / "layer.exr")
    center = (4 * 8 + 4) * 4
    close(pixels[center:center + 4], (*expected, 1), tolerance=2e-4)
