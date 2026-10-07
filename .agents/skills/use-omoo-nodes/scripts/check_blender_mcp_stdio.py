#!/usr/bin/env python3
"""Verify a Blender MCP stdio server and its Blender control path."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ModuleNotFoundError as error:
    raise SystemExit(
        "Install the MCP Python SDK, for example: uv run --with 'mcp[cli]' ..."
    ) from error


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server-command",
        default="blender-mcp",
        help="Use {python} to run the server with the current interpreter.",
    )
    parser.add_argument(
        "--server-arg",
        action="append",
        default=[],
        help="Repeat for each stdio server argument.",
    )
    parser.add_argument(
        "--server-pythonpath",
        type=Path,
        help="Optional source directory containing the blmcp package.",
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=9876, type=int)
    parser.add_argument(
        "--omoo-skill-dir",
        type=Path,
        help="Also load the skill helper and Omoo assets through MCP.",
    )
    parser.add_argument(
        "--library-root",
        type=Path,
        help="Omoo Asset Library root used with --omoo-skill-dir.",
    )
    return parser.parse_args()


async def verify(args: argparse.Namespace) -> dict[str, object]:
    environment = os.environ.copy()
    environment["BLENDER_MCP_HOST"] = args.host
    environment["BLENDER_MCP_PORT"] = str(args.port)
    if args.server_pythonpath is not None:
        environment["PYTHONPATH"] = str(args.server_pythonpath.resolve())

    server_command = (
        sys.executable
        if args.server_command == "{python}"
        else args.server_command
    )
    params = StdioServerParameters(
        command=server_command,
        args=args.server_arg,
        env=environment,
    )
    code = """
import bpy

name = "__OMOO_MCP_STDIO_VALIDATION__"
mesh = bpy.data.meshes.new(name)
obj = bpy.data.objects.new(name, mesh)
bpy.context.scene.collection.objects.link(obj)
created = bpy.data.objects.get(name) is obj
bpy.data.objects.remove(obj, do_unlink=True)
if mesh.users == 0:
    bpy.data.meshes.remove(mesh)
result = {
    "blender_version": bpy.app.version_string,
    "created": created,
    "cleaned": bpy.data.objects.get(name) is None,
}
"""
    if args.omoo_skill_dir is not None:
        if args.library_root is None:
            raise ValueError(
                "--library-root is required with --omoo-skill-dir"
            )
        helper_path = (
            args.omoo_skill_dir.resolve()
            / "scripts"
            / "omoo_blender.py"
        )
        library_root = args.library_root.resolve()
        code = f"""
import bpy
import runpy

helpers = runpy.run_path({str(helper_path)!r})
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0)
obj = bpy.context.active_object
obj.name = "__OMOO_SKILL_MCP_VALIDATION__"
modifier = helpers["add_geometry_modifier"](
    obj.name,
    "O Displace",
    ({str(library_root)!r},),
)
identifier = helpers["set_modifier_input"](
    modifier,
    "Strength",
    0.2,
)
shader_group = helpers["ensure_omoo_node_group"](
    "O One Texture",
    ({str(library_root)!r},),
)
nested_group = helpers["ensure_omoo_node_group"](
    "O Draw Tubes",
    ({str(library_root)!r},),
)
missing = {{
    group.name: [
        node.name
        for node in group.nodes
        if node.type == "GROUP" and node.node_tree is None
    ]
    for group in bpy.data.node_groups
}}
missing = {{name: nodes for name, nodes in missing.items() if nodes}}
evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
vertex_count = len(mesh.vertices)
evaluated.to_mesh_clear()
result = {{
    "blender_version": bpy.app.version_string,
    "modifier_group": modifier.node_group.name,
    "modifier_input": identifier,
    "shader_group": shader_group.name,
    "nested_group": nested_group.name,
    "evaluated_vertices": vertex_count,
    "missing_dependencies": missing,
}}
"""
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            names = sorted(tool.name for tool in tools.tools)
            call = await session.call_tool(
                "execute_blender_code",
                {"code": code},
            )
            if call.isError:
                raise RuntimeError(f"MCP call failed: {call.content!r}")
            response = json.loads(call.content[0].text)
    return {
        "server": initialized.serverInfo.name,
        "version": initialized.serverInfo.version,
        "tool_count": len(names),
        "has_execute_blender_code": "execute_blender_code" in names,
        "bridge_response": response,
    }


def main() -> int:
    args = parse_arguments()
    result = asyncio.run(verify(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    bridge = result["bridge_response"]
    if not isinstance(bridge, dict) or bridge.get("status") != "ok":
        return 1
    value = bridge.get("result")
    if not isinstance(value, dict):
        return 1
    if args.omoo_skill_dir is None:
        return 0 if value.get("created") and value.get("cleaned") else 1
    return 0 if (
        value.get("modifier_group") == "O Displace"
        and value.get("shader_group") == "O One Texture"
        and value.get("nested_group") == "O Draw Tubes"
        and not value.get("missing_dependencies")
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
