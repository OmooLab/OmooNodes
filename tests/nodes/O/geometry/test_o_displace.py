from tests.nodes.evaluation import geometry_group, select_index, assert_positions


def test_o_displace():
    vertices = [(0, 0, 0), (2, 0, 0), (0, 2, 0)]
    obj, tree, node = geometry_group("O Displace", vertices, faces=[(0, 1, 2)])
    select_index(tree, node, 0)
    node.inputs["Strength"].default_value = 2
    node.inputs["Height"].default_value = 0.75
    node.inputs["Midlevel"].default_value = 0.25
    assert_positions(obj, [(0, 0, 1), vertices[1], vertices[2]])
    node.inputs["Direction"].default_value = "Vector"
    node.inputs["Vector"].default_value = (0.75, 0.25, -0.25)
    assert_positions(obj, [(1, 0, -1), vertices[1], vertices[2]])
    node.inputs["Strength"].default_value = 0
    assert_positions(obj, vertices)
