import pytest

from tests.nodes.evaluation import close, coordinates, geometry_group, select_index


@pytest.mark.parametrize("mode,distance,weight,selected_only", [
    ("Minimum Distance", 3, 1, False), ("Project", 3, 1, False),
    ("Project", 0.1, 1, False), ("Project", 3, 0.5, False), ("Project", 3, 1, True),
])
def test_o_project(mode, distance, weight, selected_only):
    vertices = [(0.2, 0.1, 0.5), (0.3, 0.2, -0.5), (1.5, 0, 0.25)]
    obj, tree, node = geometry_group("O Project", vertices)
    grid = tree.nodes.new("GeometryNodeMeshGrid")
    grid.inputs["Size X"].default_value = 2
    grid.inputs["Size Y"].default_value = 2
    tree.links.new(grid.outputs["Mesh"], node.inputs["Source"])
    menus = [socket for socket in node.inputs if socket.name == "Menu"]
    menus[0].default_value = mode
    menus[1].default_value = "Custom"
    node.inputs["Custom"].default_value = (0, 0, 1)
    node.inputs["Radius Offset"].default_value = 0
    node.inputs["Max Distance"].default_value = distance
    node.inputs["Weight"].default_value = weight
    if selected_only:
        select_index(tree, node, 0)
    expected = [(0.2, 0.1, 0), (0.3, 0.2, 0), vertices[2]]
    if mode == "Minimum Distance":
        expected[2] = (1, 0, 0)
    if distance < 0.5:
        expected = vertices
    if weight == 0.5:
        expected = [(0.2, 0.1, 0.25), (0.3, 0.2, -0.25), vertices[2]]
    if selected_only:
        expected[1] = vertices[1]
    actual = coordinates(obj)
    assert len(actual) == len(expected)
    for point, target in zip(actual, expected):
        close(point, target)
