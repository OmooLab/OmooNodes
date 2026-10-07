"""Helpers for loading and using Omoo Nodes inside Blender."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import bpy


REFERENCE_PATH = Path(__file__).resolve().parent.parent / "references" / "node-catalog.json"
OMOO_REMOTE_ASSET_LIBRARIES = (
    ("O Essentials", "https://assets.omoolab.xyz/b52/O_Essentials/"),
    ("O Extra", "https://assets.omoolab.xyz/b52/O_Extra/"),
)


def normalized_remote_url(url: str) -> str:
    """Return one canonical remote asset-library URL."""
    if not url:
        return ""
    return f"{url.rstrip('/')}/"


def configured_asset_libraries() -> tuple[dict[str, Any], ...]:
    """Describe configured local libraries and synchronized remote caches."""
    result = []
    for library in bpy.context.preferences.filepaths.asset_libraries:
        path = Path(bpy.path.abspath(library.path)).expanduser()
        remote_url = normalized_remote_url(library.remote_url)
        is_remote = bool(library.remote_url)
        synchronized = bool(library.use_remote_url) if is_remote else None
        result.append(
            {
                "name": library.name,
                "path": path.resolve() if path.is_dir() else path,
                "enabled": bool(library.enabled),
                "remote_url": remote_url if is_remote else "",
                "is_remote": is_remote,
                "synchronized": synchronized,
                "available": path.is_dir(),
            }
        )
    return tuple(result)


def ensure_remote_asset_library(
    name: str,
    url: str,
    *,
    replace: bool = False,
    save_preferences: bool = True,
) -> Any:
    """Add one Blender 5.2 remote library through the official operator."""
    if bpy.app.version < (5, 2, 0):
        raise RuntimeError("Remote Asset Libraries require Blender 5.2 or newer")

    preferences = bpy.context.preferences
    if not preferences.experimental.use_remote_asset_libraries:
        raise RuntimeError("Enable Remote Asset Libraries in Experimental preferences")
    if not preferences.system.use_online_access:
        raise RuntimeError("Enable Online Access before adding a remote asset library")

    expected_url = normalized_remote_url(url)
    libraries = preferences.filepaths.asset_libraries
    matching_url = [
        library
        for library in libraries
        if normalized_remote_url(library.remote_url) == expected_url
    ]
    synchronized = [
        library
        for library in matching_url
        if library.use_remote_url
    ]
    if synchronized:
        return synchronized[0]

    conflicts = [
        library
        for library in libraries
        if library.name == name or library in matching_url
    ]
    if conflicts and not replace:
        details = ", ".join(
            f"{library.name!r} ({library.path})"
            for library in conflicts
        )
        raise RuntimeError(
            f"Asset library {name!r} is not synchronized as a remote library: "
            f"{details}. Pass replace=True to replace its preference entry."
        )
    for library in conflicts:
        libraries.remove(library)

    try:
        operator_result = bpy.ops.preferences.asset_library_add(
            type="REMOTE",
            name=name,
            remote_url=expected_url,
        )
    except RuntimeError as error:
        raise RuntimeError(
            "Blender could not add the remote asset library. "
            "Run this in an interactive Blender session with Preferences available."
        ) from error
    if "FINISHED" not in operator_result:
        raise RuntimeError(
            f"Adding remote asset library {name!r} returned {operator_result}"
        )

    created = next(
        (
            library
            for library in libraries
            if normalized_remote_url(library.remote_url) == expected_url
            and library.use_remote_url
        ),
        None,
    )
    if created is None:
        raise RuntimeError(
            f"Blender added {name!r}, but remote synchronization is not enabled"
        )
    if save_preferences:
        bpy.ops.wm.save_userpref()
    return created


def ensure_omoo_remote_asset_libraries(
    *,
    replace: bool = False,
    save_preferences: bool = True,
) -> tuple[Any, ...]:
    """Configure the published Blender 5.2 Omoo remote libraries."""
    libraries = tuple(
        ensure_remote_asset_library(
            name,
            url,
            replace=replace,
            save_preferences=False,
        )
        for name, url in OMOO_REMOTE_ASSET_LIBRARIES
    )
    if save_preferences:
        bpy.ops.wm.save_userpref()
    return libraries


def node_sources() -> dict[str, str]:
    """Return exact asset node group names mapped to source blend filenames."""
    payload = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    return {
        asset["name"]: asset["source_file"]
        for asset in payload["assets"]
    }


def canonical_node_group_name(node_group_name: str) -> str:
    """Resolve harmless surrounding whitespace while preserving asset names."""
    sources = node_sources()
    if node_group_name in sources:
        return node_group_name
    matches = [
        name
        for name in sources
        if name.strip() == node_group_name.strip()
    ]
    if len(matches) == 1:
        return matches[0]
    available = ", ".join(sorted(name.rstrip() for name in sources))
    raise KeyError(
        f"Unknown Omoo node group {node_group_name!r}. Available: {available}"
    )


def configured_asset_roots() -> tuple[Path, ...]:
    """Return local-library roots and synchronized remote cache roots."""
    return tuple(
        library["path"]
        for library in configured_asset_libraries()
        if library["enabled"]
        and library["available"]
        and (
            not library["is_remote"]
            or library["synchronized"]
        )
    )


def resolve_library_file(
    node_group_name: str,
    library_roots: Iterable[str | Path] = (),
) -> Path:
    """Find the blend file containing an Omoo node group."""
    sources = node_sources()
    canonical_name = canonical_node_group_name(node_group_name)
    filename = sources[canonical_name]

    explicit_roots = tuple(
        Path(root).expanduser().resolve()
        for root in library_roots
    )
    roots = explicit_roots or configured_asset_roots()
    matches = [
        candidate
        for root in roots
        for candidate in root.rglob(filename)
        if candidate.is_file()
    ]
    if not matches:
        searched = ", ".join(str(root) for root in roots) or "<none>"
        raise FileNotFoundError(
            f"Cannot find {filename} for {node_group_name!r}. "
            f"Searched Asset Library roots: {searched}"
        )
    return sorted(matches)[0]


def append_node_group(
    node_group_name: str,
    blend_file: str | Path,
    *,
    link: bool = False,
) -> Any:
    """Append or link one exact node group from a blend file."""
    node_group_name = canonical_node_group_name(node_group_name)
    existing = bpy.data.node_groups.get(node_group_name)
    if existing is not None and (existing.library is None or link):
        return existing

    source = Path(blend_file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Asset blend file does not exist: {source}")

    with bpy.data.libraries.load(
        str(source),
        link=link,
        relative=False,
    ) as (data_from, data_to):
        if node_group_name not in data_from.node_groups:
            raise KeyError(
                f"{node_group_name!r} is not in {source.name}"
            )
        data_to.node_groups = [node_group_name]

    node_group = data_to.node_groups[0]
    if node_group is None:
        raise RuntimeError(
            f"Blender did not load {node_group_name!r} from {source}"
        )
    validate_node_group(node_group)
    return node_group


def ensure_omoo_node_group(
    node_group_name: str,
    library_roots: Iterable[str | Path] = (),
    *,
    link: bool = False,
) -> Any:
    """Resolve and load an Omoo node group."""
    node_group_name = canonical_node_group_name(node_group_name)
    existing = bpy.data.node_groups.get(node_group_name)
    if existing is not None:
        validate_node_group(existing)
        return existing
    source = resolve_library_file(node_group_name, library_roots)
    return append_node_group(node_group_name, source, link=link)


def validate_node_group(node_group: Any) -> None:
    """Reject missing nested node-group dependencies."""
    missing = [
        node.name
        for node in node_group.nodes
        if node.type == "GROUP" and node.node_tree is None
    ]
    if missing:
        raise RuntimeError(
            f"{node_group.name!r} has missing node groups: {', '.join(missing)}"
        )


def input_sockets(node_group: Any) -> list[Any]:
    """Return group interface input sockets in stable order."""
    return [
        item
        for item in node_group.interface.items_tree
        if item.item_type == "SOCKET" and item.in_out == "INPUT"
    ]


def resolve_input_socket(
    node_group: Any,
    name_or_identifier: str,
    *,
    occurrence: int = 0,
) -> Any:
    """Resolve an input by stable identifier or visible name."""
    sockets = input_sockets(node_group)
    for socket in sockets:
        if socket.identifier == name_or_identifier:
            return socket
    named = [
        socket
        for socket in sockets
        if socket.name == name_or_identifier
    ]
    try:
        return named[occurrence]
    except IndexError as error:
        raise KeyError(
            f"Cannot resolve input {name_or_identifier!r} occurrence "
            f"{occurrence} on {node_group.name!r}"
        ) from error


def add_geometry_modifier(
    object_name: str,
    node_group_name: str,
    library_roots: Iterable[str | Path] = (),
    *,
    modifier_name: str | None = None,
    link: bool = False,
) -> Any:
    """Add an Omoo geometry node group as a modifier."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise KeyError(f"Object does not exist: {object_name!r}")
    node_group = ensure_omoo_node_group(
        node_group_name,
        library_roots,
        link=link,
    )
    if node_group.bl_idname != "GeometryNodeTree":
        raise TypeError(
            f"{node_group_name!r} is {node_group.bl_idname}, not GeometryNodeTree"
        )

    modifier = obj.modifiers.new(
        name=modifier_name or node_group_name,
        type="NODES",
    )
    modifier.node_group = node_group
    return modifier


