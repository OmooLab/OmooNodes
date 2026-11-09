from math import trunc

import bpy
import pytest

from tests.nodes.evaluation import evaluated_mesh, geometry_group


@pytest.mark.parametrize("step,fps_base", [(1, 1.0), (4, 1.0), (4, 1.001)])
def test_o_scene_time_steps_in_frames(step, fps_base):
    obj, tree, node = geometry_group("O Scene Time", [(0, 0, 0)], port=None)
    node.inputs["Step"].default_value = step
    store = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"
    store.domain = "POINT"
    store.inputs["Name"].default_value = "Step Seconds"
    source = next(node for node in tree.nodes if node.type == "GROUP_INPUT")
    output = next(node for node in tree.nodes if node.type == "GROUP_OUTPUT")
    tree.links.new(source.outputs["Geometry"], store.inputs["Geometry"])
    tree.links.new(node.outputs["Step Seconds"], store.inputs["Value"])
    tree.links.new(store.outputs["Geometry"], output.inputs["Geometry"])

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.render.fps_base = fps_base
    for frame in (-29, -28, -1, 0, 6, 7, 27, 28, 29, 32):
        scene.frame_set(frame)
        seconds = evaluated_mesh(obj).attributes["Step Seconds"].data[0].value
        expected = trunc(frame / step) * step * fps_base / 30
        assert seconds == pytest.approx(expected, abs=1e-6), frame
