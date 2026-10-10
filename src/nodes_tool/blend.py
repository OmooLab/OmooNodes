"""Read blend versions without loading or migrating their contents."""

import gzip
import re
import struct
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def blend_stream(path):
    with Path(path).open("rb") as stream:
        magic = stream.read(4)
        stream.seek(0)
        if magic[:2] == b"\x1f\x8b":
            with gzip.GzipFile(fileobj=stream) as compressed:
                yield compressed
        elif magic == b"\x28\xb5\x2f\xfd":
            import zstandard
            with zstandard.ZstdDecompressor().stream_reader(stream) as compressed:
                yield compressed
        else:
            yield stream


def file_version(path):
    with blend_stream(path) as stream:
        header = stream.read(17)
    modern = re.match(rb"BLENDER17-\d\dv(\d{4})", header)
    legacy = re.match(rb"BLENDER[_-][vV](\d{3})", header)
    match = modern or legacy
    if match is None:
        raise ValueError(f"Invalid blend file: {path}")
    version = int(match[1])
    return version // 100, version % 100


def check_version(path, expected):
    actual = file_version(path)
    if tuple(expected[:2]) != actual:
        raise ValueError(f"{path}: saved by Blender {actual[0]}.{actual[1]}, expected {expected[0]}.{expected[1]}")


def dependencies(path, seen=None):
    """Read library paths from the file index before loading any node data."""
    import bpy
    path = Path(path).resolve()
    seen = set() if seen is None else seen
    if path in seen:
        return
    seen.add(path)
    check_version(path, bpy.app.version)
    if bpy.app.version >= (5, 0, 0):
        with bpy.data.libraries.load(str(path)) as (source, _):
            filenames = [library.filepath for library in source.libraries]
    else:
        filenames = legacy_libraries(path)
    for filename in filenames:
        dependency = (path.parent / filename[2:] if filename.startswith("//") else Path(filename)).resolve()
        yield dependency
        yield from dependencies(dependency, seen)


def legacy_libraries(path):
    """4.5 lacks the library index API: read only LI blocks and their DNA layout."""
    libraries = []
    with blend_stream(path) as stream:
        header = stream.read(12)
        endian = "<" if header[8:9] == b"v" else ">"
        pointer = 8 if header[7:8] == b"-" else 4
        block = struct.Struct(endian + ("4siQii" if pointer == 8 else "4siIii"))
        dna = None
        while chunk := stream.read(block.size):
            code, size, _, index, _ = block.unpack(chunk)
            data = stream.read(size)
            if code == b"DNA1":
                dna = data
            elif code[:2] == b"LI":
                libraries.append((index, data))
            elif code == b"ENDB":
                break
    if not libraries:
        return []
    if dna is None:
        raise ValueError(f"Missing blend DNA: {path}")
    offset = 8  # SDNA + NAME

    def number(format):
        nonlocal offset
        value = struct.unpack_from(endian + format, dna, offset)[0]
        offset += struct.calcsize(format)
        return value

    def strings():
        nonlocal offset
        count = number("I")
        result = []
        for _ in range(count):
            end = dna.index(b"\0", offset)
            result.append(dna[offset:end].decode("ascii"))
            offset = end + 1
        offset = (offset + 3) & ~3
        return result

    names = strings()
    offset += 4  # TYPE
    types = strings()
    offset += 4  # TLEN
    lengths = [number("H") for _ in types]
    offset = ((offset + 3) & ~3) + 4  # STRC
    structures = []
    for _ in range(number("I")):
        type = number("H")
        fields = [(number("H"), number("H")) for _ in range(number("H"))]
        structures.append((type, fields))
    result = []
    for index, data in libraries:
        type, fields = structures[index]
        if types[type] != "Library":
            raise ValueError(f"Invalid library block: {path}")
        start = 0
        for field_type, field_name in fields:
            name = names[field_name]
            count = 1
            for dimension in re.findall(r"\[(\d+)\]", name):
                count *= int(dimension)
            size = (pointer if "*" in name else lengths[field_type]) * count
            if name.startswith("filepath[") or name.startswith("name["):
                result.append(data[start:start + size].split(b"\0", 1)[0].decode("utf8"))
                break
            start += size
        else:
            raise ValueError(f"Missing library filepath: {path}")
    return result
