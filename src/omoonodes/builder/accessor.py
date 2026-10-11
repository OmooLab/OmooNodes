# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
from collections.abc import Iterator
from typing import TYPE_CHECKING, Literal, cast, overload
import bpy
from bpy.types import NodeSocket
from ._registry import _wrap_socket
from ._utils import SocketError, _allow_innactive_sockets, denormalize_name, normalize_name
if TYPE_CHECKING:
    from .node import BaseNode
    from .socket import Socket

class SocketAccessor:

    def __init__(self, collection: bpy.types.NodeInputs | bpy.types.NodeOutputs | list[NodeSocket], direction: Literal['input', 'output'], *, builder: BaseNode | None=None):
        self._direction = direction
        self._collection = collection
        self._builder = builder

    def _index(self, key: str | int) -> int:
        if isinstance(key, int):
            return key
        if key == 'factor' and any(s.identifier == 'Fac' for s in self._collection):
            key = 'Fac'
        if key == 'color' and self._node.bl_idname == 'CompositorNodeGamma':
            key = 'Image'
        denorm = denormalize_name(key)
        active = [i for i, socket in enumerate(self._collection) if not socket.is_unavailable]
        for indices in (active, list(range(len(self._collection)))):
            ids = [self._collection[i].identifier for i in indices]
            names = [self._collection[i].name for i in indices]
            for values in (ids, names):
                for candidate in (key, denorm):
                    if candidate in values:
                        return indices[values.index(candidate)]
                normalized = [normalize_name(value) for value in values]
                if key in normalized:
                    return indices[normalized.index(key)]
        raise RuntimeError(f'{self._direction.title()} {key!r} not found on {self._node.bl_idname}')

    @overload
    def _get(self, key: slice) -> list[Socket]:
        ...

    @overload
    def _get(self, key: str | int) -> Socket:
        ...

    def _get(self, key: str | int | slice) -> Socket | list[Socket]:
        if isinstance(key, slice):
            sockets = [_wrap_socket(self._collection[i]) for i in range(*key.indices(len(self._collection)))]
            if self._builder is not None:
                for s in sockets:
                    s._builder_node = self._builder
            return sockets
        socket = _wrap_socket(self._collection[self._index(key)])
        if self._builder is not None:
            socket._builder_node = self._builder
        return socket

    @overload
    def __getitem__(self, key: slice) -> list[Socket]:
        ...

    @overload
    def __getitem__(self, key: str | int) -> Socket:
        ...

    def __getitem__(self, key: str | int | slice) -> Socket | list[Socket]:
        return self._get(key)

    @property
    def _node(self) -> bpy.types.Node:
        if isinstance(self._collection, list):
            assert self._collection[0].node is not None
            return self._collection[0].node
        for s in self._collection:
            assert s.node is not None
            return s.node
        return cast('bpy.types.Node', self._collection.data)

    @property
    def _ignore_visibility(self) -> bool:
        from .tree import TreeBuilder
        if not TreeBuilder._tree_contexts:
            return False
        return TreeBuilder._tree_contexts[-1].ignore_visibility

    def _visible_sockets(self) -> list[NodeSocket]:
        if self._direction == 'input':
            return [s for s in self._collection if _allow_innactive_sockets(self._node) or (not s.is_inactive and s.is_icon_visible)]
        return [s for s in self._collection if s.is_icon_visible]

    @property
    def _available(self) -> list[NodeSocket]:
        if self._direction == 'input':
            return [s for s in self._collection if (self._ignore_visibility or (not s.is_inactive and s.is_icon_visible)) and (not s.links or s.is_multi_input)]
        return [s for s in self._collection if self._ignore_visibility or s.is_icon_visible]

    @property
    def _inactive_fallback(self) -> list[NodeSocket]:
        if self._direction != 'input' or not _allow_innactive_sockets(self._node):
            return []
        return [s for s in self._collection if s.is_inactive and s.is_icon_visible and (not s.links or s.is_multi_input)]

    def _best_match(self, socket_type: str) -> NodeSocket:
        from ..socket_types import SOCKET_COMPATIBILITY
        compatible = SOCKET_COMPATIBILITY.get(socket_type, ())
        possible = [s for s in self._available if s.type in compatible]
        if possible:
            possible.sort(key=lambda x: compatible.index(x.type))
            return possible[0]
        raise SocketError(f'No compatible {self._direction} socket found for type {socket_type} on {self._node.name}')

    def _values(self) -> list[Socket]:
        return [_wrap_socket(s) for s in self._visible_sockets()]

    def _items(self) -> list[tuple[str, Socket]]:
        return [(s.name, _wrap_socket(s)) for s in self._visible_sockets()]

    def _keys(self) -> list[str]:
        return [name for name, _ in self._items()]

    def __len__(self) -> int:
        return len(self._items())

    def __iter__(self) -> Iterator[Socket]:
        return iter(self._values())

    def __getattr__(self, name: str) -> Socket:
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return self._get(name)
        except RuntimeError:
            raise AttributeError(f"Socket '{name}' not found on {self._direction} accessor")
