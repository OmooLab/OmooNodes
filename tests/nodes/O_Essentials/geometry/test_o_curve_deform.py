from tests.nodes.evaluation import geometry_group, mesh_object, select_index, assert_positions


def test_o_curve_deform():
    vertices = [(0, 0, -1), (0, 0, 0), (0, 0, 1)]
    obj, tree, node = geometry_group("O Curve Deform", vertices, edges=[(0, 1), (1, 2)])
    path = mesh_object([(2, 3, 0), (4, 3, 0), (4, 5, 0)], edges=[(0, 1), (1, 2)])
    info = tree.nodes.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = path
    curve = tree.nodes.new("GeometryNodeMeshToCurve")
    tree.links.new(info.outputs["Geometry"], curve.inputs["Mesh"])
    tree.links.new(curve.outputs["Curve"], node.inputs["Curve"])
    node.inputs["Fit to Curve"].default_value = True
    assert_positions(obj, [(2, 3, 0), (4, 3, 0), (4, 5, 0)])
    select_index(tree, node, 1)
    node.inputs["Weight"].default_value = 0.5
    assert_positions(obj, [vertices[0], (2, 1.5, 0), vertices[2]])
    node.inputs["Weight"].default_value = 0
    assert_positions(obj, vertices)
