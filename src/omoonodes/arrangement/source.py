"""Remove generated layout from a copied tree before writing source."""

from .arrange import _remove_routes
from .common import merge_group_inputs


def clear_layout(tree):
    for frame in [node for node in tree.nodes if node.bl_idname == "NodeFrame"]:
        tree.nodes.remove(frame)
    _remove_routes(tree)
    merge_group_inputs(tree)
