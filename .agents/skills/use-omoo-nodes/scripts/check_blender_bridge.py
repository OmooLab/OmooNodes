#!/usr/bin/env python3
"""Verify the official Blender MCP bridge with a reversible write test."""

from __future__ import annotations

import argparse
import json
import socket


def request(host: str, port: int, code: str) -> dict[str, object]:
    """Send one official Blender MCP bridge execute request."""
    payload = (
        json.dumps(
            {
                "type": "execute",
                "code": code,
                "strict_json": True,
            }
        )
        + "\0"
    )
    with socket.create_connection((host, port), timeout=10) as connection:
        connection.sendall(payload.encode("utf-8"))
        chunks = bytearray()
        while b"\0" not in chunks:
            chunk = connection.recv(65536)
            if not chunk:
                break
            chunks.extend(chunk)
    response, _separator, _remaining = chunks.partition(b"\0")
    if not response:
        raise ConnectionError("Blender MCP bridge returned no response")
    return json.loads(response.decode("utf-8"))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=9876, type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    code = """
import bpy

name = "__OMOO_MCP_VALIDATION__"
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
    response = request(args.host, args.port, code)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if response.get("status") != "ok":
        return 1
    result = response.get("result")
    if not isinstance(result, dict):
        return 1
    return 0 if result.get("created") and result.get("cleaned") else 1


if __name__ == "__main__":
    raise SystemExit(main())
