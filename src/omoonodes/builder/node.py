# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
T = typing.TypeVar('T')
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Protocol, Self, cast
import bpy
from bpy.types import CompositorNodeGroup, CompositorNodeTree, GeometryNodeGroup, GeometryNodeTree, Node, NodeSocket, NodeTree, ShaderNodeGroup, ShaderNodeTree
from ..socket_types import SOCKET_COMPATIBILITY, Default, InputAny
from ._utils import SocketError, _NodeLike, _SocketLike
from .accessor import SocketAccessor
from .mixins import LinkingMixin, OperatorMixin
from .tree import TreeBuilder
if TYPE_CHECKING:
    from types import EllipsisType
    from .socket import Socket

    class _DynamicTarget(Protocol):

        def _add_inputs(self, *args: Any, **kwargs: Any) -> dict[str, NodeSocket]:
            ...

        @property
        def i(self) -> SocketAccessor:
            ...

def _find_socket_from_name(collection: bpy.types.NodeInputs | bpy.types.NodeOutputs | list[NodeSocket], name: str) -> NodeSocket:
    sockets = list(collection)
    for candidates in ([s for s in sockets if not s.is_unavailable], sockets):
        ids = [s.identifier for s in candidates]
        names = [s.name for s in candidates]
        for key in [name, name.title(), name.replace('_', ' ').title()]:
            if key in ids:
                return candidates[ids.index(key)]
            if key in names:
                return candidates[names.index(key)]
    raise ValueError(f"Socket {name!r} not found: {names}")


def _value_socket_type(value: Any) -> str | None:
    if isinstance(value, _SocketLike):
        return value.socket.type
    if isinstance(value, NodeSocket):
        return value.type
    if isinstance(value, Node):
        return value.outputs[0].type if value.outputs else None
    if isinstance(value, _NodeLike):
        default = getattr(value, '_default_output_socket', None)
        return default.type if default is not None else None
    return None

