# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
import keyword
import re
import unicodedata
import warnings
from functools import cache
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
import bpy
from bpy.types import NodeSocket
if TYPE_CHECKING:
    from ..socket_types import SOCKET_TYPES

class SocketError(Exception):
    pass
_TYPE_PRECEDENCE: dict[str, int] = {'INT': 0, 'VALUE': 1, 'FLOAT': 1, 'VECTOR': 2}
GEO_NODE_NAMES = (f'GeometryNode{name}' for name in ('SetPosition', 'TransformGeometry', 'GroupInput', 'GroupOutput', 'MeshToPoints', 'PointsToVertices'))
_NON_IDENTIFIER = re.compile('[^0-9a-z]+')

@cache
def normalize_name(name: str) -> str:
    text = ''.join((c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))).lower()
    cleaned = _NON_IDENTIFIER.sub('_', text).strip('_')
    if cleaned and cleaned[0].isdigit():
        cleaned = '_' + cleaned
    if keyword.iskeyword(cleaned):
        cleaned += '_'
    return cleaned or '_'

def denormalize_name(attr_name: str) -> str:
    return attr_name.replace('_', ' ').title()

def typed_param_names(sockets) -> dict[str, str]:
    real = [s for s in sockets if not s.identifier.startswith('__extend__')]
    from collections import Counter
    counts = Counter((normalize_name(s.name) for s in real))
    reserved = {'self', '_named_links'}
    params: dict[str, str] = {}
    used: set[str] = set()
    for s in real:
        base = normalize_name(s.name)
        if counts[base] > 1:
            base = normalize_name(s.identifier)
        name, n = (base, 1)
        while name in used or name in reserved:
            n += 1
            name = f'{base}_{n}'
        used.add(name)
        params[s.identifier] = name
    return params

def socket_key(socket: NodeSocket) -> str:
    node = socket.node
    assert node is not None
    collection = node.outputs if socket.is_output else node.inputs
    repeat = 0
    for other in collection:
        if other.identifier == socket.identifier:
            break
        if other.name == socket.name:
            repeat += 1
    return f'{socket.name}#{repeat}' if repeat else socket.name

def resolve_socket_key(sockets, key: str) -> NodeSocket | None:
    name, _, repeat = key.partition('#')
    index = int(repeat) if repeat.isdigit() else 0
    seen = 0
    for socket in sockets:
        if socket.name == name:
            if seen == index:
                return socket
            seen += 1
    return next((s for s in sockets if s.identifier == key), None)

def _allow_innactive_sockets(node: bpy.types.Node) -> bool:
    return node.bl_idname in ('GeometryNodeIndexSwitch', 'GeometryNodeMenuSwitch', 'ShaderNodeMixShader', 'GeometryNodeSwitch', 'GeometryNodeGroup', 'ShaderNodeGroup', 'CompositorNodeGroup')

def _resolve_promotion(self_socket: NodeSocket, other: Any, reverse: bool) -> tuple[NodeSocket, Any, bool]:
    other_type = _output_socket_type(other)
    self_prec = _TYPE_PRECEDENCE.get(self_socket.type, 1)
    other_prec = _TYPE_PRECEDENCE.get(other_type, -1) if other_type is not None else -1
    if other_prec > self_prec:
        if isinstance(other, NodeSocket):
            other_socket = other
        else:
            other_socket = other._default_output_socket
        return (other_socket, self_socket, not reverse)
    return (self_socket, other, reverse)

@runtime_checkable
class _NodeLike(Protocol):

    @property
    def o(self) -> Any:
        ...

@runtime_checkable
class _SocketLike(Protocol):
    socket: NodeSocket

def _output_socket_type(value: Any) -> SOCKET_TYPES | None:
    if isinstance(value, NodeSocket):
        return value.type
    if isinstance(value, (_SocketLike, _NodeLike)):
        return value._default_output_socket.type
    return None

def _deprecated(old: str, new: str) -> None:
    warnings.warn(f'{old} is deprecated and will be removed in nodebpy 530; use {new}', DeprecationWarning, stacklevel=3)
