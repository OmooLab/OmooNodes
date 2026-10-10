"""Blender worker for native nodebpy conversion and asset verification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bpy

from tools.nodes.files import write_json
from tools.nodes.graph import tree_graph
from tools.nodes.publication import release_compositor_storage


def snapshot():
    missing = [(group.name, node.name) for group in bpy.data.node_groups
               for node in group.nodes if node.type == "GROUP" and node.node_tree is None and (node.inputs or node.outputs)]
    if missing:
        raise ValueError(f"Missing node group dependencies: {missing}")
    result = {}
    for group in bpy.data.node_groups:
        if group.library is not None or group.asset_data is None:
            continue
        graph = tree_graph(group)
        metadata = group.asset_data
        graph["asset_metadata"] = {
            name: getattr(metadata, name) for name in
            ("author", "description", "copyright", "license", "catalog_id")
        }
        graph["asset_metadata"]["tags"] = sorted(tag.name for tag in metadata.tags)
        graph["tree_properties"] = {
            name: getattr(group, name) for name in
            ("description", "color_tag", "node_tool_idname", "is_modifier", "is_tool",
             "is_mode_object", "is_mode_edit", "is_mode_sculpt", "is_type_mesh",
             "is_type_curve", "is_type_pointcloud") if hasattr(group, name)
        }
        if not getattr(group, "is_tool", False):
            graph["tree_properties"].pop("node_tool_idname", None)
        graph["interface_identifiers"] = [item.identifier for item in group.interface.items_tree if item.item_type == "SOCKET"]
        result[group.name] = graph
    return result


def save(path):
    roots = {group for group in bpy.data.node_groups if group.library is None and group.asset_data}
    roots.update(material for material in bpy.data.materials if material.library is None and material.users)
    bpy.data.libraries.write(str(path), roots, fake_user=True, compress=True)


def dump(job):
    from nodebpy.assets import dump_library
    from nodebpy.assets._library import _id_defaults
    from tools.nodes.export import normalize_vector_defaults, register_emitters

    register_emitters()
    bpy.ops.wm.open_mainfile(filepath=job["input"], load_ui=False)
    source_version = list(bpy.data.version[:2])
    local_names = [group.name for group in bpy.data.node_groups if group.library is None]
    groups = [group for group in bpy.data.node_groups if group.asset_data and group.library is None]
    names = [group.name for group in groups]
    # Preserve foreign ownership before nodebpy localizes its introspection copy.
    owners = {group.name: str(Path(bpy.path.abspath(group.library.filepath)).resolve())
              for group in bpy.data.node_groups if group.library}
    graph = snapshot()
    for group in bpy.data.node_groups:
        if group.library is not None:
            continue
        for item in group.interface.items_tree:
            if hasattr(item, "subtype") and item.subtype == "":
                item.subtype = "NONE"
        for frame in [node for node in group.nodes if node.bl_idname == "NodeFrame"]:
            group.nodes.remove(frame)
    temporary = Path(job["output"]).parent / "dump-input.blend"
    temporary.parent.mkdir(parents=True, exist_ok=True)
    for library in bpy.data.libraries:
        library.filepath = str(Path(bpy.path.abspath(library.filepath)).resolve())
    save(temporary)
    images = []
    resources = Path(job["output"]) / "resources"
    needed = set()
    visited = set()

    def resources_of(tree):
        if tree in visited:
            return
        visited.add(tree)
        references = _id_defaults(tree)
        needed.update(references.get("images", ()))
        for name in references.get("materials", ()):
            material = bpy.data.materials.get(name)
            if material and material.node_tree:
                resources_of(material.node_tree)
        for node in tree.nodes:
            if node.type == "GROUP" and node.node_tree:
                resources_of(node.node_tree)

    for group in groups:
        resources_of(group)
    for image in sorted(bpy.data.images, key=lambda item: item.name):
        if image.name not in needed or image.type in {"RENDER_RESULT", "COMPOSITING"}:
            continue
        if image.packed_file is None:
            raise ValueError(f"Image must be packed before export: {image.name}")
        resources.mkdir(parents=True, exist_ok=True)
        filename = f"{len(images)}{Path(image.filepath).suffix or '.png'}"
        (resources / filename).write_bytes(image.packed_file.data)
        images.append({"name": image.name, "file": filename,
                       "colorspace": image.colorspace_settings.name, "alpha_mode": image.alpha_mode})
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if names:
        dump_library(temporary, job["output"], names=names, format=False)
    else:
        Path(job["output"]).mkdir(parents=True, exist_ok=True)
    normalize_vector_defaults(Path(job["output"]))
    if images:
        write_json(resources / "images.json", images)
    write_json(job["report"], {"graphs": graph, "owners": owners, "source_version": source_version, "groups": local_names})


def build(job):
    from nodebpy.assets import build_library
    from tools.nodes.arrangement.arrange import arrange_nodes

    sys.path.insert(0, job["package_root"])
    resources = Path(job["input"]) / "resources"
    if (resources / "images.json").exists():
        for data in json.loads((resources / "images.json").read_text(encoding="utf8")):
            image = bpy.data.images.load(str(resources / data["file"]))
            image.name = data["name"]
            image.colorspace_settings.name = data["colorspace"]
            image.alpha_mode = data["alpha_mode"]
            image.pack()
    for name, owner in job.get("links", {}).items():
        if bpy.data.node_groups.get(name) is not None:
            continue
        with bpy.data.libraries.load(owner, link=True) as (_, target):
            target.node_groups = [name]
        if target.node_groups[0] is None:
            raise ValueError(f"Missing dependency {owner}: {name}")
    build_library(job["input"], job["output"], allow_existing=bool(job.get("links")))
    before = snapshot()
    for group in list(bpy.data.node_groups):
        if group.library is not None:
            continue
        arrange_nodes(group)
    after = snapshot()
    if before != after:
        raise ValueError("AnyImage arrangement changed logical node data")
    # The file-relative links are assigned explicitly: library write does not remap paths.
    import os

    for library in bpy.data.libraries:
        absolute = Path(bpy.path.abspath(library.filepath)).resolve()
        library.filepath = "//" + os.path.relpath(absolute, Path(job["output"]).parent).replace("\\", "/")
    save(job["output"])
    write_json(job["report"], {"version": list(bpy.app.version[:2])})


def inspect(job):
    bpy.ops.wm.open_mainfile(filepath=job["input"], load_ui=False)
    file_version = list(bpy.data.version)
    undefined = [(group.name, node.name) for group in bpy.data.node_groups
                 for node in group.nodes if node.bl_idname == "NodeUndefined"]
    if undefined:
        raise ValueError(f"Undefined nodes: {undefined}")
    graph = snapshot()
    if job.get("save"):
        destination = Path(job["input"])
        converted = destination.with_name(destination.stem + ".target.blend")
        save(converted)
        # Close Blender's read handles before replacing the input on Windows.
        bpy.ops.wm.read_factory_settings(use_empty=True)
        converted.replace(destination)
        bpy.ops.wm.open_mainfile(filepath=str(destination), load_ui=False)
        file_version = list(bpy.data.version)
        if file_version[:2] != list(bpy.app.version[:2]):
            raise ValueError(f"Unexpected saved file version: {file_version}")
        if snapshot() != graph:
            raise ValueError(f"Node data changed after saving: {destination}")
    write_json(job["report"], {"graphs": graph, "version": list(bpy.app.version[:2]), "file_version": file_version})


def publish(job):
    from tools.nodes.publication import publish_library
    publish_library(bpy, Path(job["input"]), Path(job["output"]),
                    job.get("remote", False), job.get("self_contained", False), job.get("contact"))
    write_json(job["report"], {"version": list(bpy.app.version[:2])})


def main():
    job_path = Path(sys.argv[sys.argv.index("--") + 1])
    job = json.loads(job_path.read_text(encoding="utf8"))
    actual = ".".join(str(part) for part in bpy.app.version)
    if actual != job["expected_version"]:
        raise ValueError(f"Expected Blender {job['expected_version']}, running {actual}")
    bpy.context.preferences.filepaths.save_version = 0
    {"dump": dump, "build": build, "inspect": inspect, "publish": publish}[job["action"]](job)
    release_compositor_storage(bpy, Path(job["report"]).with_suffix(".cleanup.blend"))


if __name__ == "__main__":
    main()
