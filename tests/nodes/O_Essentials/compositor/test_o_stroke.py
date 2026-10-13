import bpy

from tests.nodes.evaluation import close, render_pixels, render_scene


def test_o_stroke(tmp_path):
    size = 64
    scene = render_scene(size)
    scene.render.compositor_device = "CPU"
    if bpy.app.version < (5, 0, 0):
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
        out = tree.nodes.new("CompositorNodeComposite")
    else:
        tree = bpy.data.node_groups.new("Composite", "CompositorNodeTree")
        scene.compositing_node_group = tree
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        out = tree.nodes.new("NodeGroupOutput")
    image = bpy.data.images.new("Matte", width=size, height=size, float_buffer=True)
    image.colorspace_settings.name = "Non-Color"
    image.pixels[:] = [value for y in range(size) for x in range(size)
                      for value in (float(16 <= x < 48 and 16 <= y < 48),) * 3 + (1,)]
    image.pack()
    source = tree.nodes.new("CompositorNodeImage")
    source.image = image
    # A uniform image retains the matte's domain while isolating its contribution.
    uniform = bpy.data.images.new("Uniform", width=size, height=size, float_buffer=True)
    uniform.pixels[:] = [0.5, 0.5, 0.5, 1] * (size * size)
    uniform.pack()
    background = tree.nodes.new("CompositorNodeImage")
    background.image = uniform
    node = tree.nodes.new("CompositorNodeGroup")
    node.node_tree = bpy.data.node_groups["O Stroke"]
    tree.links.new(background.outputs["Image"], node.inputs["Image"])
    tree.links.new(source.outputs["Image"], node.inputs["Matte"])
    tree.links.new(node.outputs["Stroke"], out.inputs["Image"])
    node.inputs["Depth Weight"].default_value = 0
    node.inputs["Normal Weight"].default_value = 0
    node.inputs["Light"].default_value = 0
    opacity = 0.5
    expected_alpha = opacity ** 2
    node.inputs["Color"].default_value = (0.2, 0.4, 0.6, opacity)
    node.inputs["Offset"].default_value = 1.3
    node.inputs["Strength"].default_value = 0
    baseline = render_pixels(scene, tmp_path / "baseline.exr")
    alpha = baseline[3::4]
    assert max(alpha) > expected_alpha * 0.9, f"Empty or weak stroke: {max(alpha)}, opacity={opacity}"
    assert min(alpha) >= -1e-6 and max(alpha) <= expected_alpha + 1e-4, (min(alpha), max(alpha))
    close([alpha[32 * size + 32], alpha[0]], [0, 0], tolerance=1e-4)
    edge = [alpha[y * size + x] for y in range(12, 20) for x in range(24, 40)]
    assert max(edge) > expected_alpha * 0.9, f"Missing expected matte boundary: {max(edge)}"
    # Color alpha participates in both the color and mask, by design.
    close([max(alpha)], [expected_alpha], tolerance=1e-4)
    node.inputs["Light"].default_value = 1
    lit = render_pixels(scene, tmp_path / "lit.exr")
    close(lit[3::4], alpha, tolerance=1e-4)
    node.inputs["Color"].default_value = (0.2, 0.4, 0.6, 0)
    transparent = render_pixels(scene, tmp_path / "transparent.exr")
    close(transparent[3::4], [0] * (size * size), tolerance=1e-4)
    node.inputs["Color"].default_value = (0.2, 0.4, 0.6, opacity)
    node.inputs["Matte Weight"].default_value = 0
    empty = render_pixels(scene, tmp_path / "disabled.exr")
    close(empty[3::4], [0] * (size * size), tolerance=1e-4)
    node.inputs["Matte Weight"].default_value = 1
    node.inputs["Light"].default_value = 0
    node.inputs["Strength"].default_value = 1
    displaced = render_pixels(scene, tmp_path / "loose.exr")
    difference = sum(abs(a - b) for a, b in zip(alpha, displaced[3::4]))
    assert difference > 1, f"Loose strength did not move the edge: {difference}"
    node.inputs["Strength"].default_value = 0
    restored = render_pixels(scene, tmp_path / "restored.exr")
    close(restored, baseline, tolerance=1e-4)
