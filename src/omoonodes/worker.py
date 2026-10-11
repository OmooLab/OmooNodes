"""Run one job in its native bpy environment."""

import importlib.util
import difflib
import hashlib
import json
import sys
import warnings
from pathlib import Path

# Load this installed package in the target interpreter without project imports.
package = Path(__file__).parent
spec = importlib.util.spec_from_file_location("omoonodes", package / "__init__.py",
                                            submodule_search_locations=[str(package)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")

import bpy

from omoonodes.assets import build_library
from omoonodes.blend import check_version
from omoonodes.export import dump_library, tree_source, library_data
from omoonodes.sources import definitions
from omoonodes.files import write_json
from omoonodes.publication import publish_library, release_compositor_storage


def snapshot():
    trees, materials, images, _ = library_data()
    result = {}
    for value in [*trees, *materials]:
        code = tree_source(value if value.id_type == "NODETREE" else value.node_tree,
                           value if value.id_type == "MATERIAL" else None)
        # Import paths can change when a library is moved; node references cannot.
        result[f"{value.id_type}:{value.name}"] = '\n'.join(
            line for line in code.splitlines() if not line.startswith('from nodes.'))
    for image in images:
        if image.packed_file is None:
            raise ValueError(f"Expected packed image: {image.name}")
        result[f"IMAGE:{image.name}"] = [hashlib.sha256(image.packed_file.data).hexdigest(),
                                        image.colorspace_settings.name, image.alpha_mode]
    return result


def open_library(path):
    check_version(path, bpy.app.version)
    # Discover dependencies without reading their datablocks into this process.
    from omoonodes.blend import dependencies
    for dependency in dependencies(path):
        check_version(dependency, bpy.app.version)
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    for group in bpy.data.node_groups:
        for node in group.nodes:
            if node.bl_idname == "NodeUndefined":
                raise ValueError(f"Undefined node: {group.name}/{node.name}")


def main():
    job = json.loads(Path(sys.argv[-1]).read_text(encoding="utf8"))
    if tuple(map(int, job["expected_version"].split("."))) != bpy.app.version:
        raise ValueError(f"Wrong Blender runtime: {bpy.app.version}")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.read_factory_settings(use_empty=True)
    action = job["action"]
    if action == "build":
        for path in job.get("links", {}).values():
            check_version(path, bpy.app.version)
        build_library(job["input"], job["output"], job.get("links"), job.get("source_root"))
        before = snapshot()
        open_library(job["output"])
        if before != snapshot():
            after = snapshot()
            name = next(key for key in before if before[key] != after.get(key))
            difference = ''.join(difflib.unified_diff(before[name].splitlines(True), after.get(name, '').splitlines(True)))
            raise ValueError(f"Node data changed after saving: {name}\n{difference}")
    elif action in {"dump", "inspect"}:
        open_library(job["input"])
    elif action == "publish":
        publish_library(bpy, Path(job["input"]), Path(job["output"]),
                        job.get("remote", False), job.get("self_contained", False), job.get("contact"))
    else:
        raise ValueError(f"Unknown action: {action}")
    report = {"graphs": snapshot(), "version": list(bpy.app.version[:2])}
    if action == "dump":
        references = {}
        if job.get("source_root"):
            root = Path(job["source_root"])
            references = {name: ('nodes.' + '.'.join(path.relative_to(root).with_suffix('').parts), cls)
                          for (kind, name), (path, cls) in definitions(root).items() if kind == 'NODETREE'}
        report.update(dump_library(job["output"], references))
    write_json(job["report"], report)
    release_compositor_storage(bpy, Path(job["report"]).with_suffix(".cleanup.blend"))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}", flush=True)
        sys.exit(1)