class BaseNode(_NodeLike, OperatorMixin, LinkingMixin):
    _bl_idname: str
    _tree: TreeBuilder[Any]
    node: Node
    _default_input_id: str | None = None
    _default_output_id: str | None = None
    _placeholder_inputs: list[str]

    def __init__(self, node: Node | None=None):
        tree = TreeBuilder._tree_contexts[-1] if len(TreeBuilder._tree_contexts) else None
        if tree is None:
            raise RuntimeError(f"Node '{self.__class__.__name__}' must be created within a TreeBuilder context manager.\nUsage:\n  with tree:\n      node = {self.__class__.__name__}()\n")
        self._tree = tree
        self._placeholder_inputs = []
        self.node = node if node else self._tree.add(self.__class__._bl_idname)

    @property
    def tree(self) -> TreeBuilder[Any]:
        return self._tree

    @property
    def name(self) -> str:
        return str(self.node.name)

    @property
    def _default_input_socket(self) -> NodeSocket:
        if self._default_input_id is not None:
            return self.node.inputs[self.i._index(self._default_input_id)]
        return self.node.inputs[0]

    @property
    def _default_output_socket(self) -> NodeSocket:
        if self._default_output_id is not None:
            return self.node.outputs[self.o._index(self._default_output_id)]
        counter = 0
        socket = self.node.outputs[counter]
        while not socket.is_icon_visible:
            counter += 1
            socket = self.node.outputs[counter]
        return socket

    @classmethod
    def _from_node(cls, node: Node) -> Self:
        builder = cls.__new__(cls)
        builder._tree = TreeBuilder(cast(NodeTree, node.id_data))
        builder._placeholder_inputs = []
        builder.node = node
        return builder

    @classmethod
    def _find_or_create_linked(cls, socket: NodeSocket) -> Self:
        if socket.is_output:
            if socket.links:
                for link in socket.links:
                    assert link.to_node
                    if link.to_node.bl_idname == cls._bl_idname:
                        return cls._from_node(link.to_node)
            node = cls()
            node.tree.link(socket, node.i._best_match(socket.type))
            return node
        else:
            if socket.links:
                for link in socket.links:
                    assert link.from_node
                    if link.from_node.bl_idname == cls._bl_idname:
                        return cls._from_node(link.from_node)
            node = cls()
            node >> socket
            return node

    def _set_input_default_value(self, input: NodeSocket, value: Any) -> None:
        assert hasattr(input, 'default_value')
        stype = getattr(input, 'type', None)
        if stype == 'VECTOR' and isinstance(value, (int, float)):
            input.default_value = [value] * len(input.default_value)
        elif stype == 'INT' and isinstance(value, float):
            input.default_value = int(value)
        elif stype == 'MENU':
            try:
                input.default_value = value
            except TypeError:
                from .tree import _MenuDefault
                self.tree._menu_defaults.append(_MenuDefault(cast('bpy.types.NodeSocketMenu', input), value))
        else:
            input.default_value = value

    def _establish_links(self, **kwargs: InputAny):
        for name, value in kwargs.items():
            self._apply_input(name, value)

    def _apply_input(self, target: str | NodeSocket, value: InputAny):
        named = isinstance(target, str)
        if isinstance(value, Default):
            return
        if value is None or (named and 'GridPrune' in self._bl_idname and (target == 'Threshold') and (getattr(self.node, 'data_type', None) == 'BOOLEAN')):
            return
        if named:
            from ..native import input_value
            target, value, handled = input_value(self.node, target, value)
            if handled:
                return
        if isinstance(value, Node):
            node = BaseNode.__new__(BaseNode)
            node.node = value
            value = node
        if value is ...:
            if named:
                self._placeholder_inputs.append(target)
            return
        elif isinstance(value, _SocketLike):
            self._link_from(value.socket, target)
        elif isinstance(value, NodeSocket):
            self._link_from(value, target)
        elif isinstance(value, _NodeLike):
            target_type = target.type if not named else self.i._get(target).type
            self._link_from(value.o._best_match(target_type), target)
        elif getattr(value, '_as_rshift_target', None) is not None:
            self._link_from(cast(Any, value)._default_output_socket, target)
        else:
            if 'BooleanMath' in self._bl_idname and value is False:
                return
            socket = _find_socket_from_name(self.node.inputs, target) if named else target
            if isinstance(value, (list, tuple)) and getattr(socket, 'is_multi_input', False):
                for source in reversed(list(value)):
                    self._apply_input(socket, cast('InputAny', source))
                return
            self._set_input_default_value(socket, value)

    def _establish_named_links(self, pairs: list[tuple[str, InputAny]]):
        used: set[str] = set()
        for name, value in pairs:
            candidates = [s for s in self.node.inputs if s.name == name and s.identifier not in used and (not s.identifier.startswith('__extend__'))]
            if not candidates:
                raise ValueError(f'no remaining input socket named {name!r} on {self._bl_idname}')
            value_type = _value_socket_type(value)
            if value_type is None and isinstance(value, (tuple, list)):

                def fits(s) -> bool:
                    try:
                        return len(s.default_value) == len(value)
                    except (AttributeError, TypeError):
                        return False
                socket = next((s for s in candidates if fits(s)), candidates[0])
                used.add(socket.identifier)
                self._apply_input(socket, value)
                continue
            if value_type is None:
                from .items import _infer_value_type
                inferred = _infer_value_type(value)
                value_type = 'VALUE' if inferred == 'FLOAT' else inferred
            socket = next((s for s in candidates if s.type == value_type), candidates[0])
            used.add(socket.identifier)
            self._apply_input(socket, value)

    @property
    def o(self) -> SocketAccessor:
        return SocketAccessor(self.node.outputs, 'output', builder=self)

    @property
    def i(self) -> SocketAccessor:
        return SocketAccessor(self.node.inputs, 'input', builder=self)

def _match_compatible_data(sockets: Iterable[NodeSocket], types: tuple[str, ...]) -> tuple[NodeSocket, str]:
    possible = []
    for socket in sockets:
        compatible = SOCKET_COMPATIBILITY.get(socket.type, ())
        for type in types:
            if type in compatible:
                possible.append((socket, type, compatible.index(type)))
    if not possible:
        raise SocketError('No compatible socket found')
    possible.sort(key=lambda x: x[2])
    socket, type, _ = possible[0]
    return (socket, type)

