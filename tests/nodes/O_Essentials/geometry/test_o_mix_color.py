import pytest

from tests.nodes.evaluation import close, evaluated_mesh, geometry_group


@pytest.mark.parametrize("factor", [0, 0.5, 1, "position"])
def test_o_mix_color(factor):
    obj, tree, node = geometry_group("O Mix Color", [(0, 0, 0), (0.5, 0, 0), (1, 0, 0)], port=None)
    a, b = (0.2, 0.4, 0.6, 0.2), (0.8, 0.6, 0.4, 0.8)
    node.inputs["A"].default_value = a
    node.inputs["B"].default_value = b
    factors = [0, 0.5, 1] if factor == "position" else [factor] * 3
    if factor == "position":
        position = tree.nodes.new("GeometryNodeInputPosition")
        separate = tree.nodes.new("ShaderNodeSeparateXYZ")
        tree.links.new(position.outputs["Position"], separate.inputs[0])
        tree.links.new(separate.outputs["X"], node.inputs["Factor"])
    else:
        node.inputs["Factor"].default_value = factors[0]
    store = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT_COLOR"
    store.domain = "POINT"
    store.inputs["Name"].default_value = "result"
    tree.links.new(tree.nodes["Group Input"].outputs["Geometry"], store.inputs["Geometry"])
    tree.links.new(node.outputs["Color"], store.inputs["Value"])
    tree.links.new(store.outputs["Geometry"], tree.nodes["Group Output"].inputs["Geometry"])
    colors = evaluated_mesh(obj).attributes["result"].data
    assert len(colors) == len(factors)
    for color, factor in zip(colors, factors):
        close(color.color, [x * (1 - factor) + y * factor for x, y in zip(a, b)])