def set_modifier_input(
    modifier: Any,
    name_or_identifier: str,
    value: Any,
    *,
    occurrence: int = 0,
) -> str:
    """Set one exposed geometry-node modifier input and return its identifier."""
    if modifier.type != "NODES" or modifier.node_group is None:
        raise TypeError("Modifier is not an initialized Geometry Nodes modifier")
    socket = resolve_input_socket(
        modifier.node_group,
        name_or_identifier,
        occurrence=occurrence,
    )
    modifier_inputs = getattr(
        getattr(modifier, "properties", None),
        "inputs",
        None,
    )
    if (
        modifier_inputs is not None
        and hasattr(modifier_inputs, socket.identifier)
    ):
        input_property = getattr(modifier_inputs, socket.identifier)
        if not hasattr(input_property, "value"):
            raise TypeError(
                f"Modifier input {socket.identifier!r} has no writable value"
            )
        input_property.value = value
        return socket.identifier

    # Blender 5.1 and earlier expose modifier inputs as ID properties.
    modifier[socket.identifier] = value
    return socket.identifier


GROUP_NODE_TYPES = {
    "GeometryNodeTree": "GeometryNodeGroup",
    "ShaderNodeTree": "ShaderNodeGroup",
    "CompositorNodeTree": "CompositorNodeGroup",
}


