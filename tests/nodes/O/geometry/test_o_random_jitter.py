import bpy
import pytest

from tests.nodes.evaluation import close, coordinates, evaluated_mesh, geometry_group


def test_o_random_jitter_interface():
    interface = bpy.data.node_groups["O Random Jitter"].interface.items_tree
    inputs = [item.name for item in interface if item.item_type == "SOCKET" and item.in_out == "INPUT"]
    assert inputs == ["Geometry", "Strength", "Density", "Speed", "Step Size", "Offset"]
    step = interface["Step Size"]
    assert step.default_value == 1
    assert step.parent.name == "Options" and step.parent.default_closed
    offset = interface["Offset"]
    assert offset.default_value == 0
    assert offset.parent == step.parent


@pytest.mark.parametrize("strength", [0, 1])
def test_o_random_jitter(strength):
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    obj, tree, node = geometry_group("O Random Jitter", vertices, faces=[(0, 1, 2)])
    node.inputs["Strength"].default_value = strength
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_set(6)
    actual = coordinates(obj)
    mesh = evaluated_mesh(obj)
    assert (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) == (3, 3, 1)
    if strength == 0:
        for point, original in zip(actual, vertices):
            close(point, original)
        return
    assert max(abs(a - b) for point, original in zip(actual, vertices) for a, b in zip(point, original)) > 1e-4, actual
    scene.frame_set(7)
    assert any(abs(a - b) > 1e-4 for point, later in zip(actual, coordinates(obj)) for a, b in zip(point, later))
    scene.frame_set(6)
    for point, repeated in zip(actual, coordinates(obj)):
        close(point, repeated)


@pytest.mark.parametrize("speed,density", [(0.0, 2.0), (2.0, 0.0)])
def test_o_random_jitter_speed_and_density(speed, density):
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    obj, _, node = geometry_group("O Random Jitter", vertices, faces=[(0, 1, 2)])
    node.inputs["Speed"].default_value = speed
    node.inputs["Density"].default_value = density
    node.inputs["Step Size"].default_value = 4
    scene = bpy.context.scene

    scene.frame_set(13)
    first = coordinates(obj)
    scene.frame_set(14)
    for point, held in zip(first, coordinates(obj)):
        close(point, held)

    offsets = [tuple(value - base for value, base in zip(point, original)) for point, original in zip(first, vertices)]
    spatial_variation = max(abs(a - b) for offset in offsets[1:] for a, b in zip(offset, offsets[0]))
    scene.frame_set(21)
    temporal_variation = max(abs(a - b) for point, later in zip(first, coordinates(obj)) for a, b in zip(point, later))
    assert (spatial_variation > 1e-4) == (density > 0)
    assert (temporal_variation > 1e-4) == (speed > 0)


def test_o_random_jitter_offset():
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    obj, _, node = geometry_group("O Random Jitter", vertices, faces=[(0, 1, 2)])
    node.inputs["Speed"].default_value = 0
    bpy.context.scene.frame_set(13)

    original = coordinates(obj)
    node.inputs["Offset"].default_value = 0.75
    shifted = coordinates(obj)
    assert any(abs(a - b) > 1e-4 for before, after in zip(original, shifted) for a, b in zip(before, after))

    node.inputs["Offset"].default_value = 0
    for before, restored in zip(original, coordinates(obj)):
        close(before, restored)
