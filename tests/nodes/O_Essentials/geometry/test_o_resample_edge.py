import pytest

from tests.nodes.evaluation import close, coordinates, evaluated_mesh, geometry_group


@pytest.mark.parametrize("length,selected_only", [(0.5, False), (1, False), (0.75, False), (0.5, True)])
def test_o_resample_edge(length, selected_only):
    vertices = [(0, 0, 0), (2, 0, 0)]
    edges = [(0, 1)]
    if selected_only:
        vertices += [(0, 2, 0), (2, 2, 0)]
        edges += [(2, 3)]
    obj, tree, node = geometry_group("O Resample Edge", vertices, edges, port="Edge")
    node.inputs["Length"].default_value = length
    if selected_only:
        attr = obj.data.attributes.new("selected", "BOOLEAN", "POINT")
        for i, item in enumerate(attr.data):
            item.value = i < 2
        field = tree.nodes.new("GeometryNodeInputNamedAttribute")
        field.data_type = "BOOLEAN"
        field.inputs["Name"].default_value = "selected"
        tree.links.new(field.outputs["Attribute"], node.inputs["Selection"])
    actual = sorted(coordinates(obj))
    # Blender Length mode uses floor(total / length) segments with uniform spacing.
    segments = int(2 / length)
    expected_x = [2 * i / segments for i in range(segments + 1)]
    expected = [(x, 0, 0) for x in expected_x]
    if selected_only:
        expected += [(0, 2, 0), (2, 2, 0)]
    assert len(actual) == len(expected), (actual, expected)
    for point, target in zip(actual, sorted(expected)):
        close(point, target)
    mesh = evaluated_mesh(obj)
    assert len(mesh.edges) == len(expected_x) - 1 + (selected_only)
    assert len(mesh.polygons) == 0