def add_group_node(
    target_tree: Any,
    node_group_name: str,
    library_roots: Iterable[str | Path] = (),
    *,
    location: tuple[float, float] = (0.0, 0.0),
    link: bool = False,
) -> Any:
    """Add an Omoo group node to a compatible target node tree."""
    node_group = ensure_omoo_node_group(
        node_group_name,
        library_roots,
        link=link,
    )
    if target_tree.bl_idname != node_group.bl_idname:
        raise TypeError(
            f"Target is {target_tree.bl_idname}, but {node_group_name!r} "
            f"is {node_group.bl_idname}"
        )
    node_type = GROUP_NODE_TYPES[target_tree.bl_idname]
    node = target_tree.nodes.new(node_type)
    node.node_tree = node_group
    node.location = location
    return node


def set_group_node_input(
    node: Any,
    name_or_identifier: str,
    value: Any,
    *,
    occurrence: int = 0,
) -> int:
    """Set an unlinked group-node input and return its positional index."""
    matching = [
        (index, socket)
        for index, socket in enumerate(node.inputs)
        if socket.identifier == name_or_identifier
        or socket.name == name_or_identifier
    ]
    try:
        index, socket = matching[occurrence]
    except IndexError as error:
        raise KeyError(
            f"Cannot resolve input {name_or_identifier!r} occurrence "
            f"{occurrence} on node {node.name!r}"
        ) from error
    if socket.is_linked:
        raise RuntimeError(f"Input {socket.name!r} is linked")
    socket.default_value = value
    return index
