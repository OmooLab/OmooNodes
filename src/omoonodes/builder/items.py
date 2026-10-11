# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
import warnings
from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast
import bpy
from bpy.types import ID, Node, NodeSocket
from mathutils import Euler
from ..socket_types import _is_default_value
from ._registry import _wrap_socket
from ._utils import _deprecated, _SocketLike
from .node import DynamicInputsMixin, _match_compatible_data
from .socket import BaseSocket, Socket
if TYPE_CHECKING:
    from ..socket_types import InputAny, InputBoolean, InputBundle, InputClosure, InputCollection, InputColor, InputFloat, InputFont, InputGeometry, InputImage, InputInteger, InputLinkable, InputMaterial, InputMatrix, InputMenu, InputObject, InputRotation, InputSound, InputString, InputVector, _SocketShapeStructureType
    from .socket import BooleanSocket, BundleSocket, ClosureSocket, CollectionSocket, ColorSocket, FloatSocket, FontSocket, GeometrySocket, ImageSocket, IntegerSocket, MaterialSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, SoundSocket, StringSocket, VectorSocket
    from .tree import TreeBuilder
_ALL_ITEM_TYPES = ('VALUE', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'GEOMETRY', 'OBJECT', 'IMAGE', 'COLLECTION', 'MATERIAL', 'FONT', 'SOUND', 'BUNDLE', 'CLOSURE')
_DEFAULT_NAMES = {'FLOAT': 'Value', 'INT': 'Integer', 'BOOLEAN': 'Boolean', 'VECTOR': 'Vector', 'RGBA': 'Color', 'ROTATION': 'Rotation', 'MATRIX': 'Matrix', 'STRING': 'String', 'MENU': 'Menu', 'GEOMETRY': 'Geometry', 'OBJECT': 'Object', 'IMAGE': 'Image', 'COLLECTION': 'Collection', 'MATERIAL': 'Material', 'FONT': 'Font', 'SOUND': 'Sound', 'BUNDLE': 'Bundle', 'CLOSURE': 'Closure'}
_ID_TYPES = {bpy.types.Object: 'OBJECT', bpy.types.Image: 'IMAGE', bpy.types.Collection: 'COLLECTION', bpy.types.Material: 'MATERIAL', bpy.types.VectorFont: 'FONT', bpy.types.Sound: 'SOUND'}

def _socket_for_item(node: Node, items, prefix: str, item, *, output: bool=False) -> NodeSocket:
    index = next((i for i, candidate in enumerate(items) if candidate == item))
    sockets = node.outputs if output else node.inputs
    return [s for s in sockets if s.identifier.startswith(prefix)][index]

def _is_linkable(value: Any) -> bool:
    return value is not None and (not _is_default_value(value)) and (not isinstance(value, ID))

def _set_item_default(owner, socket: NodeSocket, value: Any) -> None:
    if isinstance(socket, bpy.types.NodeSocketMenu) and isinstance(value, str):
        from .tree import _MenuDefault
        owner.tree._menu_defaults.append(_MenuDefault(socket, value))
    else:
        socket.default_value = value

def _infer_value_type(value: Any) -> str | None:
    match value:
        case bool():
            return 'BOOLEAN'
        case int():
            return 'INT'
        case float():
            return 'FLOAT'
        case str():
            return 'STRING'
        case tuple() | list():
            return 'VECTOR'
        case Euler():
            return 'ROTATION'
        case ID():
            return next((t for cls, t in _ID_TYPES.items() if isinstance(value, cls)), None)
        case _:
            return None

def _resolve_source(value: InputLinkable, *, name: str | None, types: tuple[str, ...]) -> tuple[NodeSocket, str, str]:
    if isinstance(value, Item):
        value = value.output
    accessor = getattr(value, 'o', None)
    if accessor is None and (not isinstance(value, (NodeSocket, _SocketLike))):
        raise TypeError(f'{value!r} is not a socket, node or default value')
    sources = [cast('NodeSocket', value)] if accessor is None else accessor._available
    source, type = _match_compatible_data(sources, types)
    if name is None:
        default_socket = getattr(value, '_default_output_socket', None)
        name = source.name if default_socket is None else default_socket.name
    if isinstance(source, _SocketLike):
        source = source.socket
    return (source, type, name)
_InT = TypeVar('_InT', bound=BaseSocket)
_OutT = TypeVar('_OutT', bound=BaseSocket)
_RShiftT = TypeVar('_RShiftT')

