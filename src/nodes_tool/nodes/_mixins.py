# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, ClassVar, Literal
import bpy
from mathutils import Euler
from ..builder import BooleanSocketList, ColorSocketList, FloatSocketList, IntegerSocketList, ItemsMixin, MatrixSocketList, MenuSocketList, RotationSocketList, StringSocketList, VectorSocketList
from ..builder.items import _ALL_ITEM_TYPES, _DEFAULT_NAMES, Item, _deprecated, _FieldItems, _socket_for_item, _SocketItems, _SocketValueItems, _ValueItems
from ..socket_types import InputAny, InputBoolean, InputBundle, InputClosure, InputColor, InputFloat, InputGeometry, InputInteger, InputLinkable, InputMatrix, InputMenu, InputRotation, InputString, InputVector, _BakedDataTypeValues
if TYPE_CHECKING:
    from ..builder import BooleanSocket, BundleSocket, ColorSocket, FloatSocket, GeometrySocket, IntegerSocket, MatrixSocket, MenuSocket, RotationSocket, StringSocket, VectorSocket

class _BakeItems(_FieldItems):

    def string(self, value: InputString=None, name: str | None=None) -> Item[StringSocket]:
        return self._typed(value, name, 'STRING')

    def geometry(self, value: InputGeometry=None, name: str | None=None) -> Item[GeometrySocket]:
        return self._typed(value, name, 'GEOMETRY')

    def bundle(self, value: InputBundle=None, name: str | None=None) -> Item[BundleSocket]:
        return self._typed(value, name, 'BUNDLE')

class _BakeMixin(ItemsMixin):
    _items_collection = 'bake_items'
    _socket_data_types = tuple(('VALUE' if t == 'FLOAT' else t for t in _BakedDataTypeValues))
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, *args: InputLinkable | str, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None, **kwargs: InputAny):
        super().__init__()
        self.items._add_all(args)
        self.items._add_all(items)
        self.items._add_all(kwargs)
        self._establish_links()

    @property
    def items(self) -> _BakeItems:
        return _BakeItems(self)

class _CombineBundleItems(_SocketValueItems):
    _has_output = False

class _CombineBundleMixin(ItemsMixin):
    _items_collection = 'bundle_items'
    _socket_data_types = _ALL_ITEM_TYPES
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None, *, define_signature: bool=False):
        super().__init__()
        self.items._add_all(items)
        set_property(self.node, 'define_signature', define_signature)

    def _item_socket(self, item, *, output: bool=False) -> bpy.types.NodeSocket:
        return _socket_for_item(self.node, self._items, 'Item_', item, output=output)

    @property
    def items(self) -> _CombineBundleItems:
        return _CombineBundleItems(self)

class _SeparateBundleItems(_SocketItems):
    _has_input = False

class _SeparateBundleMixin(ItemsMixin):
    _items_collection = 'bundle_items'
    _socket_data_types = _ALL_ITEM_TYPES
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, bundle: InputBundle=None, items: Mapping[str, str] | None=None, *, define_signature: bool=False):
        super().__init__()
        set_property(self.node, 'define_signature', define_signature)
        self.items._add_all(items)
        self._establish_links(Bundle=bundle)

    def _item_socket(self, item, *, output: bool=False) -> bpy.types.NodeSocket:
        return _socket_for_item(self.node, self._items, 'Item_', item, output=output)

    @property
    def items(self) -> _SeparateBundleItems:
        return _SeparateBundleItems(self)

class _ClosureToListItems(_SocketItems):
    _has_input = False

class _ClosureToListMixin(ItemsMixin):
    _items_collection = 'list_items'
    _socket_data_types = _ALL_ITEM_TYPES
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, count: InputInteger=1, closure: InputClosure=None, items: Mapping[str, str] | None=None):
        super().__init__()
        self.items._add_all(items)
        self._establish_links(Count=count, Closure=closure)

    def _item_socket(self, item, *, output: bool=False) -> bpy.types.NodeSocket:
        return _socket_for_item(self.node, self._items, 'List_', item, output=output)

    @property
    def items(self) -> _ClosureToListItems:
        return _ClosureToListItems(self)

class _FormatStringItems(_ValueItems):
    _has_output = False

    def float(self, value: InputFloat=None, name: str | None=None) -> Item[FloatSocket]:
        return self._typed(value, name, 'FLOAT')

    def integer(self, value: InputInteger=None, name: str | None=None) -> Item[IntegerSocket]:
        return self._typed(value, name, 'INT')

    def string(self, value: InputString=None, name: str | None=None) -> Item[StringSocket]:
        return self._typed(value, name, 'STRING')

class _FormatStringMixin(ItemsMixin):
    _items_collection = 'format_items'
    _socket_data_types = ('VALUE', 'INT', 'STRING')
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, format: InputString='', items: Mapping[str, InputString | InputInteger | InputFloat] | Iterable[InputString | InputInteger | InputFloat] | None=None):
        super().__init__()
        self.items._add_all(items)
        self._establish_links(Format=format)

    @property
    def items(self) -> _FormatStringItems:
        return _FormatStringItems(self)

