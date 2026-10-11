"""Remove generated layout from a copied tree before writing source."""

from .arrange import _remove_routes
from .common import replace_link_source


def clear_layout(tree):
    for frame in [node for node in tree.nodes if node.bl_idname == "NodeFrame"]:
        tree.nodes.remove(frame)
    _remove_routes(tree)
    inputs = [node for node in tree.nodes if node.bl_idname == "NodeGroupInput"]
    if not inputs:
        return
    first = inputs[0]
    for node in inputs[1:]:
        for edge in list(tree.links):
            if edge.from_node == node:
                source = next(socket for socket in first.outputs if socket.identifier == edge.from_socket.identifier)
                replace_link_source(tree, edge, source)
        tree.nodes.remove(node)
    first.name = "Group Input"
