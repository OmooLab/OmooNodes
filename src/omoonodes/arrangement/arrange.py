"""Materialize the joint calculation and connection plan in node trees."""

from .branches import calculation_blocks
from .dimensions import estimate_node_dimensions, visible_socket
from .layout import plan_layout
from .common import merge_group_inputs, origin_socket, prepare_node_group, replace_link_source, socket_links


def _remove_routes(node_group):
    previous = [node for node in node_group.nodes if node.bl_idname == "NodeReroute" and node.inputs[0].is_linked]

    for node in [node for node in node_group.nodes if node not in previous]:
        for socket in node.inputs:
            links = socket_links(socket)
            if not any(link.from_node in previous for link in links):
                continue
            if not socket.is_multi_input:
                replace_link_source(node_group, links[0], origin_socket(links[0].from_socket))
                continue
            sources = [origin_socket(link.from_socket) for link in links]
            for link in links:
                node_group.links.remove(link)
            seen = set()
            for source in reversed(sources):
                original = source
                if source in seen:
                    # Blender coalesces identical direct links; retain repeated inputs.
                    duplicate = node_group.nodes.new("NodeReroute")
                    node_group.links.new(source, duplicate.inputs[0])
                    source = duplicate.outputs[0]
                seen.add(original)
                node_group.links.new(source, socket)
    for node in previous:
        node_group.nodes.remove(node)


def _input_regions(targets, positions, sizes):
    """Share a read between nearby consumers in the same layout column."""
    regions = []
    for target in sorted(targets, key=lambda i: (*positions[i], i)):
        x, y = positions[target]
        height = sizes[target].height
        if regions:
            region = regions[-1]
            left, top = positions[region[0]]
            bottom = max(positions[i][1] + sizes[i].height for i in region)
            tallest = max(sizes[i].height for i in region)
            # Match normal node spacing, and keep a shared read within one
            # compact region rather than chaining through an entire column.
            if abs(x - left) <= 32 and y - bottom <= 64 and max(bottom, y + height) - top <= max(320, tallest, height):
                region.append(target)
                continue
        regions.append([target])
    return regions


def _localize_inputs(node_group, nodes, positions, sizes):
    """Place interface reads by consumer proximity, independently of block roles."""
    ids = {node: i for i, node in enumerate(nodes)}
    for node in list(nodes):
        if node.bl_idname != "NodeGroupInput":
            continue
        uses = [edge for edge in node_group.links if edge.from_node == node]
        targets = {ids[edge.to_node] for edge in uses}
        reads = {}
        for region in _input_regions(targets, positions, sizes):
            read = node if not reads else node_group.nodes.new("NodeGroupInput")
            reads.update({target: read for target in region})
        for edge in uses:
            read = reads[ids[edge.to_node]]
            if read == node:
                continue
            source = next(socket for socket in read.outputs if socket.identifier == edge.from_socket.identifier)
            replace_link_source(node_group, edge, source)


def _plan_nodes(node_group):
    """Use stable connection order for both the initial and localized layouts."""
    nodes = list(node_group.nodes)
    sizes = {i: estimate_node_dimensions(node) for i, node in enumerate(nodes)}
    # Inactive sockets retain authored links but have no editor row to route.
    edges = sorted(
        (edge for edge in node_group.links
         if not edge.from_socket.is_unavailable and not edge.to_socket.is_unavailable),
        key=lambda edge: (edge.from_node.name, edge.from_socket.identifier,
                          edge.to_node.name, edge.to_socket.identifier, edge.multi_input_sort_id),
    )
    blocks, core = calculation_blocks(nodes, edges)
    positions, routes = plan_layout(nodes, edges, sizes, blocks, core)
    return nodes, sizes, edges, positions, routes


def arrange_nodes(node_group):
    """Arrange calculation bodies and shared channels before creating reroutes."""
    for frame in [node for node in node_group.nodes if node.bl_idname == "NodeFrame"]:
        for child in [node for node in node_group.nodes if node.parent == frame]:
            position = tuple(child.location_absolute)
            child.parent = None
            child.location = position
        node_group.nodes.remove(frame)
    _remove_routes(node_group)
    merge_group_inputs(node_group)
    prepare_node_group(node_group)
    nodes = list(node_group.nodes)
    if not nodes:
        return
    for node in nodes:
        node.select = False
        if node.bl_idname in {"ShaderNodeMath", "ShaderNodeVectorMath", "FunctionNodeIntegerMath"}:
            node.hide = all(socket.is_linked for socket in node.inputs if visible_socket(socket))
    nodes, sizes, edges, positions, routes = _plan_nodes(node_group)
    _localize_inputs(node_group, nodes, positions, sizes)
    if len(node_group.nodes) != len(nodes):
        prepare_node_group(node_group)
        nodes, sizes, edges, positions, routes = _plan_nodes(node_group)
    for i, (x, y) in positions.items():
        nodes[i].select = False
        nodes[i].location = (x, -y)
        nodes[i].width = sizes[i].width
    cache = {}
    for index, path in routes.items():
        edge = edges[index]
        source = edge.from_socket
        for x, y in path[1:-1]:
            key = (source, round(x, 4), round(y, 4))
            reroute = cache.get(key)
            if reroute is None:
                reroute = node_group.nodes.new("NodeReroute")
                reroute.location = (x - 8, -y + 8)
                node_group.links.new(source, reroute.inputs[0])
                cache[key] = reroute
            source = reroute.outputs[0]
        if len(path) > 2:
            replace_link_source(node_group, edge, source)
    prepare_node_group(node_group)
