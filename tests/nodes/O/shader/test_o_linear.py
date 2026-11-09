import math

import bpy
import pytest

from tests.nodes.evaluation import close, mesh_object, render_pixels, render_scene


@pytest.mark.parametrize("angle,port", [(0, "Gradient"), (0, "Fac"), (math.pi / 2, "Gradient")])
def test_o_linear(angle, port, tmp_path):
    scene = render_scene(8)
    plane = mesh_object([(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)], faces=[(0, 1, 2, 3)])
    material = bpy.data.materials.new("Emission")
    material.use_nodes = True
    plane.data.materials.append(material)
    tree = material.node_tree
    tree.nodes.clear()
    node = tree.nodes.new("ShaderNodeGroup")
    node.node_tree = bpy.data.node_groups["O Linear"]
    emission = tree.nodes.new("ShaderNodeEmission")
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(emission.outputs[0], out.inputs["Surface"])
    node.inputs["Angle"].default_value = angle
    tree.links.new(node.outputs[port], emission.inputs["Color"])
    vectors = [(0.2, 0.3, 0), (0.8, 0.7, 0)] if port == "Gradient" else [(0.4, 0.3, 0), (0.6, 0.3, 0)]
    for i, vector in enumerate(vectors):
        node.inputs["Vector"].default_value = vector
        x = (vector[0] - 0.5) * math.cos(angle) - (vector[1] - 0.5) * math.sin(angle) + 0.5
        expected = float(x < 0.5) if port == "Fac" else x
        pixels = render_pixels(scene, tmp_path / f"sample-{i}.exr")
        close(pixels[(4 * 8 + 4) * 4: (4 * 8 + 4) * 4 + 4], (expected, expected, expected, 1), tolerance=2e-4)