class Item:

    def __init__(self, items: ItemCollection[Any], item: Any):
        self._items = items
        self._index = next((i for i, candidate in enumerate(items._bpy) if candidate == item))

    @property
    def _item(self):
        return self._items._bpy[self._index]

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.name!r}, {self.socket_type!r})'

    @property
    def name(self) -> str:
        return self._item.name

    @property
    def socket_type(self) -> str:
        item = self._item
        return getattr(item, 'socket_type', None) or item.data_type

    @property
    def input(self) -> _InT:
        if not self._items._has_input:
            raise AttributeError(f'{self!r} has no input socket')
        socket = self._items._item_socket(self._item)
        return cast('_InT', _chained(socket, self._items._has_output, lambda: self.output))

    @property
    def output(self) -> _OutT:
        if not self._items._has_output:
            raise AttributeError(f'{self!r} has no output socket')
        return cast('_OutT', _wrap_socket(self._items._item_socket(self._item, output=True)))

    @property
    def _default_output_socket(self) -> NodeSocket:
        return self.output.socket

    def _as_rshift_target(self) -> _InT:
        return self.input

    def __rshift__(self, other: _RShiftT) -> _RShiftT:
        return cast('_RShiftT', self.output >> cast(Any, other))

    @classmethod
    def __class_getitem__(cls, item):
        return cls

def _chained(socket: NodeSocket, continues: bool, follow) -> Socket:
    wrapped = _wrap_socket(socket)
    if continues:
        wrapped._chain_to = follow
    return wrapped

class MenuItem(Item):

    @property
    def is_selected(self) -> BooleanSocket:
        return self.output

    @property
    def description(self) -> str:
        return self._item.description

    @description.setter
    def description(self, value: str) -> None:
        self._item.description = value
_HandleT = TypeVar('_HandleT', bound=Item[Any, Any])

class ItemCollection:
    _handle_type: ClassVar[type[Item]] = Item
    _collection: ClassVar[str | None] = None
    _prefix: ClassVar[str | None] = None
    _value_types: ClassVar[tuple[str, ...] | None] = None
    _has_input: ClassVar[bool] = True
    _has_output: ClassVar[bool] = True

    def __init__(self, owner: Any):
        self._owner = owner

    def __repr__(self) -> str:
        return f'{type(self).__name__}({list(self)!r})'

    def __len__(self) -> int:
        return len(self._bpy)

    def __iter__(self) -> Iterator[_HandleT]:
        return (self._handle(item) for item in list(self._bpy))

    def __getitem__(self, key: int | str) -> _HandleT:
        items = list(self._bpy)
        if isinstance(key, int):
            return self._handle(items[key])
        for item in items:
            if item.name == key:
                return self._handle(item)
        raise KeyError(key)

    @property
    def _node(self) -> Node:
        return self._owner.node

    @property
    def _bpy(self):
        if self._collection is None:
            return self._owner._items
        return getattr(self._owner._items_node, self._collection)

    def _item_socket(self, item, *, output: bool=False) -> NodeSocket:
        if self._prefix is None:
            return self._owner._item_socket(item, output=output)
        return _socket_for_item(self._node, self._bpy, self._prefix, item, output=output)

    def _new_item(self, name: str, type: str):
        if self._collection is None:
            return self._owner._new_item(name, type)
        return self._bpy.new(type, name)

    def _configure(self, item, **props: Any) -> None:
        for key, value in props.items():
            setattr(item, key, value)

    def _handle(self, item) -> _HandleT:
        return cast('_HandleT', self._handle_type(self, item))

    def _entry_socket(self, handle: Item) -> NodeSocket:
        return self._item_socket(handle._item)

    def _default_name(self, type: str) -> str:
        return _DEFAULT_NAMES.get(type, type.capitalize())

    def _declare(self, value: Any, name: str | None, type: str | None, **props: Any) -> Any:
        owner = self._owner
        source = None
        if _is_linkable(value):
            types = self._value_types or owner._socket_data_types
            source, inferred, name = _resolve_source(value, name=name, types=types)
            type = type or inferred
        elif type is None:
            type = _infer_value_type(value)
            if type is None:
                raise TypeError(f'item {name!r} needs a value to infer its type from, or type=')
        type = getattr(owner, '_type_map', {}).get(type, type)
        if name is None:
            name = self._default_name(type)
        item = self._new_item(name, type)
        self._configure(item, **props)
        handle = self._handle(item)
        if source is not None:
            owner.tree.link(source, self._entry_socket(handle))
        elif value is not None:
            _set_item_default(owner, self._entry_socket(handle), value)
        return handle

    def _typed(self, value: Any, name: str | None, type: str, **props: Any) -> Any:
        value, name = _legacy_order(value, name, type)
        return self._declare(value, name, type, **props)

    def _add_all(self, items: Mapping[str, Any] | Iterable[Any] | None) -> None:
        if items is None:
            return
        if isinstance(items, Mapping):
            for name, value in items.items():
                declared = self._owner._declared_item_type(value)
                if declared is not None:
                    self._declare(None, name, declared)
                else:
                    self._declare(value, name, None)
        else:
            for value in items:
                self._declare(value, None, None)

    @classmethod
    def __class_getitem__(cls, item):
        return cls

