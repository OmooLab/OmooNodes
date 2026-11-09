from tests.nodes.evaluation import geometry_group, mesh_object, select_index, assert_positions, source_geometry


def test_o_point_deform():
    vertices = [(0, 0, 0), (2, 0, 0), (0, 2, 0)]
    obj, tree, node = geometry_group("O Point Deform", vertices, faces=[(0, 1, 2)])
    source = mesh_object([(x, y, z + 2) for x, y, z in vertices])
    rest = source.data.attributes.new("rest", "FLOAT_VECTOR", "POINT")
    for item, point in zip(rest.data, vertices):
        item.vector = point
    source_geometry(tree, node, source)
    field = tree.nodes.new("GeometryNodeInputNamedAttribute")
    field.data_type = "FLOAT_VECTOR"
    field.inputs["Name"].default_value = "rest"
    tree.links.new(field.outputs["Attribute"], node.inputs["Rest Positon"])
    node.inputs["Weight"].default_value = 0.5
    node.inputs["Smooth Iterations"].default_value = 0
    select_index(tree, node, 0)
    assert_positions(obj, [(0, 0, 1), vertices[1], vertices[2]])
    node.inputs["Weight"].default_value = 0
    assert_positions(obj, vertices)
