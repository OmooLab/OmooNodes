from tests.nodes.evaluation import close, coordinates, geometry_group, select_index, assert_positions


def test_o_relax():
    vertices = [(x, y, 0) for y in (-1, 0, 1) for x in (-1, 0, 1)]
    vertices[4] = (0.4, 0, 0)
    faces = [(i, i + 1, i + 4, i + 3) for i in (0, 1, 3, 4)]
    obj, tree, node = geometry_group("O Relax", vertices, faces=faces)
    node.inputs["Iterations"].default_value = 1
    select_index(tree, node, 4)
    actual = coordinates(obj)
    assert 0 <= actual[4][0] < 0.4, actual
    close(actual[4][1:], (0, 0))
    expected = list(vertices)
    expected[4] = actual[4]
    assert_positions(obj, expected)
    node.inputs["Weight"].default_value = 0
    assert_positions(obj, vertices)