def _legacy_order(value: Any, name: Any, type: str) -> tuple[Any, Any]:
    if isinstance(value, str) and type not in ('STRING', 'MENU') and (not isinstance(name, str)):
        warnings.warn(f'item factories now take the value first: use items.<type>(value, {value!r}) instead of items.<type>({value!r}, value)', DeprecationWarning, stacklevel=4)
        return (name, value)
    return (value, name)

class ItemsMixin(DynamicInputsMixin):
    _items_collection: str
    if TYPE_CHECKING:
        node: Node
        tree: TreeBuilder[Any]

        def _establish_links(self, **kwargs: Any) -> None:
            ...

    @property
    def _items_node(self) -> Node:
        return self.node

    @property
    def _items(self):
        return getattr(self._items_node, self._items_collection)

    def _new_item(self, name: str, type: str):
        return self._items.new(socket_type=type, name=name)

    def _item_socket(self, item, *, output: bool=False) -> NodeSocket:
        sockets = self.node.outputs if output else self.node.inputs
        matches = [s for s in sockets if s.name == item.name]
        if len(matches) == 1:
            return matches[0]
        items = list(self._items)
        idx = next((i for i, it in enumerate(items) if it == item))
        real = [s for s in sockets if not s.identifier.startswith('__extend__')]
        return real[len(real) - len(items) + idx]

    def _add_socket(self, name: str, type: str) -> NodeSocket:
        return self._item_socket(self._new_item(name, type))

    def _declared_item_type(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        if value in self._socket_data_types:
            return self._type_map.get(value, value)
        if value in {self._type_map.get(t, t) for t in self._socket_data_types}:
            return value
        return None

    @property
    def items(self) -> ItemCollection[Any]:
        return ItemCollection(self)

    def capture(self, value: InputLinkable, *, name: str | None=None) -> Socket:
        _deprecated('capture(value, name=)', 'items.new(value, name).output')
        return self.items._declare(value, name, None).output

    def add_item(self, name: str, value: Any=None, *, type: str | None=None) -> Item:
        _deprecated('add_item(name, value)', 'items.new(value, name)')
        return self.items._declare(value, name, type)

    def add_items(self, items: Mapping[str, InputLinkable | str]) -> dict[str, Item]:
        _deprecated('add_items(mapping)', 'items.new(value, name) per item')
        handles = {}
        for name, value in items.items():
            declared = self._declared_item_type(value)
            if declared is not None:
                handles[name] = self.items._declare(None, name, declared)
            else:
                handles[name] = self.items._declare(value, name, None)
        return handles

class _ValueItems(ItemCollection):

    def new(self, value: InputAny=None, name: str | None=None, *, type: str | None=None) -> _HandleT:
        return self._declare(value, name, type)

class _DeclaredItems(ItemCollection):

    def new(self, name: str | None=None, *, type: str) -> _HandleT:
        return self._declare(None, name, type)

class _FieldItems(_ValueItems):

    def float(self, value: InputFloat=None, name: str | None=None) -> Item[FloatSocket]:
        return self._typed(value, name, 'FLOAT')

    def integer(self, value: InputInteger=None, name: str | None=None) -> Item[IntegerSocket]:
        return self._typed(value, name, 'INT')

    def boolean(self, value: InputBoolean=None, name: str | None=None) -> Item[BooleanSocket]:
        return self._typed(value, name, 'BOOLEAN')

    def vector(self, value: InputVector=None, name: str | None=None) -> Item[VectorSocket]:
        return self._typed(value, name, 'VECTOR')

    def color(self, value: InputColor=None, name: str | None=None) -> Item[ColorSocket]:
        return self._typed(value, name, 'RGBA')

    def rotation(self, value: InputRotation=None, name: str | None=None) -> Item[RotationSocket]:
        return self._typed(value, name, 'ROTATION')

    def matrix(self, value: InputMatrix=None, name: str | None=None) -> Item[MatrixSocket]:
        return self._typed(value, name, 'MATRIX')

class _StructuredItems(ItemCollection):

    def _configure(self, item, **props: Any) -> None:
        if props.get('structure_type') == 'AUTO':
            del props['structure_type']
        super()._configure(item, **props)

class _SocketValueItems(_StructuredItems, _ValueItems):

    def float(self, value: InputFloat=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[FloatSocket]:
        return self._typed(value, name, 'FLOAT', structure_type=structure_type)

    def integer(self, value: InputInteger=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[IntegerSocket]:
        return self._typed(value, name, 'INT', structure_type=structure_type)

    def boolean(self, value: InputBoolean=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[BooleanSocket]:
        return self._typed(value, name, 'BOOLEAN', structure_type=structure_type)

    def vector(self, value: InputVector=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[VectorSocket]:
        return self._typed(value, name, 'VECTOR', structure_type=structure_type)

    def color(self, value: InputColor=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ColorSocket]:
        return self._typed(value, name, 'RGBA', structure_type=structure_type)

    def rotation(self, value: InputRotation=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[RotationSocket]:
        return self._typed(value, name, 'ROTATION', structure_type=structure_type)

    def matrix(self, value: InputMatrix=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MatrixSocket]:
        return self._typed(value, name, 'MATRIX', structure_type=structure_type)

    def string(self, value: InputString=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[StringSocket]:
        return self._typed(value, name, 'STRING', structure_type=structure_type)

    def menu(self, value: InputMenu=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MenuSocket]:
        return self._typed(value, name, 'MENU', structure_type=structure_type)

    def geometry(self, value: InputGeometry=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[GeometrySocket]:
        return self._typed(value, name, 'GEOMETRY', structure_type=structure_type)

    def object(self, value: InputObject=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ObjectSocket]:
        return self._typed(value, name, 'OBJECT', structure_type=structure_type)

    def image(self, value: InputImage=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ImageSocket]:
        return self._typed(value, name, 'IMAGE', structure_type=structure_type)

    def collection(self, value: InputCollection=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[CollectionSocket]:
        return self._typed(value, name, 'COLLECTION', structure_type=structure_type)

    def material(self, value: InputMaterial=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MaterialSocket]:
        return self._typed(value, name, 'MATERIAL', structure_type=structure_type)

    def font(self, value: InputFont=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[FontSocket]:
        return self._typed(value, name, 'FONT', structure_type=structure_type)

    def sound(self, value: InputSound=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[SoundSocket]:
        return self._typed(value, name, 'SOUND', structure_type=structure_type)

    def bundle(self, value: InputBundle=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[BundleSocket]:
        return self._typed(value, name, 'BUNDLE', structure_type=structure_type)

    def closure(self, value: InputClosure=None, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ClosureSocket]:
        return self._typed(value, name, 'CLOSURE', structure_type=structure_type)

class _SocketItems(_StructuredItems, _DeclaredItems):

    def _declared(self, name: str | None, type: str, structure_type: str) -> Any:
        return self._declare(None, name, type, structure_type=structure_type)

    def float(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[FloatSocket]:
        return self._declared(name, 'FLOAT', structure_type)

    def integer(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[IntegerSocket]:
        return self._declared(name, 'INT', structure_type)

    def boolean(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[BooleanSocket]:
        return self._declared(name, 'BOOLEAN', structure_type)

    def vector(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[VectorSocket]:
        return self._declared(name, 'VECTOR', structure_type)

    def color(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ColorSocket]:
        return self._declared(name, 'RGBA', structure_type)

    def rotation(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[RotationSocket]:
        return self._declared(name, 'ROTATION', structure_type)

    def matrix(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MatrixSocket]:
        return self._declared(name, 'MATRIX', structure_type)

    def string(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[StringSocket]:
        return self._declared(name, 'STRING', structure_type)

    def menu(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MenuSocket]:
        return self._declared(name, 'MENU', structure_type)

    def geometry(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[GeometrySocket]:
        return self._declared(name, 'GEOMETRY', structure_type)

    def object(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ObjectSocket]:
        return self._declared(name, 'OBJECT', structure_type)

    def image(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ImageSocket]:
        return self._declared(name, 'IMAGE', structure_type)

    def collection(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[CollectionSocket]:
        return self._declared(name, 'COLLECTION', structure_type)

    def material(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[MaterialSocket]:
        return self._declared(name, 'MATERIAL', structure_type)

    def font(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[FontSocket]:
        return self._declared(name, 'FONT', structure_type)

    def sound(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[SoundSocket]:
        return self._declared(name, 'SOUND', structure_type)

    def bundle(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[BundleSocket]:
        return self._declared(name, 'BUNDLE', structure_type)

    def closure(self, name: str | None=None, *, structure_type: _SocketShapeStructureType='AUTO') -> Item[ClosureSocket]:
        return self._declared(name, 'CLOSURE', structure_type)
