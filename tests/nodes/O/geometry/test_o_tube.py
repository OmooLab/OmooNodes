import math

import bpy
import pytest

from tests.nodes.evaluation import close, evaluated_mesh, mesh_object


@pytest.mark.parametrize(
    "radius,radius_scale,expected",
    [(None, 1.0, (0.1, 0.1)), ((0.0, 0.2), 1.5, (0.0, 0.3))],
)
def test_o_tube_radius(radius, radius_scale, expected):
    obj = mesh_object([(0, 0, 0), (0.5, 0, 0)], edges=[(0, 1)])
    if radius is not None:
        attribute = obj.data.attributes.new("radius", "FLOAT", "POINT")
        attribute.data.foreach_set("value", radius)

    group = bpy.data.node_groups["O Tube"]
    assert group.is_modifier
    modifier = obj.modifiers.new("Tube", "NODES")
    modifier.node_group = group
    socket = next(item for item in group.interface.items_tree if item.name == "Radius Scale")
    if hasattr(modifier, "properties"):
        getattr(modifier.properties.inputs, socket.identifier).value = radius_scale
    else:
        modifier[socket.identifier] = radius_scale
    obj.update_tag(refresh={"DATA"})

    mesh = evaluated_mesh(obj)
    assert mesh.polygons
    for x, expected_radius in zip((0.0, 0.5), expected):
        ring = [math.hypot(v.co.y, v.co.z) for v in mesh.vertices if abs(v.co.x - x) < 1e-6]
        assert ring
        close(ring, [expected_radius] * len(ring))
