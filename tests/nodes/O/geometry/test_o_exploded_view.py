import pytest

from tests.nodes.evaluation import close, coordinates, geometry_group


@pytest.mark.parametrize(
    "scale,group_id,distance",
    [(0.0, -123456, 0.0), (1.0, -123456, 1.0), (1.0, 0, 0.0)],
)
def test_o_exploded_view(scale, group_id, distance):
    vertices = [
        (-2, 0, 0), (-1, 0, 0), (-1, 1, 0), (-2, 1, 0),
        (1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 1, 0),
    ]
    obj, tree, group = geometry_group(
        "O Exploded View", vertices, faces=[(0, 1, 2, 3), (4, 5, 6, 7)],
    )
    assert group.node_tree.is_modifier
    group.inputs["Scale"].default_value = scale
    group.inputs["Group ID"].default_value = group_id
    realize = tree.nodes.new("GeometryNodeRealizeInstances")
    output = next(node for node in tree.nodes if node.type == "GROUP_OUTPUT")
    tree.links.new(group.outputs["Geometry"], realize.inputs["Geometry"])
    tree.links.new(realize.outputs["Geometry"], output.inputs["Geometry"])

    actual = sorted(coordinates(obj))
    expected = sorted((x + (distance if x > 0 else -distance), y, z) for x, y, z in vertices)
    assert len(actual) == len(expected)
    for point, target in zip(actual, expected):
        close(point, target)
