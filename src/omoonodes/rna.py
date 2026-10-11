"""Read and restore editable RNA data; unsupported structures fail explicitly."""

SKIP = {
    "rna_type", "id_data", "name_full", "type", "inputs", "outputs", "internal_links",
    "location_absolute", "interface", "nodes", "links", "animation_data",
    "asset_data", "preview", "library", "override_library", "original", "users",
    "parent", "node", "paired_output", "active_item", "active_index", "active_input_index",
    "active_output_index", "inspection_index", "single_input", "single_output",
    "panel_states", "node_tree", "tag", "select", "show_expanded", "is_updated", "interface_items",
    "use_fake_user", "use_extra_user", "is_runtime_data",
    "frame_current", "enabled",
}


def plain(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, set):
        return {"$set": sorted(value)}
    if hasattr(value, "id_type"):
        return {"$id": [value.id_type, value.name]}
    if hasattr(value, "keys"):
        return {key: plain(value[key]) for key in value.keys()}
    return tuple(plain(item) for item in value)


def read(value, skip=(), depth=0):
    if depth > 12:
        raise ValueError(f"Unsupported nested RNA: {value.bl_rna.identifier}")
    result = {}
    for prop in value.bl_rna.properties:
        key = prop.identifier
        if key in SKIP or key in skip or key.startswith("bl_"):
            continue
        child = getattr(value, key)
        if key == "subtype" and child == "":
            child = "NONE"  # Old files can retain a removed presentation subtype.
        if prop.type == "POINTER" and child == value:
            continue
        if prop.type == "COLLECTION":
            result[key] = [read(item, depth=depth + 1) for item in child]
        elif prop.type == "POINTER":
            if child is None or hasattr(child, "id_type"):
                if not prop.is_readonly:
                    result[key] = plain(child)
            else:
                nested = read(child, depth=depth + 1)
                if nested:
                    result[key] = nested
        elif not prop.is_readonly:
            data = plain(child)
            if key == "default_value" and hasattr(value, "dimensions") and isinstance(data, tuple):
                data = data[:value.dimensions]
            result[key] = data
    if hasattr(value, "keys"):
        try:
            keys = value.keys()
        except TypeError:  # Some RNA structs expose keys() without IDProperty storage.
            keys = ()
        custom = {key: plain(value[key]) for key in keys if key != "_RNA_UI" and key not in value.bl_rna.properties}
        if custom:
            result["$custom"] = custom
    return result


def restore(value, properties, reference):
    for key in sorted(properties, key=lambda key: {"subtype": -2, "dimensions": -1}.get(key, 0)):
        data = properties[key]
        try:
            if key == "$custom":
                for name, item in data.items():
                    value[name] = item
                continue
            prop = value.bl_rna.properties.get(key)
            if prop is None:
                raise ValueError(f"Unknown property {key}")
            if isinstance(data, dict) and "$id" in data:
                setattr(value, key, reference(*data["$id"]))
            elif isinstance(data, dict) and "$set" in data:
                setattr(value, key, set(data["$set"]))
            elif prop.type == "COLLECTION":
                restore_collection(getattr(value, key), data, reference)
            elif prop.type == "POINTER" and isinstance(data, dict):
                restore(getattr(value, key), data, reference)
            else:
                setattr(value, key, data)
                if key == "dimensions" and hasattr(value, "identifier"):
                    # Interface vector dimension changes replace its RNA subtype.
                    value = next(item for item in value.id_data.interface.items_tree
                                 if getattr(item, "identifier", None) == value.identifier)
        except (AttributeError, TypeError, ValueError, RuntimeError) as error:
            raise ValueError(f"{value.bl_rna.identifier}.{key}: {error}") from error
    if hasattr(value, "update") and value.bl_rna.identifier == "CurveMapping":
        value.update()


def restore_collection(collection, items, reference):
    if hasattr(collection, "clear") and hasattr(collection, "new"):
        collection.clear()
    while len(collection) > len(items):
        collection.remove(collection[-1])
    for index, data in enumerate(items):
        if index >= len(collection):
            if not hasattr(collection, "new"):
                raise ValueError(f"Cannot create collection item {data}")
            parameters = collection.bl_rna.functions["new"].parameters
            arguments = {}
            for param in parameters:
                if param.is_output:
                    continue
                key = param.identifier
                if key in data:
                    arguments[key] = data[key]
                elif key == "socket_type" and "data_type" in data:
                    arguments[key] = {"FLOAT_VECTOR": "VECTOR", "FLOAT_COLOR": "RGBA",
                                      "BYTE_COLOR": "RGBA"}.get(data["data_type"], data["data_type"])
                elif key in {"x", "y"} and "location" in data:
                    arguments[key] = data["location"][key == "y"]
                elif key in {"position", "value"} and "location" in data:
                    arguments[key] = data["location"][key == "value"]
                elif param.is_required:
                    raise ValueError(f"Missing collection constructor argument: {key}")
            collection.new(**arguments)
        restore(collection[index], data, reference)
