# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
TreeT = typing.TypeVar('TreeT')
from collections import Counter
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Self, TypeVar, cast
import bpy
from bpy.types import CompositorNodeTree, GeometryNodeTree, Node, NodeFrame, Nodes, NodeSocket, NodeTree, ShaderNodeTree
from ..socket_types import SOCKET_COMPATIBILITY, Default, FloatInterfaceSubtypes, IntegerInterfaceSubtypes, StringInterfaceSubtypes, VectorInterfaceSubtypes, _AttributeDomains, _SocketShapeStructureType
from ._utils import SocketError, _allow_innactive_sockets, resolve_socket_key, socket_key
from .socket import BooleanSocket, BundleSocket, ClosureSocket, CollectionSocket, ColorSocket, FloatSocket, FontSocket, GeometrySocket, ImageSocket, IntegerSocket, MaterialSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, ShaderSocket, Socket, SoundSocket, StringSocket, VectorSocket
_SocketT = TypeVar('_SocketT', bound=Socket)
_FloatDefaultInputs = Literal['VALUE', 'SCENE_FRAME']
_IntegerDefaultInputs = Literal['VALUE', 'INDEX', 'ID_OR_INDEX', 'SCENE_FRAME']
_VectorDefaultInputs = Literal['VALUE', 'NORMAL', 'POSITION', 'HANDLE_LEFT', 'HANDLE_RIGHT', 'UNIFORM_IMAGE_COORDINATES']
_MatrixDefaultInputs = Literal['VALUE', 'INSTANCE_TRANSFORM']
_ObjectDefaultInputs = Literal['VALUE', 'SELF_OBJECT']

class PanelContext:

    def __init__(self, socket_context: SocketContext, name: str, *, description: str='', default_closed: bool=False):
        self._socket_context = socket_context
        self._name = name
        self._description = description
        self._default_closed = default_closed
        self._panel: bpy.types.NodeTreeInterfacePanel | None = None

    def __enter__(self) -> Self:
        interface = self._socket_context.interface
        self._panel = interface.new_panel(self._name, description=self._description, default_closed=self._default_closed)
        self._previous = self._socket_context._active_panel
        if self._previous is not None:
            assert self._panel is not None
            interface.move_to_parent(self._panel, self._previous, len(self._previous.interface_items))
        self._socket_context._active_panel = self._panel
        return self

    def __exit__(self, *args: object) -> None:
        self._socket_context._active_panel = self._previous

class TreePanelContext:

    def __init__(self, builder: TreeBuilder[Any], name: str | bpy.types.NodeTreeInterfacePanel, *, description: str='', default_closed: bool=False, reuse: bool=True):
        self._builder = builder
        self._name = name
        self._description = description
        self._default_closed = default_closed
        self._reuse = reuse
        self.panel: bpy.types.NodeTreeInterfacePanel | None = None

    def __enter__(self) -> Self:
        interface = self._builder.tree.interface
        assert interface is not None
        self._previous_inputs = self._builder.inputs._active_panel
        self._previous_outputs = self._builder.outputs._active_panel
        parent = self._previous_inputs or self._previous_outputs
        if self._previous_inputs is not None and self._previous_outputs is not None and (self._previous_inputs != self._previous_outputs):
            raise ValueError(f'Cannot nest mixed panel {self._name!r}: different panels are active for inputs ({self._previous_inputs.name!r}) and outputs ({self._previous_outputs.name!r}).')

        def parent_matches(item) -> bool:
            if parent is None:
                return item.parent is None or item.parent.index == -1
            return item.parent == parent
        if not isinstance(self._name, str):
            self.panel = self._name
        else:
            self.panel = None
            if self._reuse:
                self.panel = next((item for item in interface.items_tree if getattr(item, 'item_type', '') == 'PANEL' and item.name == self._name and parent_matches(item)), None)
            if self.panel is None:
                self.panel = interface.new_panel(self._name, description=self._description, default_closed=self._default_closed)
                if parent is not None:
                    interface.move_to_parent(self.panel, parent, len(parent.interface_items))
        self._builder.inputs._active_panel = self.panel
        self._builder.outputs._active_panel = self.panel
        return self

    def __exit__(self, *args: object) -> None:
        self._builder.inputs._active_panel = self._previous_inputs
        self._builder.outputs._active_panel = self._previous_outputs

