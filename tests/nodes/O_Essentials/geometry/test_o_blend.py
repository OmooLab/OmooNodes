from tests.nodes.evaluation import geometry_group, mesh_object, select_index, assert_positions, source_geometry


def test_o_blend():
    vertices = [(0, 0, 0), (2, 0, 0), (0, 2, 0)]
    obj, tree, node = geometry_group("O Blend", vertices, faces=[(0, 1, 2)])
    source_geometry(tree, node, mesh_object([(x + 2, y - 2, z + 4) for x, y, z in vertices]))
    node.inputs["Factor"].default_value = 0.5
    select_index(tree, node, 1)
    assert_positions(obj, [vertices[0], (3, -1, 2), vertices[2]])
    node.inputs["Factor"].default_value = 0
    assert_positions(obj, vertices)
