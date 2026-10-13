import bpy
import pytest

from tests.nodes.evaluation import close, coordinates, evaluated_mesh, geometry_group


@pytest.mark.parametrize("strength", [0, 1])
def test_o_random_jitter(strength):
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    obj, tree, node = geometry_group("O Random Jitter", vertices, faces=[(0, 1, 2)])
    node.inputs["Strength"].default_value = strength
    bpy.context.scene.frame_set(12)
    actual = coordinates(obj)
    mesh = evaluated_mesh(obj)
    assert (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) == (3, 3, 1)
    if strength == 0:
        for point, original in zip(actual, vertices):
            close(point, original)
        return
    assert max(abs(a - b) for point, original in zip(actual, vertices) for a, b in zip(point, original)) > 1e-4, actual
    bpy.context.scene.frame_set(20)
    coordinates(obj)
    bpy.context.scene.frame_set(12)
    for point, repeated in zip(actual, coordinates(obj)):
        close(point, repeated)
