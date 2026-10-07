#!/usr/bin/env python3
"""Inspect Omoo Nodes asset node groups from Blender files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def json_value(value: Any) -> Any:
    """Convert Blender values into JSON-compatible values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "to_list"):
        return value.to_list()
    try:
        return list(value)
    except TypeError:
        return repr(value)


def optional_value(item: Any, name: str) -> Any:
    """Return a JSON-safe optional Blender RNA property."""
    if not hasattr(item, name):
        return None
    try:
        return json_value(getattr(item, name))
    except (AttributeError, TypeError, ValueError):
        return None


def interface_items(node_group: Any) -> list[dict[str, Any]]:
    """Flatten sockets while retaining their interface panel path."""
    result: list[dict[str, Any]] = []

    for item in node_group.interface.items_tree:
        if item.item_type != "SOCKET":
            continue

        panels = []
        parent = item.parent
        while parent is not None:
            panels.append(parent.name)
            parent = parent.parent
        panels.reverse()

        socket = {
            "name": item.name,
            "identifier": item.identifier,
            "in_out": item.in_out,
            "socket_type": item.socket_type,
            "panel": panels,
            "description": optional_value(item, "description"),
            "default": optional_value(item, "default_value"),
            "min": optional_value(item, "min_value"),
            "max": optional_value(item, "max_value"),
            "subtype": optional_value(item, "subtype"),
            "hide_value": optional_value(item, "hide_value"),
            "attribute_domain": optional_value(item, "attribute_domain"),
            "force_non_field": optional_value(item, "force_non_field"),
            "default_attribute": optional_value(
                item,
                "default_attribute_name",
            ),
        }
        result.append(
            {
                key: value
                for key, value in socket.items()
                if value not in (None, "", [])
            }
        )
    return result


def asset_tags(asset_data: Any) -> list[str]:
    """Return stable asset tags."""
    return sorted(tag.name for tag in asset_data.tags)


def inspect_node_group(node_group: Any, source: Path) -> dict[str, Any]:
    """Describe one asset node group."""
    dependencies: list[dict[str, Any]] = []
    node_types: Counter[str] = Counter()

    for node in node_group.nodes:
        node_types[node.bl_idname] += 1
        if node.bl_idname not in {"GeometryNodeGroup", "ShaderNodeGroup"}:
            continue
        if node.node_tree is None:
            dependencies.append({"node": node.name, "missing": True})
            continue
        dependency: dict[str, Any] = {
            "node": node.name,
            "node_group": node.node_tree.name,
        }
        if node.node_tree.library is not None:
            dependency["library"] = node.node_tree.library.filepath
        dependencies.append(dependency)

    asset_data = node_group.asset_data
    return {
        "name": node_group.name,
        "source_file": source.name,
        "tree_type": node_group.bl_idname,
        "description": asset_data.description,
        "catalog_id": asset_data.catalog_id,
        "tags": asset_tags(asset_data),
        "interface": interface_items(node_group),
        "node_count": len(node_group.nodes),
        "node_types": dict(sorted(node_types.items())),
        "dependencies": dependencies,
    }


def inspect_blend_file(bpy: Any, source: Path) -> list[dict[str, Any]]:
    """Open one Blender file and inspect local asset node groups."""
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    return [
        inspect_node_group(node_group, source)
        for node_group in sorted(bpy.data.node_groups, key=lambda item: item.name)
        if node_group.asset_data is not None and node_group.library is None
    ]


def discover_blend_files(paths: list[Path]) -> list[Path]:
    """Expand files and directories into a unique blend-file list."""
    result: set[Path] = set()
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved.is_file() and resolved.suffix == ".blend":
            result.add(resolved)
            continue
        if resolved.is_dir():
            result.update(resolved.rglob("*.blend"))
            continue
        raise FileNotFoundError(f"Blend path does not exist: {resolved}")
    return sorted(result)


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect asset node groups in Omoo Nodes blend files.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Blend files or directories containing blend files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON to this path instead of stdout.",
    )
    return parser.parse_args(argv)


def arguments_after_separator(argv: list[str]) -> list[str]:
    """Support both regular Python and Blender --python invocation."""
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def main() -> int:
    try:
        import bpy
    except ModuleNotFoundError:
        print(
            "Run with Blender or a compatible bpy Python package.",
            file=sys.stderr,
        )
        return 2

    args = parse_arguments(arguments_after_separator(sys.argv))
    try:
        files = discover_blend_files(args.paths)
        assets = [
            asset
            for source in files
            for asset in inspect_blend_file(bpy, source)
        ]
    except (FileNotFoundError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    payload = {
        "blender_version": bpy.app.version_string,
        "asset_count": len(assets),
        "assets": assets,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(serialized, end="")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
