import pytest

from tests.nodes.evaluation import evaluated_mesh, geometry_group


@pytest.mark.parametrize("point_count", [0, 2])
def test_o_pick_instance_point_cloud(point_count):
    obj, tree, group = geometry_group("O Pick Instance", [], port=None)
    points = tree.nodes.new("GeometryNodePoints")
    points.inputs["Count"].default_value = point_count
    realize = tree.nodes.new("GeometryNodeRealizeInstances")
    vertices = tree.nodes.new("GeometryNodePointsToVertices")
    output = next(node for node in tree.nodes if node.type == "GROUP_OUTPUT")

    tree.links.new(points.outputs["Points"], group.inputs["Geometry"])
    tree.links.new(group.outputs["Instance"], realize.inputs["Geometry"])
    tree.links.new(realize.outputs["Geometry"], vertices.inputs["Points"])
    tree.links.new(vertices.outputs["Mesh"], output.inputs["Geometry"])

    assert len(evaluated_mesh(obj).vertices) == point_count
