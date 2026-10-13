from tests.nodes.evaluation import geometry_group, assert_positions


def test_o_sharpen():
    # A symmetric pyramid fan has curved interior edges and a pinned boundary.
    vertices = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0), (0, 0, 1)]
    faces = [(i, (i + 1) % 4, 4) for i in range(4)]
    obj, tree, node = geometry_group("O Sharpen", vertices, faces=faces)
    node.inputs["Iterations"].default_value = 1
    node.inputs["Weight"].default_value = 0.5
    # All four neighbors lie on z=0 with equal curvature, so half weight gives z=0.5.
    assert_positions(obj, [*vertices[:4], (0, 0, 0.5)])
    node.inputs["Weight"].default_value = 0
    assert_positions(obj, vertices)