class _FieldToListItems(_ValueItems):

    def float(self, value: InputFloat=None, name: str | None=None) -> Item[FloatSocket, FloatSocketList]:
        return self._typed(value, name, 'FLOAT')

    def integer(self, value: InputInteger=None, name: str | None=None) -> Item[IntegerSocket, IntegerSocketList]:
        return self._typed(value, name, 'INT')

    def boolean(self, value: InputBoolean=None, name: str | None=None) -> Item[BooleanSocket, BooleanSocketList]:
        return self._typed(value, name, 'BOOLEAN')

    def vector(self, value: InputVector=None, name: str | None=None) -> Item[VectorSocket, VectorSocketList]:
        return self._typed(value, name, 'VECTOR')

    def color(self, value: InputColor=None, name: str | None=None) -> Item[ColorSocket, ColorSocketList]:
        return self._typed(value, name, 'RGBA')

    def rotation(self, value: InputRotation=None, name: str | None=None) -> Item[RotationSocket, RotationSocketList]:
        return self._typed(value, name, 'ROTATION')

    def matrix(self, value: InputMatrix=None, name: str | None=None) -> Item[MatrixSocket, MatrixSocketList]:
        return self._typed(value, name, 'MATRIX')

    def string(self, value: InputString=None, name: str | None=None) -> Item[StringSocket, StringSocketList]:
        return self._typed(value, name, 'STRING')

    def menu(self, value: InputMenu=None, name: str | None=None) -> Item[MenuSocket, MenuSocketList]:
        return self._typed(value, name, 'MENU')

class _FieldToListMixin(ItemsMixin):
    _items_collection = 'list_items'
    _socket_data_types = ('VALUE', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU')
    _type_map: ClassVar[dict[str, str]] = {'VALUE': 'FLOAT'}

    def __init__(self, count: InputInteger=1, items: Mapping[str, InputAny] | Iterable[InputAny] | None=None, *, fields: dict[str, InputLinkable | str] | None=None):
        super().__init__()
        if fields is not None:
            _deprecated('FieldToList(fields=)', 'FieldToList(items=)')
            items = fields
        self.items._add_all(items)
        self._establish_links(Count=count)

    @property
    def items(self) -> _FieldToListItems:
        return _FieldToListItems(self)

    def _list_item(self, type: str, value: Any, name: str | None) -> Any:
        _deprecated(f'FieldToList.{_DEFAULT_NAMES[type].lower()}(value, name)', 'items.<type>(value, name).output')
        return self.items._declare(value, name, type).output

    def float(self, input: InputFloat=0.0, name: str | None=None) -> FloatSocketList:
        return self._list_item('FLOAT', input, name)

    def integer(self, input: InputInteger=0, name: str | None=None) -> IntegerSocketList:
        return self._list_item('INT', input, name)

    def boolean(self, input: InputBoolean=False, name: str | None=None) -> BooleanSocketList:
        return self._list_item('BOOLEAN', input, name)

    def vector(self, input: InputVector=(0, 0, 0), name: str | None=None) -> VectorSocketList:
        return self._list_item('VECTOR', input, name)

    def color(self, input: InputColor=(0, 0, 0, 1), name: str | None=None) -> ColorSocketList:
        return self._list_item('RGBA', input, name)

    def rotation(self, input: InputRotation=None, name: str | None=None) -> RotationSocketList:
        return self._list_item('ROTATION', Euler((0, 0, 0)) if input is None else input, name)

    def matrix(self, input: InputMatrix=None, name: str | None=None) -> MatrixSocketList:
        return self._list_item('MATRIX', input, name)

    def string(self, input: InputString='', name: str | None=None) -> StringSocketList:
        return self._list_item('STRING', input, name)

    def menu(self, input: InputString=None, name: str | None=None) -> MenuSocketList:
        return self._list_item('MENU', input, name)

class _HandleModeMixin:

    @property
    def left(self) -> bool:
        return 'LEFT' in self.node.mode

    @left.setter
    def left(self, value: bool) -> None:
        set_property(self.node, 'mode', self.node.mode | {'LEFT'} if value else self.node.mode - {'LEFT'})

    @property
    def right(self) -> bool:
        return 'RIGHT' in self.node.mode

    @right.setter
    def right(self, value: bool) -> None:
        set_property(self.node, 'mode', self.node.mode | {'RIGHT'} if value else self.node.mode - {'RIGHT'})

    @property
    def mode(self) -> set[Literal['LEFT', 'RIGHT']]:
        return self.node.mode

    @mode.setter
    def mode(self, value: set[Literal['LEFT', 'RIGHT']]) -> None:
        set_property(self.node, 'mode', value)
