#!/usr/bin/env python3
"""Create a small scene that validates Omoo geometry and shader nodes."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

import bpy

HELPERS = runpy.run_path(
    str(
        Path(__file__).resolve().parents[1]
        / ".agents"
        / "skills"
        / "use-omoo-nodes"
        / "scripts"
        / "omoo_blender.py"
    )
)
add_geometry_modifier = HELPERS["add_geometry_modifier"]
add_group_node = HELPERS["add_group_node"]
ensure_omoo_node_group = HELPERS["ensure_omoo_node_group"]
set_group_node_input = HELPERS["set_group_node_input"]
set_modifier_input = HELPERS["set_modifier_input"]


def arguments_after_separator(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("library_root", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args(argv)


def clear_scene() -> None:
    for obj in tuple(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def build_validation_scene(library_root: Path) -> dict[str, object]:
    clear_scene()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
    obj = bpy.context.active_object
    obj.name = "Omoo Validation"

    modifier = add_geometry_modifier(
        obj.name,
        "O Displace",
        (library_root,),
    )
    strength_identifier = set_modifier_input(modifier, "Strength", 0.2)

    material = bpy.data.materials.new("Omoo One Texture")
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    group_node = add_group_node(
        material.node_tree,
        "O One Texture",
        (library_root,),
        location=(-240.0, 0.0),
    )
    color_index = set_group_node_input(
        group_node,
        "Color",
        (0.08, 0.32, 0.8, 1.0),
    )
    material.node_tree.links.new(group_node.outputs["BSDF"], output.inputs["Surface"])
    obj.data.materials.append(material)

    nested_group = ensure_omoo_node_group(
        "O Draw Tubes",
        (library_root,),
    )

    dependency_errors = {
        group.name: [
            node.name
            for node in group.nodes
            if node.type == "GROUP" and node.node_tree is None
        ]
        for group in bpy.data.node_groups
    }
    dependency_errors = {
        name: missing
        for name, missing in dependency_errors.items()
        if missing
    }
    if dependency_errors:
        raise RuntimeError(f"Missing nested node groups: {dependency_errors}")

    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated.to_mesh()
    vertex_count = len(evaluated_mesh.vertices)
    evaluated.to_mesh_clear()
    return {
        "object": obj.name,
        "modifier": modifier.name,
        "modifier_group": modifier.node_group.name,
        "strength_identifier": strength_identifier,
        "shader_group": group_node.node_tree.name,
        "nested_geometry_group": nested_group.name,
        "color_input_index": color_index,
        "evaluated_vertices": vertex_count,
        "missing_dependencies": dependency_errors,
    }


def main() -> int:
    args = parse_arguments(arguments_after_separator(sys.argv))
    result = build_validation_scene(args.library_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(
        filepath=str(args.output.resolve()),
        check_existing=False,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
