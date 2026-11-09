import math

from tests.nodes.evaluation import geometry_group, select_index, assert_positions


def test_o_transform():
    vertices = [(1, 0, 0), (0, 1, 0), (-1, 0, 0)]
    obj, tree, node = geometry_group("O Transform", vertices, faces=[(0, 1, 2)])
    node.inputs["Translation"].default_value = (1, 2, 3)
    node.inputs["Rotation"].default_value = (0, 0, math.pi / 2)
    node.inputs["Scale"].default_value = (2, 3, 1)
    select_index(tree, node, 0)
    assert_positions(obj, [(1, 4, 3), vertices[1], vertices[2]])
    tree.links.remove(node.inputs["Selection"].links[0])
    node.inputs["Selection"].default_value = False
    assert_positions(obj, vertices)