class DynamicInputsMixin(ABC):
    _socket_data_types: tuple[str, ...]
    _type_map: ClassVar[dict[str, str]] = {}

    def _match_compatible_data(self, sockets: Iterable[NodeSocket], types: tuple[str, ...] | None=None) -> tuple[NodeSocket, str]:
        return _match_compatible_data(sockets, self._socket_data_types if types is None else types)

    def _find_best_socket_pair(self, source: BaseNode | Socket | NodeSocket | EllipsisType | LinkingMixin, target: BaseNode | Socket | NodeSocket | EllipsisType | LinkingMixin) -> tuple[NodeSocket, NodeSocket]:
        try:
            return super()._find_best_socket_pair(source, target)
        except SocketError:
            dyn = cast('_DynamicTarget', target)
            target_name, source_socket = next(iter(dyn._add_inputs(source).items()))
            return (source_socket, dyn.i[target_name].socket)

    @abstractmethod
    def _add_socket(self, name: str, *args: Any, **kwargs: Any) -> NodeSocket:
        ...

    def _declared_item_type(self, value: Any) -> str | None:
        return None

    def _add_unlinked_input(self, name: str, value: Any) -> bool:
        declared = self._declared_item_type(value)
        if declared is not None:
            self._add_socket(name=name, type=declared)
            return True
        return False

    def _add_inputs(self, *args, **kwargs) -> dict[str, NodeSocket]:
        new_sockets = {}
        items = {}
        for arg in args:
            items[arg._default_output_socket.name] = arg
        items.update(kwargs)
        for key, source in items.items():
            if self._add_unlinked_input(key, source):
                continue
            socket_source, type = self._match_compatible_data(source.o._available if hasattr(source, 'o') else [source])
            if type in self._type_map:
                type = self._type_map[type]
            socket = self._add_socket(name=key, type=type)
            new_sockets[socket.identifier] = socket_source
        return new_sockets

class NodeGroupBuilder(BaseNode, ABC):
    _name: str
    _tree_idname: Literal['GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree']
    _warning_propagation: Literal['ALL', 'ERRORS_AND_WARNINGS', 'ERRORS', 'NONE'] = 'ALL'
    _color_tag: Literal['NONE', 'ATTRIBUTE', 'COLOR', 'CONVERTER', 'GEOMETRY', 'INPUT', 'OUTPUT', 'TEXTURE', 'VECTOR'] = 'NONE'
    _tree_properties: ClassVar[dict[str, Any]] = {}

    def __init__(self, **kwargs: Any):
        super().__init__()
        self._setup_node_group()
        self.node.show_options = False
        named_links = kwargs.pop('_named_links', None)
        self._establish_links(**kwargs)
        if named_links:
            self._establish_named_links(named_links)
        self.node.name = self.node_tree.name

    @property
    @abstractmethod
    def node_tree(self) -> T:
        ...

    @abstractmethod
    def _setup_node_group(self) -> None:
        ...

    @abstractmethod
    def _build_group(self, tree: TreeBuilder[T]) -> None:
        pass

    @classmethod
    def create_group(cls) -> T:
        return cls.__new__(cls)._create_group()

    def _group_name(self) -> str:
        return self._name

    def _create_group(self) -> T:
        name = self._group_name()
        existing = bpy.data.node_groups.get(name)
        if existing is not None:
            if existing.bl_idname != self._tree_idname:
                raise TypeError(f"Node group '{name}' already exists as {existing.bl_idname}, not {self._tree_idname}. Use a unique _name for this group.")
            return cast(T, existing)
        with TreeBuilder(name, tree_type=self._tree_idname) as tree:
            self._build_group(tree)
        tree.tree.color_tag = self._color_tag
        for key, value in self._tree_properties.items():
            setattr(tree.tree, key, value)
        return cast(T, tree.tree)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class CustomGeometryGroup(NodeGroupBuilder):
    _bl_idname = 'GeometryNodeGroup'
    _tree_idname = 'GeometryNodeTree'
    node: GeometryNodeGroup

    @property
    def node_tree(self) -> GeometryNodeTree:
        assert self.node.node_tree is not None
        return self.node.node_tree

    def _setup_node_group(self) -> None:
        self.node.node_tree = self._create_group()
        self.node.warning_propagation = self._warning_propagation

class CustomShaderGroup(NodeGroupBuilder):
    _bl_idname = 'ShaderNodeGroup'
    _tree_idname = 'ShaderNodeTree'
    node: ShaderNodeGroup

    @property
    def node_tree(self) -> ShaderNodeTree:
        assert self.node.node_tree is not None
        return self.node.node_tree

    def _setup_node_group(self) -> None:
        self.node.node_tree = self._create_group()

class CustomCompositorGroup(NodeGroupBuilder):
    _bl_idname = 'CompositorNodeGroup'
    _tree_idname = 'CompositorNodeTree'
    node: CompositorNodeGroup

    @property
    def node_tree(self) -> CompositorNodeTree:
        assert self.node.node_tree is not None
        return self.node.node_tree

    def _setup_node_group(self) -> None:
        self.node.node_tree = self._create_group()
