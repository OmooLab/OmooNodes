"""Small native fixtures and numerical assertions shared by behavior cases."""

import math

import bpy


def close(actual, expected, tolerance=1e-5):
    actual, expected = list(actual), list(expected)
    assert len(actual) == len(expected), f"length: actual={len(actual)}, expected={len(expected)}"
    differences = [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected))
                   if not math.isfinite(a) or not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)]
    assert not differences, f"(index, actual, expected)={differences[:8]}, count={len(differences)}, tolerance={tolerance}"


def mesh_object(vertices, edges=(), faces=()):
    mesh = bpy.data.meshes.new("Input")
    mesh.from_pydata(vertices, edges, faces)
    obj = bpy.data.objects.new("Input", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def geometry_group(name, vertices, edges=(), faces=(), port="Geometry"):
    obj = mesh_object(vertices, edges, faces)
    tree = bpy.data.node_groups.new("Evaluate", "GeometryNodeTree")
    tree.is_modifier = True
    tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    node = tree.nodes.new("GeometryNodeGroup")
    node.node_tree = bpy.data.node_groups[name]
    if port:
        tree.links.new(inp.outputs["Geometry"], node.inputs[port])
        tree.links.new(node.outputs[port], out.inputs["Geometry"])
    obj.modifiers.new("Evaluate", "NODES").node_group = tree
    return obj, tree, node


def evaluated_mesh(obj):
    bpy.context.view_layer.update()
    return obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data


def coordinates(obj):
    return [tuple(vertex.co) for vertex in evaluated_mesh(obj).vertices]


def select_index(tree, node, index):
    field = tree.nodes.new("GeometryNodeInputIndex")
    compare = tree.nodes.new("FunctionNodeCompare")
    compare.data_type = "INT"
    compare.operation = "EQUAL"
    inputs = [socket for socket in compare.inputs if socket.type == "INT" and not socket.is_unavailable]
    tree.links.new(field.outputs["Index"], inputs[0])
    inputs[1].default_value = index
    tree.links.new(compare.outputs["Result"], node.inputs["Selection"])


def render_scene(size):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.cycles.seed = 0
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 1
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.film_transparent = True
    scene.render.use_compositing = True
    scene.view_settings.view_transform = "Standard"
    scene.frame_set(1)
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (0, 0, 3)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2
    return scene


def render_pixels(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        pixels = list(image.pixels)
        assert pixels and all(math.isfinite(value) for value in pixels), "Invalid render output"
        return pixels
    finally:
        bpy.data.images.remove(image)


def assert_positions(obj, expected):
    actual = coordinates(obj)
    assert len(actual) == len(expected), (actual, expected)
    for point, target in zip(actual, expected):
        close(point, target)
    mesh = evaluated_mesh(obj)
    assert [tuple(edge.vertices) for edge in mesh.edges] == [tuple(edge.vertices) for edge in obj.data.edges]
    assert [tuple(face.vertices) for face in mesh.polygons] == [tuple(face.vertices) for face in obj.data.polygons]


def source_geometry(tree, node, source):
    info = tree.nodes.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = source
    tree.links.new(info.outputs["Geometry"], node.inputs["Source"])
