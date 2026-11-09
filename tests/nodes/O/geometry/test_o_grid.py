import bpy
import pytest

from tests.nodes.evaluation import close, evaluated_mesh, geometry_group, mesh_object


def test_o_grid_default_modifier():
    obj = mesh_object([(10, 0, 0)])
    group = bpy.data.node_groups["O Grid"]
    assert group.is_modifier
    inputs = [item for item in group.interface.items_tree if item.in_out == "INPUT"]
    assert [item.name for item in inputs] == ["Size X", "Size Y", "Subdivide", "Thickness"]
    assert [item.default_value for item in inputs] == [1, 1, 0, 0]
    assert inputs[2].max_value == 8
    obj.modifiers.new("Grid", "NODES").node_group = group

    mesh = evaluated_mesh(obj)
    assert len(mesh.polygons) == 1
    close(mesh.polygons[0].normal, (0, 0, 1))
    assert {tuple(vertex.co) for vertex in mesh.vertices} == {
        (-0.5, -0.5, 0), (-0.5, 0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0),
    }


@pytest.mark.parametrize(
    "size_x,size_y,subdivide,thickness,face_count,vertex_count",
    [(2, 1, 0, 0, 2, 6), (1, 2, 3, 0, 128, 153), (2, 1, 2, 1.2, 184, 186)],
)
def test_o_grid_size_and_uv(size_x, size_y, subdivide, thickness, face_count, vertex_count):
    obj, tree, node = geometry_group("O Grid", [], port=None)
    for name, value in zip(("Size X", "Size Y", "Subdivide", "Thickness"), (size_x, size_y, subdivide, thickness)):
        node.inputs[name].default_value = value
    store = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT_VECTOR"
    store.domain = "CORNER"
    store.inputs["Name"].default_value = "Socket UV"
    output = next(node for node in tree.nodes if node.type == "GROUP_OUTPUT")
    tree.links.new(node.outputs["Geometry"], store.inputs["Geometry"])
    tree.links.new(node.outputs["UV Map"], store.inputs["Value"])
    tree.links.new(store.outputs["Geometry"], output.inputs["Geometry"])

    mesh = evaluated_mesh(obj)
    assert len(mesh.polygons) == face_count
    assert len(mesh.vertices) == vertex_count
    x, y, z = zip(*(vertex.co for vertex in mesh.vertices))
    close((min(x), max(x), min(y), max(y), min(z), max(z)),
          (-size_x / 2, size_x / 2, -size_y / 2, size_y / 2, -thickness / 2, thickness / 2))
    uv_map = mesh.uv_layers["UVMap"].uv
    socket_uv = mesh.attributes["Socket UV"].data
    for loop, uv, field_uv in zip(mesh.loops, uv_map, socket_uv):
        vertex = mesh.vertices[loop.vertex_index].co
        expected = (vertex.x / size_x + 0.5, vertex.y / size_y + 0.5)
        close(uv.vector, expected)
        close(field_uv.vector, (*expected, 0))
