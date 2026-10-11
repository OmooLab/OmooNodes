"""Blender API differences behind the nodebpy authoring API."""

import bpy

PORT_PROPERTIES = {
    'CompositorNodeSetAlpha': {'Type': 'mode'},
    'GeometryNodeResampleCurve': {'Mode': 'mode'},
    'GeometryNodeSetCurveNormal': {'Mode': 'mode'},
    'GeometryNodeVolumeToMesh': {'Resolution Mode': 'resolution_mode'},
    'GeometryNodeDistributePointsInVolume': {'Mode': 'mode'},
    'GeometryNodeMeshToVolume': {'Resolution Mode': 'resolution_mode'},
    'GeometryNodeSubdivisionSurface': {'UV Smooth': 'uv_smooth', 'Boundary Smooth': 'boundary_smooth'},
    'GeometryNodeRaycast': {'Interpolation': 'mapping'},
    'GeometryNodeTransform': {'Mode': 'mode'},
    'FunctionNodeFindInString': {'Mode': 'mode'},
    'GeometryNodeMergeByDistance': {'Mode': 'mode'},
    'GeometryNodeTriangulate': {'Quad Method': 'quad_method', 'N-gon Method': 'ngon_method'},
    'CompositorNodeBlur': {'Type': 'filter_type'},
    'CompositorNodeFilter': {'Type': 'filter_type'},
}
OLD_DEFAULTS = {
    ('ShaderNodeBsdfPrincipled', 'Thin Wall'): False,
    ('GeometryNodeCaptureAttribute', 'Selection'): True,
    ('FunctionNodeFindInString', 'Mode'): 'From Start',
    ('GeometryNodeSubdivisionSurface', 'Quality'): 3,
    ('CompositorNodeDisplace', 'Interpolation'): 'Anisotropic',
    ('CompositorNodeDisplace', 'Extension X'): 'Clip',
    ('CompositorNodeDisplace', 'Extension Y'): 'Clip',
    ('CompositorNodeAlphaOver', 'Type'): 'Over',
    ('ShaderNodeBsdfDiffuse', 'Roughness'): 0.0,
}
INPUT_ALIASES = {
    'CompositorNodeGamma': {'Color': 'Image'},
    'CompositorNodeAlphaOver': {'Background': 'Image', 'Foreground': 'Image_001'},
    'CompositorNodeDisplace': {'Displacement': 'Vector'},
}


def create_node(tree, kind):
    if bpy.app.version < (5, 0, 0) and tree.bl_idname == 'CompositorNodeTree' and kind == 'ShaderNodeGamma':
        kind = 'CompositorNodeGamma'
    node = tree.nodes.new(kind)
    if kind == 'CompositorNodeDisplace' and 'X Scale' in node.inputs:
        node.inputs['X Scale'].default_value = 1
        node.inputs['Y Scale'].default_value = 1
    return node


def set_property(node, key, value):
    if not hasattr(node, key):
        if (key, value) in {('realize_to_point_domain', False), ('vector_dimensions', 3), ('ui_shortcut', 0)}:
            return
    setattr(node, key, value)


def input_value(node, name, value):
    if bpy.app.version >= (5, 0, 0):
        return name, value, False
    if name not in node.inputs:
        prop = PORT_PROPERTIES.get(node.bl_idname, {}).get(name)
        if prop and hasattr(node, prop):
            options = node.bl_rna.properties[prop].enum_items
            identifier = next((item.identifier for item in options if value in (item.identifier, item.name)), None)
            if identifier is None:
                raise ValueError(f'{node.bl_idname}.{name} does not support {value!r} in Blender 4.5')
            setattr(node, prop, identifier)
            return name, value, True
        pair = (node.bl_idname, name)
        if pair in OLD_DEFAULTS and isinstance(value, (bool, int, float, str)) and value == OLD_DEFAULTS[pair]:
            return name, value, True
        name = INPUT_ALIASES.get(node.bl_idname, {}).get(name, name)
    return name, value, False

def export_inputs(node, inputs, props, literal):
    if node.bl_idname in {'FunctionNodeCompare', 'FunctionNodeRandomValue'}:
        for socket in node.inputs:
            key = socket.identifier.lower().replace(' ', '_')
            if key in inputs:
                if socket.is_unavailable:
                    inputs.pop(key)
                else:
                    inputs[socket.name.lower().replace(' ', '_')] = inputs.pop(key)

    for new, old in INPUT_ALIASES.get(node.bl_idname, {}).items():
        old_key = old.lower().replace(' ', '_').replace('-', '_')
        if old_key in inputs:
            inputs[new.lower().replace(' ', '_').replace('-', '_')] = inputs.pop(old_key)
    for port, prop in PORT_PROPERTIES.get(node.bl_idname, {}).items():
        if hasattr(node, prop) and port not in node.inputs:
            value = getattr(node, prop)
            label = node.bl_rna.properties[prop].enum_items[value].name
            inputs[port.lower().replace(' ', '_').replace('-', '_')] = literal(label)
            props.pop(prop, None)
    return inputs, props

def prepare_export(tree):
    # 4.5 Displace scales become explicit vector multiplication in 5.2.
    for node in list(tree.nodes):
        if node.bl_idname != 'CompositorNodeDisplace' or 'X Scale' not in node.inputs:
            continue
        scales = [node.inputs[key] for key in ('X Scale', 'Y Scale')]
        if all(not socket.is_linked and socket.default_value == 1 for socket in scales):
            continue
        combine = tree.nodes.new('ShaderNodeCombineXYZ')
        multiply = tree.nodes.new('ShaderNodeVectorMath')
        multiply.operation = 'MULTIPLY'
        vector = node.inputs['Vector']
        if vector.is_linked:
            tree.links.new(vector.links[0].from_socket, multiply.inputs[0])
        else:
            multiply.inputs[0].default_value = vector.default_value
        for index, socket in enumerate(scales):
            if socket.is_linked:
                link = socket.links[0]
                tree.links.new(link.from_socket, combine.inputs[index])
                tree.links.remove(link)
            else:
                combine.inputs[index].default_value = socket.default_value
            socket.default_value = 1
        tree.links.new(combine.outputs[0], multiply.inputs[1])
        tree.links.new(multiply.outputs[0], vector)