class SocketContext:
    _direction: Literal['INPUT', 'OUTPUT'] | None

    def __init__(self, tree_builder: TreeBuilder[Any]):
        self.builder = tree_builder
        self._active_panel: bpy.types.NodeTreeInterfacePanel | None = None

    @property
    def tree(self) -> NodeTree:
        tree = self.builder.tree
        assert tree is not None
        return tree

    @property
    def interface(self) -> bpy.types.NodeTreeInterface:
        interface = self.tree.interface
        assert interface is not None
        return interface

    def panel(self, name: str, *, description: str='', default_closed: bool=False) -> PanelContext:
        return PanelContext(self, name, description=description, default_closed=default_closed)

    def _add_socket(self, socket_type: str, name: str, description: str) -> bpy.types.NodeTreeInterfaceSocket:
        kwargs: dict[str, Any] = {'name': name, 'in_out': self._direction, 'socket_type': socket_type}
        if self._active_panel is not None:
            kwargs['parent'] = self._active_panel
        interface_socket = self.interface.new_socket(**kwargs)
        assert interface_socket is not None
        interface_socket.description = description
        return interface_socket

    def _set_props(self, interface_socket: bpy.types.NodeTreeInterfaceSocket, **kwargs: Any) -> None:
        if kwargs.get('force_non_field') is False:
            kwargs.pop('force_non_field')
        elif 'force_non_field' in kwargs:
            kwargs = {'force_non_field': kwargs.pop('force_non_field'), **kwargs}
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == 'optional_label' and (not hasattr(interface_socket, key)):
                # Blender 4.5 keeps the newer display setting for source round-trips.
                if value:
                    interface_socket[key] = value
                continue
            if interface_socket.socket_type == 'NodeSocketMenu' and key == 'default_value':
                self.builder._menu_defaults.append(_MenuDefault(interface_socket, value))
            elif key == 'default_attribute':
                interface_socket.default_attribute_name = value
            elif key == 'default_input' and isinstance(value, Default):
                interface_socket.default_input = value.value
            else:
                setattr(interface_socket, key, value)

    def _wrap(self, socket_cls: type[_SocketT], interface_socket: bpy.types.NodeTreeInterfaceSocket) -> _SocketT:
        if self._direction == 'INPUT':
            bpy_socket = self.builder._input_node().outputs[interface_socket.identifier]
        else:
            bpy_socket = self.builder._output_node().inputs[interface_socket.identifier]
        s = socket_cls(bpy_socket)
        s._tree = self.builder
        s._interface_socket = interface_socket
        s._interface_identifier = interface_socket.identifier
        return s

    def float(self, name: str='Value', default_value: float=0.0, description: str='', *, min_value: float | None=None, max_value: float | None=None, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', subtype: FloatInterfaceSubtypes='NONE', attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, force_non_field: bool=False, default_input: _FloatDefaultInputs | Default='VALUE') -> FloatSocket:
        iface = self._add_socket('NodeSocketFloat', name, description)
        self._set_props(iface, default_value=default_value, min_value=min_value, max_value=max_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, subtype=subtype, attribute_domain=attribute_domain, default_attribute=default_attribute, force_non_field=force_non_field, default_input=default_input)
        return self._wrap(FloatSocket, iface)

    def integer(self, name: str='Integer', default_value: int=0, description: str='', *, min_value: int=-2147483648, max_value: int=2147483647, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', default_input: _IntegerDefaultInputs | Default='VALUE', subtype: IntegerInterfaceSubtypes='NONE', attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, force_non_field: bool=False) -> IntegerSocket:
        iface = self._add_socket('NodeSocketInt', name, description)
        self._set_props(iface, default_value=default_value, min_value=min_value, max_value=max_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, default_input=default_input, subtype=subtype, attribute_domain=attribute_domain, default_attribute=default_attribute, force_non_field=force_non_field)
        return self._wrap(IntegerSocket, iface)

    def boolean(self, name: str='Boolean', default_value: bool=False, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', layer_selection_field: bool=False, attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, is_panel_toggle: bool=False, force_non_field: bool=False) -> BooleanSocket:
        iface = self._add_socket('NodeSocketBool', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, layer_selection_field=layer_selection_field, attribute_domain=attribute_domain, default_attribute=default_attribute, is_panel_toggle=is_panel_toggle, force_non_field=force_non_field)
        return self._wrap(BooleanSocket, iface)

    def vector(self, name: str='Vector', default_value: tuple[float, float] | tuple[float, float, float] | tuple[float, float, float, float] | None=None, description: str='', *, dimensions: Literal[2, 3, 4]=3, min_value: float | None=None, max_value: float | None=None, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', subtype: VectorInterfaceSubtypes='NONE', default_attribute: str | None=None, default_input: _VectorDefaultInputs | Default='VALUE', attribute_domain: _AttributeDomains='POINT', force_non_field: bool=False) -> VectorSocket:
        values: tuple[float, ...] = (0.0,) * dimensions if default_value is None else tuple(default_value)
        assert len(values) == dimensions, 'Default value length must match dimensions'
        iface = self._add_socket('NodeSocketVector', name, description)
        rna_default = (values + (0.0, 0.0, 0.0))[:3]
        self._set_props(iface, dimensions=dimensions, default_value=rna_default, min_value=min_value, max_value=max_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, subtype=subtype, default_input=default_input, default_attribute=default_attribute, attribute_domain=attribute_domain, force_non_field=force_non_field)
        return self._wrap(VectorSocket, iface)

    def color(self, name: str='Color', default_value: tuple[float, float, float, float]=(1.0, 1.0, 1.0, 1.0), description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, force_non_field: bool=False) -> ColorSocket:
        assert len(default_value) == 4, 'Default color must be RGBA tuple'
        iface = self._add_socket('NodeSocketColor', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, attribute_domain=attribute_domain, default_attribute=default_attribute, force_non_field=force_non_field)
        return self._wrap(ColorSocket, iface)

    def rotation(self, name: str='Rotation', default_value: tuple[float, float, float]=(0.0, 0.0, 0.0), description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, force_non_field: bool=False) -> RotationSocket:
        iface = self._add_socket('NodeSocketRotation', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, attribute_domain=attribute_domain, default_attribute=default_attribute, force_non_field=force_non_field)
        return self._wrap(RotationSocket, iface)

    def matrix(self, name: str='Matrix', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', default_input: _MatrixDefaultInputs | Default='VALUE', attribute_domain: _AttributeDomains='POINT', default_attribute: str | None=None, force_non_field: bool=False) -> MatrixSocket:
        iface = self._add_socket('NodeSocketMatrix', name, description)
        self._set_props(iface, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, default_input=default_input, attribute_domain=attribute_domain, default_attribute=default_attribute, force_non_field=force_non_field)
        return self._wrap(MatrixSocket, iface)

    def string(self, name: str='String', default_value: str='', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, subtype: StringInterfaceSubtypes='NONE', structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> StringSocket:
        iface = self._add_socket('NodeSocketString', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, subtype=subtype, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(StringSocket, iface)

    def menu(self, name: str='Menu', default_value: str | None=None, description: str='', *, expanded: bool=False, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> MenuSocket:
        iface = self._add_socket('NodeSocketMenu', name, description)
        self._set_props(iface, default_value=default_value, menu_expanded=expanded, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(MenuSocket, iface)

    def object(self, name: str='Object', default_value: bpy.types.Object | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False, default_input: _ObjectDefaultInputs | Default='VALUE') -> ObjectSocket:
        iface = self._add_socket('NodeSocketObject', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field, default_input=default_input)
        return self._wrap(ObjectSocket, iface)

    def geometry(self, name: str='Geometry', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> GeometrySocket:
        iface = self._add_socket('NodeSocketGeometry', name, description)
        self._set_props(iface, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(GeometrySocket, iface)

    def collection(self, name: str='Collection', default_value: bpy.types.Collection | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> CollectionSocket:
        iface = self._add_socket('NodeSocketCollection', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(CollectionSocket, iface)

    def image(self, name: str='Image', default_value: bpy.types.Image | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> ImageSocket:
        iface = self._add_socket('NodeSocketImage', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(ImageSocket, iface)

    def material(self, name: str='Material', default_value: bpy.types.Material | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> MaterialSocket:
        iface = self._add_socket('NodeSocketMaterial', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(MaterialSocket, iface)

    def font(self, name: str='Font', default_value: bpy.types.VectorFont | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False) -> FontSocket:
        iface = self._add_socket('NodeSocketFont', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier)
        return self._wrap(FontSocket, iface)

    def sound(self, name: str='Sound', default_value: bpy.types.Sound | None=None, description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False) -> SoundSocket:
        iface = self._add_socket('NodeSocketSound', name, description)
        self._set_props(iface, default_value=default_value, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier)
        return self._wrap(SoundSocket, iface)

    def bundle(self, name: str='Bundle', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> BundleSocket:
        iface = self._add_socket('NodeSocketBundle', name, description)
        self._set_props(iface, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(BundleSocket, iface)

    def closure(self, name: str='Closure', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> ClosureSocket:
        iface = self._add_socket('NodeSocketClosure', name, description)
        self._set_props(iface, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(ClosureSocket, iface)

    def shader(self, name: str='Shader', description: str='', *, optional_label: bool=False, hide_value: bool=False, hide_in_modifier: bool=False, structure_type: _SocketShapeStructureType='AUTO', force_non_field: bool=False) -> ShaderSocket:
        iface = self._add_socket('NodeSocketShader', name, description)
        self._set_props(iface, optional_label=optional_label, hide_value=hide_value, hide_in_modifier=hide_in_modifier, structure_type=structure_type, force_non_field=force_non_field)
        return self._wrap(ShaderSocket, iface)

    def __len__(self) -> int:
        assert self.tree.interface is not None
        return len([item for item in self.tree.interface.items_tree if isinstance(item, bpy.types.NodeTreeInterfaceSocket) and item.in_out == self._direction])

class DirectionalContext(SocketContext):
    _direction = 'INPUT'

class InputInterfaceContext(DirectionalContext):
    _direction = 'INPUT'

class OutputInterfaceContext(DirectionalContext):
    _direction = 'OUTPUT'

@dataclass
class _MenuDefault:
    item: bpy.types.NodeSocketMenu | bpy.types.NodeTreeInterfaceSocketMenu
    default: str
    identifier: str = ''
    node_name: str | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if not self.identifier:
            self.identifier = self.item.identifier
            node = getattr(self.item, 'node', None)
            self.node_name = node.name if node is not None else None

    def resolve(self, tree: NodeTree):
        if self.node_name is None:
            interface = tree.interface
            assert interface is not None
            return next((item for item in interface.items_tree if getattr(item, 'identifier', None) == self.identifier), None)
        try:
            if self.item.identifier == self.identifier:
                return self.item
        except ReferenceError:
            pass
        return self._resolve_by_breadcrumbs(tree)

    def _resolve_by_breadcrumbs(self, tree: NodeTree):
        assert self.node_name is not None
        node = tree.nodes.get(self.node_name)
        if node is None:
            return None
        return next((s for s in node.inputs if s.identifier == self.identifier), None)

class TreeBuilder:
    tree: TreeT
    _tree_contexts: ClassVar[list[TreeBuilder]] = []
    _frame_contexts: ClassVar[list[NodeFrame]] = []

    def __init__(self, tree: NodeTree | str='Geometry Nodes', *, tree_type: Literal['GeometryNodeTree', 'ShaderNodeTree', 'CompositorNodeTree']='GeometryNodeTree', collapse: bool=False, fake_user: bool=False, ignore_visibility: bool=False, clear: bool=False, is_modifier: bool | None=None, is_tool: bool | None=None):
        if isinstance(tree, str):
            existing = bpy.data.node_groups.get(tree) if clear else None
            if existing is not None and existing.bl_idname == tree_type:
                self.tree = existing
            else:
                self.tree = bpy.data.node_groups.new(tree, tree_type)
        else:
            self.tree = tree
        if clear:
            self.tree.nodes.clear()
            self.tree.interface.clear()
        if is_modifier is not None:
            self.is_modifier = is_modifier
        if is_tool is not None:
            self.is_tool = is_tool
        self._menu_defaults: list[_MenuDefault] = []
        self._exited = False
        self.inputs: InputInterfaceContext = InputInterfaceContext(self)
        self.outputs: OutputInterfaceContext = OutputInterfaceContext(self)
        self.collapse = collapse
        self.fake_user = fake_user
        self.ignore_visibility = ignore_visibility

    @classmethod
    def geometry(cls, name: GeometryNodeTree | str='Geometry Nodes', *, collapse: bool=False, fake_user: bool=False, clear: bool=False, is_modifier: bool | None=None, is_tool: bool | None=None) -> TreeBuilder[GeometryNodeTree]:
        return cast('TreeBuilder[GeometryNodeTree]', cls(name, tree_type='GeometryNodeTree', collapse=collapse, fake_user=fake_user, clear=clear, is_modifier=is_modifier, is_tool=is_tool))

    @classmethod
    def shader(cls, name: ShaderNodeTree | str='Shader Nodes', *, collapse: bool=False, fake_user: bool=False, clear: bool=False) -> TreeBuilder[ShaderNodeTree]:
        return cast('TreeBuilder[ShaderNodeTree]', cls(name, tree_type='ShaderNodeTree', collapse=collapse, fake_user=fake_user, clear=clear))

    @classmethod
    def compositor(cls, name: CompositorNodeTree | str='Compositor Nodes', *, collapse: bool=False, fake_user: bool=False, clear: bool=False) -> TreeBuilder[CompositorNodeTree]:
        return cast('TreeBuilder[CompositorNodeTree]', cls(name, tree_type='CompositorNodeTree', collapse=collapse, fake_user=fake_user, clear=clear))

    @property
    def nodes(self) -> Nodes:
        return self.tree.nodes

    @property
    def fake_user(self) -> bool:
        return self.tree.use_fake_user

    @fake_user.setter
    def fake_user(self, value: bool) -> None:
        self.tree.use_fake_user = value

    @property
    def is_modifier(self) -> bool:
        return getattr(self.tree, 'is_modifier', False)

    @is_modifier.setter
    def is_modifier(self, value: bool) -> None:
        self.tree.is_modifier = value

    @property
    def is_tool(self) -> bool:
        return getattr(self.tree, 'is_tool', False)

    @is_tool.setter
    def is_tool(self, value: bool) -> None:
        self.tree.is_tool = value

    def to_python(self, min_chain_length: int=3, strict: bool=True, max_inline_width: int | None=88, top_level: Literal['with', 'class']='with', format: bool=True, nodebpy_pkg: str='omoonodes', in_place: bool=False) -> str:
        from ..export import to_python
        return to_python(self, min_chain_length=min_chain_length, strict=strict, max_inline_width=max_inline_width, top_level=top_level, format=format, nodebpy_pkg=nodebpy_pkg, in_place=in_place)

    def activate_tree(self) -> None:
        TreeBuilder._tree_contexts.append(self)

    def deactivate_tree(self) -> None:
        TreeBuilder._tree_contexts.pop()

    def __enter__(self) -> Self:
        self.activate_tree()
        self._exited = False
        return self

    def __exit__(self, *args: object) -> None:
        try:
            if not args or args[0] is None:
                self._apply_input_defaults()
            self._exited = True
        finally:
            self.deactivate_tree()

    def _apply_input_defaults(self) -> None:
        if not self._menu_defaults:
            return
        self.tree.interface_update(bpy.context)
        for value in self._menu_defaults:
            if value.default == '':
                continue
            item = value.resolve(self.tree)
            if item is not None:
                item.default_value = value.default

    def __len__(self) -> int:
        return len(self.nodes)

    def panel(self, name: str | bpy.types.NodeTreeInterfacePanel | TreePanelContext, *, description: str='', default_closed: bool=False, reuse: bool=True) -> TreePanelContext:
        if isinstance(name, TreePanelContext):
            assert name.panel is not None
            name = name.panel
        return TreePanelContext(self, name, description=description, default_closed=default_closed, reuse=reuse)

    def _input_node(self) -> Node:
        try:
            return self.tree.nodes['Group Input']
        except KeyError:
            node = self.tree.nodes.new('NodeGroupInput')
            assert node is not None
            return node

    def _output_node(self) -> Node:
        try:
            return self.tree.nodes['Group Output']
        except KeyError:
            node = self.tree.nodes.new('NodeGroupOutput')
            assert node is not None
            return node

    def link(self, socket1: NodeSocket, socket2: NodeSocket) -> bpy.types.NodeLink:
        if not isinstance(socket1, NodeSocket):
            socket1 = socket1.socket
        if not isinstance(socket2, NodeSocket):
            socket2 = socket2.socket
        is_reroute = getattr(socket1.node, 'bl_idname', None) == 'NodeReroute' or getattr(socket2.node, 'bl_idname', None) == 'NodeReroute'
        if not is_reroute and socket1.type not in SOCKET_COMPATIBILITY.get(socket2.type, ()) and (socket1.type != 'CUSTOM') and (socket2.type != 'CUSTOM'):
            raise SocketError(f'Incompatible socket types, {socket1.type} and {socket2.type}')
        link = self.tree.links.new(socket1, socket2, handle_dynamic_sockets=True)
        assert link is not None
        from_socket, to_socket = (link.from_socket, link.to_socket)
        assert from_socket is not None and to_socket is not None
        if any((socket.is_inactive for socket in [from_socket, to_socket])) and (not self.ignore_visibility):
            for socket in [from_socket, to_socket]:
                assert socket.node is not None
                if socket.is_inactive and (not _allow_innactive_sockets(socket.node) and getattr(socket.node, 'data_type', None) != socket.type):
                    other = to_socket if socket is from_socket else from_socket
                    assert other.node is not None
                    direction = 'input' if socket.is_output is False else 'output'
                    message = f"Socket '{socket.name}' ({direction}) on node '{socket.node.name}' ({socket.node.bl_idname}) is inactive, so the link from '{other.name}' on '{other.node.name}' will be created by Blender but ignored when evaluated. Socket type: {socket.bl_idname}."
                    raise RuntimeError(message)
        return link

    def add(self, name: str) -> Node:
        from ..native import create_node
        node = create_node(self.tree, name)
        assert node is not None
        node.hide = self.collapse
        if self._frame_contexts:
            node.parent = self._frame_contexts[-1]
        return node

    @classmethod
    def __class_getitem__(cls, item):
        return cls

class MaterialBuilder(TreeBuilder):

    def __init__(self, name: str='New Material', *, collapse: bool=False, fake_user: bool=False, ignore_visibility: bool=False, clear: bool=False):
        material = bpy.data.materials.get(name) if clear else None
        if material is None:
            material = bpy.data.materials.new(name)
        assert material is not None
        self.material = material
        self.material.use_nodes = True
        self.material.use_fake_user = fake_user
        assert self.material.node_tree
        super().__init__(self.material.node_tree, collapse=collapse, fake_user=fake_user, ignore_visibility=ignore_visibility, clear=True)
