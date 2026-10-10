"""Capture logical node data without layout or runtime identifiers."""

from __future__ import annotations

import hashlib
import json

SKIP = {
    "rna_type", "name", "name_full", "label", "select", "location", "location_absolute",
    "dimensions", "width", "height", "hide", "color", "use_custom_color", "parent",
    "inputs", "outputs", "internal_links", "id_data", "node_tree", "panel_states",
    "show_options", "show_preview", "show_texture", "warning_propagation",
    "active_index", "active_input_index", "active_output_index", "inspection_index",
    "single_input", "single_output", "active_item",
    "paired_output", "type", "bl_idname", "bl_label", "bl_description",
    "bl_icon", "bl_static_type", "bl_width_default", "bl_width_min", "bl_width_max",
    "bl_height_default", "bl_height_min", "bl_height_max", "bl_socket_idname",
}
LAYOUT = {"NodeFrame", "NodeReroute", "NodeGroupInput"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def properties(value, depth=0):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, set):
        return sorted(value)
    if hasattr(value, "id_type"):
        if value.id_type == "IMAGE":
            packed = [item.packed_file.data for item in value.packed_files]
            if not packed:
                raise ValueError(f"Image must be packed: {value.name}")
            return [value.id_type, value.name, {
                "data": [hashlib.sha256(data).hexdigest() for data in packed],
                "colorspace": value.colorspace_settings.name,
                "alpha_mode": value.alpha_mode,
            }]
        if value.id_type == "MATERIAL" and value.node_tree:
            return [value.id_type, value.name, digest(tree_graph(value.node_tree))]
        return [value.id_type, value.name]
    if type(value).__name__.startswith("bpy_prop_collection"):
        return [properties(item, depth + 1) for item in value]
    if depth > 10:
        raise ValueError(f"Unsupported nested configuration: {type(value).__name__}")
    if hasattr(value, "bl_rna"):
        result = {}
        for prop in value.bl_rna.properties:
            logical_name = prop.identifier == "name" and not hasattr(value, "inputs")
            if (prop.identifier in SKIP and not logical_name) or prop.identifier.startswith("bl_"):
                continue
            if prop.is_readonly and prop.type not in {"COLLECTION", "POINTER"}:
                continue
            child = getattr(value, prop.identifier)
            if prop.type == "POINTER" and child == value:
                continue
            try:
                result[prop.identifier] = properties(child, depth + 1)
            except ValueError as error:
                raise ValueError(f"{prop.identifier}.{error}") from error
        return result
    try:
        return [properties(item, depth + 1) for item in value]
    except TypeError as error:
        raise ValueError(f"Unsupported configuration: {type(value).__name__}") from error


def origin(socket):
    seen = set()
    while socket.node.bl_idname == "NodeReroute":
        if socket.node in seen:
            raise ValueError("Cyclic reroute chain")
        seen.add(socket.node)
        links = socket.node.inputs[0].links
        if not links:
            return None
        socket = links[0].from_socket
    return socket


def socket_key(socket):
    # Dynamic identifiers are allocation counters; active socket order is stable.
    sockets = socket.node.outputs if socket.is_output else socket.node.inputs
    if socket.node.type == "GROUP":
        matches = [item for item in sockets if item.name == socket.name]
        return [socket.name, matches.index(socket), socket.type]
    active = [item for item in sockets if not item.is_unavailable]
    if socket not in active:
        return ["unavailable", socket.identifier, socket.name, socket.type]
    return [active.index(socket), socket.name, socket.type]


def tree_graph(tree, memo=None):
    memo = {} if memo is None else memo
    if tree in memo:
        return memo[tree]
    interface = []
    for item in tree.interface.items_tree:
        data = {"kind": item.item_type, "name": item.name}
        for name in ("in_out", "socket_type", "default_value", "min_value", "max_value",
                     "subtype", "description", "force_non_field", "attribute_domain",
                     "default_attribute_name", "default_input", "hide_in_modifier"):
            if hasattr(item, name):
                value = getattr(item, name)
                # Blender 5.2 removed COLOR_GAMMA; its stale enum reads as "".
                data[name] = "NONE" if name == "subtype" and value == "" else properties(value)
        if getattr(item, "socket_type", "") == "NodeSocketVector":
            dimensions = getattr(item, "dimensions", 3)
            data["default_value"] = data["default_value"][:dimensions]
        interface.append(data)
    nodes = [node for node in tree.nodes if node.bl_idname not in LAYOUT]
    bases = {}
    configurations = []
    edges = []
    for node in nodes:
        values = []
        keys = {}
        scalar = None
        if node.bl_idname == "ShaderNodeVectorMath" and node.operation == "MULTIPLY":
            scalar = next((index for index, socket in enumerate(node.inputs[:2])
                           if socket.is_linked and origin(socket.links[0].from_socket).type == "VALUE"), None)
            if scalar is not None:
                keys[node.inputs[scalar]] = [1, "Scale", "VALUE"]
                keys[node.inputs[1 - scalar]] = [0, "Vector", "VECTOR"]
        for socket in node.inputs:
            if socket.is_unavailable:
                continue
            if not socket.is_linked and hasattr(socket, "default_value"):
                values.append([keys.get(socket, socket_key(socket)), properties(socket.default_value)])
            links = sorted(socket.links, key=lambda link: link.multi_input_sort_id, reverse=True)
            for index, link in enumerate(links):
                source = origin(link.from_socket)
                if source is None:
                    continue
                start = ("input", socket_key(source)[0]) if source.node.bl_idname == "NodeGroupInput" else source.node
                edges.append((start, socket_key(source), node, keys.get(socket, socket_key(socket)), index))
        try:
            configuration = properties(node)
        except ValueError as error:
            raise ValueError(f"{tree.name}/{node.name}: {error}") from error
        # Multiplying a vector by a linked scalar and Vector Math SCALE have
        # the same componentwise operation; nodebpy lowers the former to SCALE.
        if scalar is not None:
            configuration["operation"] = "SCALE"
        base = {"type": node.bl_idname, "properties": configuration, "defaults": values}
        if node.type == "GROUP":
            base["group"] = node.node_tree.name if node.node_tree else None
            if node.node_tree is not None:
                base["group_logic"] = digest(tree_graph(node.node_tree, memo))
        bases[node] = digest(base)
        configurations.append(base)
    colors = dict(bases)
    for _ in range(len(nodes)):
        incoming = {node: [] for node in nodes}
        for source, source_socket, target, target_socket, order in edges:
            source_color = source if isinstance(source, tuple) else colors[source]
            incoming[target].append([source_color, source_socket, target_socket, order])
        colors = {node: digest([bases[node], sorted(incoming[node], key=repr)]) for node in nodes}
    connections = []
    for source, source_socket, target, target_socket, order in edges:
        source_color = source if isinstance(source, tuple) else colors[source]
        connections.append([source_color, source_socket, colors[target], target_socket, order])
    result = {"type": tree.bl_idname, "interface": interface,
              "configurations": sorted(configurations, key=lambda value: json.dumps(value, sort_keys=True)),
              "pairings": sorted([colors[node], colors[node.paired_output]] for node in nodes
                                 if getattr(node, "paired_output", None) in colors),
              "nodes": sorted(colors.values()), "links": sorted(connections, key=repr)}
    memo[tree] = result
    return result
