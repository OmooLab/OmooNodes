import pytest

from tests.nodes.evaluation import close, coordinates, evaluated_mesh, geometry_group, select_index


@pytest.mark.parametrize("weight,selection", [(1, "all"), (0, "all"), (1, "none"), (1, "center")])
def test_o_smooth(weight, selection):
    vertices = [(x, y, float(x == 0 and y == 0)) for y in (-1, 0, 1) for x in (-1, 0, 1)]
    faces = [(i, i + 1, i + 4, i + 3) for i in (0, 1, 3, 4)]
    obj, tree, node = geometry_group("O Smooth", vertices, faces=faces)
    node.inputs["Iterations"].default_value = 1
    node.inputs["Weight"].default_value = weight
    if selection == "none":
        node.inputs["Selection"].default_value = False
    if selection == "center":
        select_index(tree, node, 4)
    actual = coordinates(obj)
    mesh = evaluated_mesh(obj)
    assert (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) == (9, 12, 4)
    if weight == 0 or selection == "none":
        for point, original in zip(actual, vertices):
            close(point, original)
        return
    assert 0 <= actual[4][2] < 1, actual
    close(actual[4][:2], (0, 0))
    for i, point in enumerate(actual):
        close(point, (-actual[8 - i][0], -actual[8 - i][1], actual[8 - i][2]))
        if selection == "center" and i != 4:
            close(point, vertices[i])
