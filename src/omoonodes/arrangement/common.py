"""Node utilities from AnyImage (GPL-3.0-or-later)."""


def prepare_node_group(node_group):
    for node in list(node_group.nodes):
        for socket in node.outputs:
            socket.hide = not socket.is_linked
        if node.bl_idname == "NodeGroupInput" and not any(socket.is_linked for socket in node.outputs):
            node_group.nodes.remove(node)


def replace_link_source(node_group, link, source):
    multi = link.to_socket.is_multi_input
    replacement = node_group.links.new(source, link.to_socket)
    if multi:
        replacement.swap_multi_input_sort_id(link)
        node_group.links.remove(link)


def socket_links(socket):
    return sorted(socket.links, key=lambda link: link.multi_input_sort_id, reverse=True)


def merge_group_inputs(tree):
    """Normalize interface reads while preserving repeated multi-input links."""
    inputs = [node for node in tree.nodes if node.bl_idname == "NodeGroupInput"]
    if not inputs:
        return
    first = inputs[0]
    outputs = {socket.identifier: socket for socket in first.outputs}
    for node in inputs[1:]:
        for edge in list(tree.links):
            if edge.from_node != node:
                continue
            source = outputs[edge.from_socket.identifier]
            if edge.to_socket.is_multi_input and any(
                link.from_socket == source for link in edge.to_socket.links
            ):
                duplicate = tree.nodes.new("NodeReroute")
                tree.links.new(source, duplicate.inputs[0])
                source = duplicate.outputs[0]
            replace_link_source(tree, edge, source)
        tree.nodes.remove(node)
    first.name = "Group Input"


def origin_socket(socket):
    while socket.node.bl_idname == "NodeReroute" and socket.node.inputs[0].is_linked:
        socket = socket.node.inputs[0].links[0].from_socket
    return socket
