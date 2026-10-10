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


def origin_socket(socket):
    while socket.node.bl_idname == "NodeReroute" and socket.node.inputs[0].is_linked:
        socket = socket.node.inputs[0].links[0].from_socket
    return socket
