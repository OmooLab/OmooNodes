"""Strict nodebpy emitters for configurations used by the existing assets."""

import ast


def normalize_vector_defaults(root):
    """Correct nodebpy's 2D default export of Blender's fixed 3-float RNA array."""
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf8"))
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "vector" or len(node.args) < 2:
                continue
            dimensions = next((item.value for item in node.keywords if item.arg == "dimensions"), None)
            if not isinstance(dimensions, ast.Constant) or dimensions.value != 2:
                continue
            values = node.args[1]
            if isinstance(values, ast.Tuple) and len(values.elts) == 3:
                if ast.literal_eval(values.elts[2]) != 0:
                    raise ValueError(f"Nonzero unused 2D component: {path}")
                values.elts = values.elts[:2]
                changed = True
        if changed:
            path.write_text(ast.unparse(tree) + "\n", encoding="utf8")


def register_emitters():
    import nodebpy.export.codegen as codegen
    from nodebpy.export.codegen import BinOp, Call, GroupCall, Lit, Ref, _EMITTERS, _stmt_lines, register_emitter

    # The default formatter snaps by one float32 ULP, which hides small edits.
    codegen._fmt_float = lambda value: repr(float(value))
    tree_properties = codegen._tree_prop_overrides

    def semantic_tree_properties(tree):
        result = tree_properties(tree)
        # 4.5 allocates an unused tool id for ordinary groups; 5.2 does not.
        if not getattr(tree, "is_tool", False):
            result.pop("node_tool_idname", None)
        return result

    codegen._tree_prop_overrides = semantic_tree_properties
    original = _EMITTERS["GeometryNodeGroup"]
    compare = _EMITTERS["FunctionNodeCompare"]
    viewer = _EMITTERS["GeometryNodeViewer"]

    @register_emitter("ShaderNodeTexImage")
    def emit_image_texture(node, context):
        expression = context.constructor(node)
        if node.image is None:
            return expression
        # nodebpy records the image dependency but omits the node's image assignment.
        variable = f"image_texture_{len(context.var_map)}_{len(context.pending_lines)}"
        context.pending_lines.extend([
            "    import bpy",
            f"    {variable} = {expression.render()}",
            f"    {variable}.node.image = bpy.data.images[{node.image.name!r}]",
        ])
        return Ref(variable)

    @register_emitter("FunctionNodeAlignEulerToVector")
    def emit_align_euler(node, context):
        # This legacy node is still native Blender RNA but has no SDK wrapper.
        # Preserve it exactly instead of substituting Align Rotation to Vector.
        variable = f"legacy_align_{len(context.pending_lines)}_{len(context.var_map)}"
        context.pending_lines.extend([
            "    from nodebpy.builder import BaseNode, TreeBuilder",
            f"    {variable} = BaseNode(TreeBuilder._tree_contexts[-1].add('FunctionNodeAlignEulerToVector'))",
            f"    {variable}.node.axis = {node.axis!r}",
            f"    {variable}.node.pivot_axis = {node.pivot_axis!r}",
        ])
        for index, socket in enumerate(node.inputs):
            link = context.input_link(node, socket.identifier)
            if link:
                context.pending_lines.extend(_stmt_lines(BinOp(">>", context.upstream_expr(link, pipeline=True), Ref(f"{variable}.i[{index}]"))))
            else:
                value = tuple(socket.default_value) if socket.type == "VECTOR" else socket.default_value
                context.pending_lines.append(f"    {variable}.node.inputs[{index}].default_value = {value!r}")
        return Ref(variable)

    @register_emitter("GeometryNodeViewer")
    def emit_viewer(node, context):
        start = len(context.pending_lines)
        result = viewer(node, context)
        assignment = context.pending_lines[start]
        variable = assignment.split("=", 1)[0].strip()
        context.pending_lines[start:] = [assignment, f"    {variable}.node.viewer_items.clear()"]
        for index, item in enumerate(node.viewer_items):
            context.pending_lines.append(
                f"    {variable}.node.viewer_items.new({item.socket_type!r}, {item.name!r}).auto_remove = {item.auto_remove!r}"
            )
            link = context.input_link(node, node.inputs[index].identifier)
            if link:
                statement = BinOp(">>", context.upstream_expr(link, pipeline=True), Ref(f"{variable}.i[{index}]"))
                context.pending_lines.extend(_stmt_lines(statement))
        return result

    @register_emitter("FunctionNodeCompare")
    def emit_compare(node, context):
        result = compare(node, context)
        # Setting DOT_PRODUCT resets C to 0.9 after the constructor's initial
        # defaults were inspected. Explicitly preserve the authored threshold.
        if isinstance(result, Call) and node.data_type == "VECTOR" and node.mode == "DOT_PRODUCT":
            socket = node.inputs["C"]
            link = context.input_link(node, socket.identifier)
            result.kwargs["c"] = context.upstream_expr(link) if link else Lit(socket.default_value)
        return result

    @register_emitter("GeometryNodeGroup")
    def emit_group(node, context):
        if node.node_tree is None:
            if node.inputs or node.outputs:
                raise ValueError(f"Missing nonempty group: {node.id_data.name}/{node.name}")
            return Call("g.Group")
        result = original(node, context)
        if not isinstance(result, GroupCall):
            return result
        names = [socket.name for socket in node.inputs]
        duplicated = {name for name in names if names.count(name) > 1}
        if duplicated:
            result.named_links = []
            for socket in node.inputs:
                if socket.name not in duplicated:
                    continue
                link = context.input_link(node, socket.identifier)
                value = context.upstream_expr(link) if link else Lit(socket.default_value)
                result.named_links.append((socket.name, value))
        return result

    register_emitter("ShaderNodeGroup")(emit_group)
    register_emitter("CompositorNodeGroup")(emit_group)
