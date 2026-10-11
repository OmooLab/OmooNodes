# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
import typing
T = typing.TypeVar('T')
import ast
import heapq
import inspect
import json
import keyword
import re
import textwrap
from collections import Counter
from collections.abc import Callable, Collection, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cache
from typing import TYPE_CHECKING, Any, Literal, NamedTuple
import numpy as np
from bpy.types import ID, FunctionNodeCompare, Node, NodeSocket, NodeTree
from ..socket_types import Default
from ._floats import fmt_float as _fmt_float
if TYPE_CHECKING:
    from ..builder.tree import TreeBuilder

class CodegenError(Exception):
    pass
_ATOM_PREC = 100
_UNARY_PREC = 11
_BINOP_PREC: dict[str, int] = {'|': 5, '^': 6, '&': 7, '>>': 8, '+': 9, '-': 9, '*': 10, '/': 10, '//': 10, '%': 10, '@': 10, '**': 12}
_RIGHT_ASSOC = frozenset({'**'})

class Expr:
    prec: int = _ATOM_PREC

    def render(self) -> str:
        raise NotImplementedError

    @staticmethod
    def _child(child: Expr, parens: bool) -> str:
        text = child.render()
        return f'({text})' if parens else text

@dataclass
class Raw(Expr):
    text: str

    def render(self) -> str:
        return self.text

@dataclass
class Lit(Expr):
    value: Any

    def render(self) -> str:
        return _fmt(self.value)

    @property
    def prec(self) -> int:
        if isinstance(self.value, float):
            text = _fmt(self.value)
            if 'math.' in text and ' ' in text:
                return _BINOP_PREC['*']
        return _ATOM_PREC

@dataclass
class Ref(Expr):
    name: str

    def render(self) -> str:
        return self.name

@dataclass
class Attr(Expr):
    base: Expr
    name: str

    def render(self) -> str:
        return f'{self._child(self.base, self.base.prec < _ATOM_PREC)}.{self.name}'

@dataclass
class Subscript(Expr):
    base: Expr
    key: Expr

    def render(self) -> str:
        return f'{self._child(self.base, self.base.prec < _ATOM_PREC)}[{self.key.render()}]'

@dataclass
class Call(Expr):
    func: str
    args: list[Expr] = field(default_factory=list)
    kwargs: dict[str, Expr] = field(default_factory=dict)

    def render(self) -> str:
        parts = [a.render() for a in self.args]
        parts += [f'{k}={v.render()}' for k, v in self.kwargs.items()]
        return f"{self.func}({', '.join(parts)})"

@dataclass
class TupleExpr(Expr):
    items: list[Expr]

    def render(self) -> str:
        rendered = [item.render() for item in self.items]
        if len(rendered) == 1:
            return f'({rendered[0]},)'
        return f"({', '.join(rendered)})"

@dataclass
class DictExpr(Expr):
    items: dict[str, Expr]

    def render(self) -> str:
        inner = ', '.join((f'{_fmt(k)}: {v.render()}' for k, v in self.items.items()))
        return '{' + inner + '}'

@dataclass
class GroupCall(Expr):
    func: str
    items: dict[str, Expr]
    named_links: list[tuple[str, Expr]] = field(default_factory=list)

    def render(self) -> str:
        parts: list[str] = []
        raw: dict[str, Expr] = {}

        def flush_raw() -> None:
            if raw:
                inner = ', '.join((f'{_fmt(k)}: {v.render()}' for k, v in raw.items()))
                parts.append(f'**{{{inner}}}')
                raw.clear()
        for k, v in self.items.items():
            if k.isidentifier() and (not keyword.iskeyword(k)) and (k not in ('self', '_named_links')):
                flush_raw()
                parts.append(f'{k}={v.render()}')
            else:
                raw[k] = v
        flush_raw()
        if self.named_links:
            pairs = ', '.join((f'({_fmt(k)}, {v.render()})' for k, v in self.named_links))
            parts.append(f'_named_links=[{pairs}]')
        return f"{self.func}({', '.join(parts)})"

@dataclass
class MethodCall(Expr):
    receiver: Expr
    method: str
    args: list[Expr] = field(default_factory=list)
    kwargs: dict[str, Expr] = field(default_factory=dict)

    def render(self) -> str:
        base = self._child(self.receiver, self.receiver.prec < _ATOM_PREC)
        parts = [a.render() for a in self.args]
        parts += [f'{k}={v.render()}' for k, v in self.kwargs.items()]
        return f"{base}.{self.method}({', '.join(parts)})"

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr
    prec: int = field(default=_UNARY_PREC, init=False)

    def render(self) -> str:
        return f'{self.op}{self._child(self.operand, self.operand.prec < self.prec)}'
_COMPARE_PREC = 4

@dataclass
class CompareOp(Expr):
    op: str
    lhs: Expr
    rhs: Expr
    prec: int = field(default=_COMPARE_PREC, init=False)

    def render(self) -> str:
        lhs = self._child(self.lhs, self.lhs.prec <= self.prec)
        rhs = self._child(self.rhs, self.rhs.prec <= self.prec)
        return f'{lhs} {self.op} {rhs}'

@dataclass
class BinOp(Expr):
    op: str
    lhs: Expr
    rhs: Expr
    prec: int = field(default=_ATOM_PREC, init=False)

    def __post_init__(self) -> None:
        self.prec = _BINOP_PREC[self.op]

    def render(self) -> str:
        right_assoc = self.op in _RIGHT_ASSOC
        lhs_parens = self.lhs.prec < self.prec or (self.lhs.prec == self.prec and right_assoc)
        rhs_parens = self.rhs.prec < self.prec or (self.rhs.prec == self.prec and (not right_assoc))
        lhs = self._child(self.lhs, lhs_parens)
        rhs = self._child(self.rhs, rhs_parens)
        return f'{lhs} {self.op} {rhs}'
_MAX_LINE_WIDTH = 88

def _stmt_lines(expr: Expr, assign: str | None=None, indent: str='    ', width: int=_MAX_LINE_WIDTH) -> list[str]:
    prefix = f'{assign} = ' if assign else ''
    flat = f'{indent}{prefix}{expr.render()}'
    if len(flat) <= width or not (isinstance(expr, BinOp) and expr.op == '>>'):
        return [flat]
    segments: list[Expr] = []
    node: Expr = expr
    while isinstance(node, BinOp) and node.op == '>>':
        segments.append(node.rhs)
        node = node.lhs
    segments.append(node)
    segments.reverse()
    prec = _BINOP_PREC['>>']
    inner = indent + '    '
    head = segments[0]
    lines = [f'{indent}{prefix}(', f'{inner}{Expr._child(head, head.prec < prec)}']
    lines.extend((f'{inner}>> {Expr._child(seg, seg.prec <= prec)}' for seg in segments[1:]))
    lines.append(f'{indent})')
    return lines

def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _fmt_float(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, ID):
        collection = _ID_COLLECTIONS.get(value.id_type)
        if collection is not None:
            return f'bpy.data.{collection}.get({json.dumps(value.name, ensure_ascii=False)})'
        return repr(value)
    try:
        items = list(value)
    except TypeError:
        return repr(value)
    if len(items) == 1:
        return f'({_fmt(items[0])},)'
    return f"({', '.join((_fmt(v) for v in items))})"

def _eq(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        if isinstance(a, str) and isinstance(b, str):
            return a == b
        if hasattr(a, '__len__') and hasattr(b, '__len__'):
            if len(a) != len(b):
                return False
            return all((_eq(x, y) for x, y in zip(a, b)))
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return bool(np.float32(a) == np.float32(b))
        return a == b
    except Exception:
        return False

def _is_zero(val: Any) -> bool:
    if isinstance(val, bool):
        return not val
    if isinstance(val, (int, float)):
        return val == 0
    try:
        return all((_is_zero(v) for v in val))
    except TypeError:
        return False
_NODE_REGISTRY: dict[str, tuple[str, type]] | None = None
_ALIAS_MODULES = {'g': 'geometry', 's': 'shader', 'c': 'compositor'}
_TREE_CONSTRUCTORS = {'GeometryNodeTree': 'TreeBuilder', 'ShaderNodeTree': 'TreeBuilder.shader', 'CompositorNodeTree': 'TreeBuilder.compositor'}
_TREE_ALIAS = {'GeometryNodeTree': 'g', 'ShaderNodeTree': 's', 'CompositorNodeTree': 'c'}
_SKIP_BL_IDNAMES = frozenset({'NodeGroupInput', 'NodeGroupOutput', 'NodeReroute', 'NodeFrame'})
_INTERFACE_TYPE_METHOD: dict[str, str] = {'NodeSocketFloat': 'float', 'NodeSocketInt': 'integer', 'NodeSocketBool': 'boolean', 'NodeSocketVector': 'vector', 'NodeSocketColor': 'color', 'NodeSocketRotation': 'rotation', 'NodeSocketMatrix': 'matrix', 'NodeSocketString': 'string', 'NodeSocketMenu': 'menu', 'NodeSocketObject': 'object', 'NodeSocketGeometry': 'geometry', 'NodeSocketCollection': 'collection', 'NodeSocketImage': 'image', 'NodeSocketMaterial': 'material', 'NodeSocketFont': 'font', 'NodeSocketSound': 'sound', 'NodeSocketBundle': 'bundle', 'NodeSocketClosure': 'closure', 'NodeSocketShader': 'shader'}
_DATABLOCK_IFACE_DEFAULT_TYPES = frozenset({'NodeSocketObject', 'NodeSocketCollection', 'NodeSocketImage', 'NodeSocketMaterial', 'NodeSocketFont', 'NodeSocketSound'})
_ID_COLLECTIONS: dict[str, str] = {'MATERIAL': 'materials', 'IMAGE': 'images', 'OBJECT': 'objects', 'COLLECTION': 'collections', 'TEXTURE': 'textures', 'TEXT': 'texts', 'FONT': 'fonts', 'SOUND': 'sounds', 'SCENE': 'scenes', 'MASK': 'masks'}
_NO_DEFAULT_VALUE_TYPES = frozenset({'NodeSocketGeometry', 'NodeSocketObject', 'NodeSocketCollection', 'NodeSocketImage', 'NodeSocketMaterial', 'NodeSocketFont', 'NodeSocketSound', 'NodeSocketBundle', 'NodeSocketClosure', 'NodeSocketShader'})

def _all_subclasses(cls: type):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)

def _get_node_registry() -> dict[str, tuple[str, type]]:
    global _NODE_REGISTRY
    if _NODE_REGISTRY is not None:
        return _NODE_REGISTRY
    _NODE_REGISTRY = {}
    from ..builder.node import BaseNode
    from ..nodes import compositor, geometry, shader
    domains = [('g', geometry.__name__), ('s', shader.__name__), ('c', compositor.__name__)]
    ambiguous = {'GeometryNodeGroup', 'ShaderNodeGroup', 'CompositorNodeGroup'}
    for cls in _all_subclasses(BaseNode):
        bl_id = getattr(cls, '_bl_idname', None)
        if not bl_id or bl_id in ambiguous:
            continue
        if bl_id in _NODE_REGISTRY:
            existing = _NODE_REGISTRY[bl_id][1]
            if not (existing.__name__.startswith('_') and (not cls.__name__.startswith('_'))):
                continue
        for alias, prefix in domains:
            if cls.__module__.startswith(prefix):
                _NODE_REGISTRY[bl_id] = (alias, cls)
                break
    return _NODE_REGISTRY

def _find_cls(bl_idname: str) -> tuple[str, type] | None:
    if bl_idname == 'CompositorNodeGamma':
        bl_idname = 'ShaderNodeGamma'
    return _get_node_registry().get(bl_idname)
_signature = cache(inspect.signature)
_PROBE_TREES: dict[str, Any] = {}
_KEEP_PROBE_TREES = False

@contextmanager
def probe_trees() -> Iterator[None]:
    global _KEEP_PROBE_TREES
    if _KEEP_PROBE_TREES:
        yield
        return
    _KEEP_PROBE_TREES = True
    try:
        yield
    finally:
        _KEEP_PROBE_TREES = False
        import bpy
        for tree in _PROBE_TREES.values():
            bpy.data.node_groups.remove(tree)
        _PROBE_TREES.clear()

def _with_probe_tree(tree_idname: str, fn: Callable[[Any], T], default: T) -> T:
    try:
        import bpy
        probe_tree = _PROBE_TREES.get(tree_idname)
        if probe_tree is None:
            probe_tree = bpy.data.node_groups.new('__nodebpy_codegen_probe__', tree_idname)
            assert probe_tree is not None
            if _KEEP_PROBE_TREES:
                _PROBE_TREES[tree_idname] = probe_tree
        try:
            return fn(probe_tree)
        finally:
            if _KEEP_PROBE_TREES:
                probe_tree.nodes.clear()
                if probe_tree.interface is not None:
                    probe_tree.interface.clear()
            else:
                bpy.data.node_groups.remove(probe_tree)
    except Exception:
        return default
_BLENDER_SOCKET_DEFAULTS: dict[tuple[str, str], dict[str, object]] = {}

def _get_blender_socket_defaults(tree_idname: str, bl_idname: str) -> dict[str, object]:
    key = (tree_idname, bl_idname)
    if key in _BLENDER_SOCKET_DEFAULTS:
        return _BLENDER_SOCKET_DEFAULTS[key]

    def probe(probe_tree) -> dict[str, object]:
        defaults: dict[str, object] = {}
        node = probe_tree.nodes.new(bl_idname)
        for s in node.inputs:
            if not hasattr(s, 'default_value'):
                continue
            val = s.default_value
            try:
                defaults[s.identifier] = tuple(val)
            except TypeError:
                defaults[s.identifier] = val
        return defaults
    defaults = _with_probe_tree(tree_idname, probe, {})
    _BLENDER_SOCKET_DEFAULTS[key] = defaults
    return defaults
_NODE_OUTPUT_STRUCTURE: dict[tuple[str, str, str], str | None] = {}

def _fresh_output_structure(tree_idname: str, bl_idname: str, output_id: str) -> str | None:
    key = (tree_idname, bl_idname, output_id)
    if key in _NODE_OUTPUT_STRUCTURE:
        return _NODE_OUTPUT_STRUCTURE[key]

    def probe(probe_tree) -> str | None:
        node = probe_tree.nodes.new(bl_idname)
        for s in node.outputs:
            if s.identifier == output_id:
                return getattr(s, 'inferred_structure_type', None)
        return None
    result = _with_probe_tree(tree_idname, probe, None)
    _NODE_OUTPUT_STRUCTURE[key] = result
    return result
_IFACE_DEFAULTS: dict[tuple[str, str], dict[str, object]] = {}

def _get_interface_defaults(tree_idname: str, socket_type: str) -> dict[str, object]:
    key = (tree_idname, socket_type)
    if key in _IFACE_DEFAULTS:
        return _IFACE_DEFAULTS[key]

    def probe(probe_tree) -> dict[str, object]:
        defaults: dict[str, object] = {}
        socket = probe_tree.interface.new_socket('probe', in_out='INPUT', socket_type=socket_type)
        for prop in socket.bl_rna.properties:
            if prop.is_readonly:
                continue
            try:
                value = getattr(socket, prop.identifier)
            except Exception:
                continue
            if not isinstance(value, str):
                try:
                    value = tuple(value)
                except TypeError:
                    pass
            defaults[prop.identifier] = value
        return defaults
    defaults = _with_probe_tree(tree_idname, probe, {})
    _IFACE_DEFAULTS[key] = defaults
    return defaults

def _normalize(name: str) -> str:
    from ..builder._utils import normalize_name
    return normalize_name(name)

def _make_var(label: str, counter: dict[str, int]) -> str:
    base = re.sub('_+', '_', re.sub('\\W', '_', _normalize(label))).strip('_')
    if not base or base[0].isdigit():
        base = f'n_{base}' if base else 'node'
    if keyword.iskeyword(base) or base in ['g', 's', 'c', 'nodebpy']:
        base = f'{base}_'
    if base in ('math', 'bpy') and base not in counter:
        counter[base] = 0
    if base not in counter:
        counter[base] = 0
        return base
    counter[base] += 1
    return f'{base}_{counter[base]}'

def _node_var_label(node) -> str:
    if node.bl_idname in _GROUP_BASES and node.node_tree is not None:
        return node.node_tree.name
    return node.bl_label or 'node'

class _Link(NamedTuple):
    from_node: Any
    from_socket: Any
    to_node: Any
    to_socket: Any
    sort_id: int = 0

def _trace_reroute(node, socket, node_tree):
    visited = set()
    while node.bl_idname == 'NodeReroute' and node.name not in visited:
        visited.add(node.name)
        upstream = [link for link in node_tree.links if link.to_node.name == node.name]
        if not upstream:
            break
        node = upstream[0].from_node
        socket = upstream[0].from_socket
    return (node, socket)

def _canonical_links(node_tree, links: list[_Link]) -> list[_Link]:
    node_idx = {n.name: i for i, n in enumerate(node_tree.nodes)}

    def socket_idx(sockets, socket) -> int:
        for i, s in enumerate(sockets):
            if s.identifier == socket.identifier:
                return i
        return -1
    return sorted(links, key=lambda link: (node_idx.get(link.to_node.name, -1), socket_idx(link.to_node.inputs, link.to_socket), -link.sort_id, node_idx.get(link.from_node.name, -1), socket_idx(link.from_node.outputs, link.from_socket)))

def _effective_links(node_tree) -> list[_Link]:
    links: list[_Link] = []
    for link in node_tree.links:
        if link.to_node.bl_idname == 'NodeReroute':
            continue
        if _is_ignored_link(link):
            continue
        from_node, from_socket = _trace_reroute(link.from_node, link.from_socket, node_tree)
        if from_node.bl_idname == 'NodeReroute':
            continue
        links.append(_Link(from_node, from_socket, link.to_node, link.to_socket, getattr(link, 'multi_input_sort_id', 0)))
    return _canonical_links(node_tree, links)

def _is_ignored_link(link) -> bool:
    from ..builder._utils import _allow_innactive_sockets
    for socket, node in ((link.from_socket, link.from_node), (link.to_socket, link.to_node)):
        if node.bl_idname == 'NodeReroute':
            continue
        if getattr(socket, 'is_inactive', False) and (not _allow_innactive_sockets(node)) and (getattr(node, 'data_type', None) != socket.type):
            return True
    return False

def _ordering_edges(node_tree):
    for link in _effective_links(node_tree):
        if link.from_node != link.to_node and link.from_node.bl_idname != 'NodeGroupInput':
            yield (link.from_node, link.to_node)
    for node in node_tree.nodes:
        paired = getattr(node, 'paired_output', None)
        if paired is not None:
            yield (node, paired)

def _topo_sort(node_tree) -> list:
    nodes = list(node_tree.nodes)
    node_by_name = {n.name: n for n in nodes}
    in_deg: dict[str, int] = {n.name: 0 for n in nodes}
    adj: dict[str, list[str]] = {n.name: [] for n in nodes}
    for from_node, to_node in _ordering_edges(node_tree):
        fn, tn = (from_node.name, to_node.name)
        adj[fn].append(tn)
        in_deg[tn] += 1
    heap = [(n.bl_idname, n.name) for n in nodes if in_deg[n.name] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        _, name = heapq.heappop(heap)
        order.append(node_by_name[name])
        for m_name in adj[name]:
            in_deg[m_name] -= 1
            if in_deg[m_name] == 0:
                heapq.heappush(heap, (node_by_name[m_name].bl_idname, m_name))
    if len(order) != len(nodes):
        raise ValueError(f'Node tree {node_tree.name!r} contains a link cycle')
    return order

def _frame_chain(node) -> list:
    chain = []
    parent = node.parent
    while parent is not None and parent.bl_idname == 'NodeFrame':
        chain.append(parent)
        parent = parent.parent
    chain.reverse()
    return chain

def _frame_order(node_tree, ordered):
    chains = {n.name: _frame_chain(n) for n in ordered}
    frame_nodes_all = {f.name: f for n in ordered for f in chains[n.name]}
    if not frame_nodes_all:
        return (ordered, {n.name: () for n in ordered}, {})
    node_by_name = {n.name: n for n in ordered}
    in_order = set(node_by_name)
    edges = [(a.name, b.name) for a, b in _ordering_edges(node_tree) if a.name in in_order and b.name in in_order]
    dropped: set[str] = set()

    def full_path(name) -> tuple[str, ...]:
        return tuple((f.name for f in chains[name] if f.name not in dropped))

    def order_level(names: list[str], depth: int):
        ckey: dict[str, Any] = {}
        clusters: dict[Any, list[str]] = {}
        order_keys: list[Any] = []
        for name in names:
            path = full_path(name)
            key = path[depth] if len(path) > depth else ('__node__', name)
            ckey[name] = key
            if key not in clusters:
                clusters[key] = []
                order_keys.append(key)
            clusters[key].append(name)
        nameset = set(names)
        adj: dict[Any, set] = {k: set() for k in order_keys}
        in_deg = dict.fromkeys(order_keys, 0)
        for a, b in edges:
            if a in nameset and b in nameset:
                ka, kb = (ckey[a], ckey[b])
                if ka != kb and kb not in adj[ka]:
                    adj[ka].add(kb)
                    in_deg[kb] += 1
        pos = {k: i for i, k in enumerate(order_keys)}
        heap = [pos[k] for k in order_keys if in_deg[k] == 0]
        heapq.heapify(heap)
        result_keys: list[Any] = []
        while heap:
            k = order_keys[heapq.heappop(heap)]
            result_keys.append(k)
            for m in adj[k]:
                in_deg[m] -= 1
                if in_deg[m] == 0:
                    heapq.heappush(heap, pos[m])
        if len(result_keys) != len(order_keys):
            stuck = next((k for k in order_keys if in_deg[k] > 0 and (not isinstance(k, tuple))), None)
            return (None, stuck)
        out: list[str] = []
        for key in result_keys:
            if isinstance(key, tuple):
                out.append(clusters[key][0])
                continue
            sub, stuck = order_level(clusters[key], depth + 1)
            if sub is None:
                return (None, stuck)
            out.extend(sub)
        return (out, None)
    while True:
        result, stuck = order_level([n.name for n in ordered], 0)
        if result is not None:
            order = [node_by_name[name] for name in result]
            frame_path_of = {name: full_path(name) for name in result}
            frame_nodes = {f: node for f, node in frame_nodes_all.items() if f not in dropped}
            return (order, frame_path_of, frame_nodes)
        if stuck is None:
            return (ordered, {n.name: () for n in ordered}, {})
        dropped.add(stuck)

@dataclass
class _Val:
    expr: Expr | None
    is_socket: bool = False
    socket_id: str | None = None
    outputs: dict[str, Expr] | None = None

    def require_expr(self) -> Expr:
        if self.expr is None:
            raise CodegenError('Value was dissolved into per-output accessors and has no single expression')
        return self.expr

@dataclass
class EmitContext:
    node_tree: Any
    links: list[_Link]
    incoming: dict[str, list[_Link]]
    outgoing: dict[str, list[_Link]]
    var_map: dict[str, _Val] = field(default_factory=dict)
    counter: dict[str, int] = field(default_factory=dict)
    used_aliases: set[str] = field(default_factory=set)
    pending_lines: list[str] = field(default_factory=list)
    zones: dict[str, _ZoneState] = field(default_factory=dict)
    collector: _GroupCollector | None = None

    def input_link(self, node: Node, identifier: str) -> _Link | None:
        for link in self.incoming.get(node.name, ()):
            if link.to_socket.identifier == identifier:
                return link
        return None

    def _resolve(self, link: _Link) -> _Val:
        from_node, from_socket = (link.from_node, link.from_socket)
        if from_node.bl_idname == 'NodeGroupInput':
            val = self.var_map.get(f'_iface_inputs_{from_socket.identifier}')
            if val is None:
                raise CodegenError(f"Group input socket '{from_socket.name}' has no interface variable — was the interface emitted?")
            return val
        val = self.var_map.get(from_node.name)
        if val is None:
            raise CodegenError(f"Node '{from_node.name}' is referenced before any code was generated for it")
        return val

    def upstream_expr(self, link: _Link, *, pipeline: bool=False) -> Expr:
        return _output_expr(self._resolve(link), link.from_node, link.from_socket, to_socket=link.to_socket, pipeline=pipeline)

    def socket_expr(self, link: _Link) -> Expr:
        return _output_expr(self._resolve(link), link.from_node, link.from_socket, force_socket=True)

    def promote_to_var(self, link: _Link, expr: Expr) -> Expr:
        label = link.from_socket.name or _node_var_label(link.from_node)
        var = _make_var(label, self.counter)
        self.pending_lines.append(f'    {var} = {expr.render()}')
        ref = Ref(var)
        if link.from_node.bl_idname != 'NodeGroupInput':
            self.var_map[link.from_node.name] = _Val(ref, is_socket=True, socket_id=link.from_socket.identifier)
        return ref

    def input_expr(self, node: Node, socket: NodeSocket) -> Expr | None:
        link = self.input_link(node, socket.identifier)
        if link is not None:
            return self.upstream_expr(link)
        if hasattr(socket, 'default_value'):
            return Lit(socket.default_value)
        return None

    def constructor(self, node: Node, skip_input_id: str | None=None) -> Call:
        found = _find_cls(node.bl_idname)
        if found is None:
            raise CodegenError(f"No nodebpy class is registered for '{node.bl_idname}' (node '{node.name}')")
        alias, cls = found
        self.used_aliases.add(alias)
        by_socket: dict[str, list[tuple[int, Expr]]] = {}
        multi_inputs: set[str] = set()
        for link in self.incoming.get(node.name, ()):
            if skip_input_id and link.to_socket.identifier == skip_input_id:
                continue
            name = _normalize(link.to_socket.identifier)
            if getattr(link.to_socket, 'is_multi_input', False):
                multi_inputs.add(name)
            by_socket.setdefault(name, []).append((link.sort_id, self.upstream_expr(link)))
        socket_kwargs: dict[str, Expr] = {}
        for name, entries in by_socket.items():
            if len(entries) == 1 and name not in multi_inputs:
                socket_kwargs[name] = entries[0][1]
            else:
                entries.sort(key=lambda e: e[0], reverse=True)
                socket_kwargs[name] = TupleExpr([e[1] for e in entries])
        socket_kwargs.update(self._literal_kwargs(node, cls, socket_kwargs, skip_input_id))
        prop_values = {name: value for name, value in _non_default_props(node, cls).items() if name not in socket_kwargs}
        from ..native import export_inputs
        socket_kwargs, prop_values = export_inputs(node, socket_kwargs, prop_values, Lit)
        if node.bl_idname == 'FunctionNodeRandomValue':
            return Call(f'{alias}.RandomValue', kwargs={**socket_kwargs, 'data_type': Lit(node.data_type)})
        factory_call = _factory_call(f'{alias}.{cls.__name__}', node, cls, prop_values, socket_kwargs, skip_input_id)
        if factory_call is not None:
            return factory_call
        kwargs = dict(socket_kwargs)
        for name, value in prop_values.items():
            kwargs[name] = Lit(value)
        return Call(f'{alias}.{cls.__name__}', kwargs=kwargs)

    def _literal_kwargs(self, node, cls: type, existing: dict, skip_input_id: str | None) -> dict[str, Expr]:
        try:
            sig = _signature(cls.__init__)
        except (TypeError, ValueError):
            sig = None
        positional = [(n, p) for n, p in sig.parameters.items() if n != 'self' and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD] if sig else []
        result: dict[str, Expr] = {}
        blender_defaults: dict[str, object] | None = None
        for i, socket in enumerate(node.inputs):
            if socket.is_linked:
                continue
            if not socket.enabled:
                continue
            if skip_input_id and socket.identifier == skip_input_id:
                continue
            if not hasattr(socket, 'default_value'):
                continue
            kwarg_name = _normalize(socket.identifier)
            if kwarg_name in existing:
                continue
            try:
                val = socket.default_value
            except Exception:
                continue
            default: object = inspect.Parameter.empty
            if sig and kwarg_name in sig.parameters:
                default = sig.parameters[kwarg_name].default
            elif i < len(positional):
                default = positional[i][1].default
            if default is not inspect.Parameter.empty and default is not None:
                if _eq(val, default):
                    continue
            else:
                if blender_defaults is None:
                    blender_defaults = _get_blender_socket_defaults(self.node_tree.bl_idname, node.bl_idname)
                blender_default = blender_defaults.get(socket.identifier)
                if blender_default is not None:
                    if _eq(val, blender_default):
                        continue
                elif _is_zero(val):
                    continue
            result[kwarg_name] = Lit(val)
        return result

def _bare_resolves_elsewhere(from_node, from_socket, to_socket) -> bool:
    if to_socket is None:
        return False
    from ..socket_types import SOCKET_COMPATIBILITY
    compatible = SOCKET_COMPATIBILITY.get(to_socket.type, ())
    candidates = [s for s in from_node.outputs if s.type in compatible]
    if not candidates:
        return False
    best = min(range(len(candidates)), key=lambda i: (compatible.index(candidates[i].type), i))
    return candidates[best].identifier != from_socket.identifier

def _needs_output_accessor(from_node, from_socket) -> bool:
    if from_node.bl_idname == 'GeometryNodeMenuSwitch':
        return True
    active = [s for s in from_node.outputs if not getattr(s, 'is_inactive', False) and '__extend__' not in s.identifier]
    if len(active) <= 1:
        return False
    if from_socket.type == 'GEOMETRY':
        return sum((s.type == 'GEOMETRY' for s in active)) > 1
    return True

def _output_expr(val: _Val, from_node, from_socket, *, to_socket=None, force_socket: bool=False, pipeline: bool=False) -> Expr:
    if from_node.bl_idname == 'FunctionNodeRandomValue' and val.expr is not None:
        return Attr(val.expr, 'o.value')
    if val.outputs is not None:
        expr = val.outputs.get(from_socket.identifier)
        if expr is None:
            raise CodegenError(f"Output '{from_socket.name}' of node '{from_node.name}' has no generated expression")
        return expr
    if val.expr is None:
        raise CodegenError(f"Node '{from_node.name}' has no generated expression")
    if val.is_socket:
        if val.socket_id is not None and val.socket_id != from_socket.identifier:
            raise CodegenError(f"Expression for node '{from_node.name}' evaluates to output '{val.socket_id}' but '{from_socket.identifier}' was requested")
        return val.expr
    if not force_socket and from_node.outputs and (from_node.outputs[0].identifier == from_socket.identifier) and (pipeline or not _needs_output_accessor(from_node, from_socket)) and (not _bare_resolves_elsewhere(from_node, from_socket, to_socket)):
        return val.expr
    if sum((s.name == from_socket.name for s in from_node.outputs)) > 1:
        if from_node.bl_idname in _ITEMS_NODE_SPECS or from_node.bl_idname in _TYPED_ITEMS_NODE_SPECS or from_node.type == 'GROUP':
            index = next((i for i, s in enumerate(from_node.outputs) if s.identifier == from_socket.identifier))
            return Subscript(Attr(val.expr, 'o'), Lit(index))
        key = _normalize(from_socket.identifier)
    else:
        key = _normalize(from_socket.name)
    if not key.isidentifier() or keyword.iskeyword(key):
        return Subscript(Attr(val.expr, 'o'), Lit(from_socket.name))
    return Attr(val.expr, f'o.{key}')

def _is_stable(expr: Expr) -> bool:
    if isinstance(expr, Ref):
        return True
    if isinstance(expr, Attr):
        return _is_stable(expr.base)
    return False
_BASE_NODE_PROPS: set[str] | None = None

def _base_node_props() -> set[str]:
    global _BASE_NODE_PROPS
    if _BASE_NODE_PROPS is None:
        try:
            import bpy
            _BASE_NODE_PROPS = set(bpy.types.Node.bl_rna.properties.keys())
        except Exception:
            _BASE_NODE_PROPS = set()
    return _BASE_NODE_PROPS

def _property_rna_name(cls: type, name: str, rna_props) -> str | None:
    if rna_props is not None and name in rna_props:
        return name
    attr = inspect.getattr_static(cls, name, None)
    if not isinstance(attr, property) or attr.fget is None:
        return None
    try:
        body = ast.parse(textwrap.dedent(inspect.getsource(attr.fget)))
    except (OSError, TypeError, SyntaxError):
        return None
    for sub in ast.walk(body):
        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Attribute) and isinstance(sub.value.value, ast.Attribute) and (sub.value.value.attr == 'node') and isinstance(sub.value.value.value, ast.Name) and (sub.value.value.value.id == 'self'):
            rna = sub.value.attr
            if rna_props is not None and rna in rna_props:
                return rna
    return None

def _non_default_props(node, cls: type) -> dict[str, Any]:
    try:
        sig = _signature(cls.__init__)
    except (TypeError, ValueError):
        return {}
    rna_props = getattr(getattr(node, 'bl_rna', None), 'properties', None)
    result: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        if param.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            continue
        if param.default is inspect.Parameter.empty:
            continue
        if _input_socket_by_kwarg(node, name) is not None:
            continue
        rna_name = _property_rna_name(cls, name, rna_props)
        if rna_name is None:
            continue
        if rna_name in _base_node_props():
            continue
        try:
            current = getattr(node, rna_name)
        except AttributeError:
            continue
        if current != param.default:
            result[name] = current
    return result

class _Factory(NamedTuple):
    path: str
    props: dict[str, Any]
    socket_params: dict[str, str]
    param_defaults: dict[str, Any]
    prop_params: dict[str, str]
_FACTORY_CACHE: dict[type, list[_Factory]] = {}

def _as_function(attr: Any):
    if isinstance(attr, (classmethod, staticmethod)):
        return attr.__func__
    if inspect.isfunction(attr):
        return attr
    return None

def _iter_factory_funcs(cls: type):
    for name, attr in vars(cls).items():
        if name.startswith('_'):
            continue
        func = _as_function(attr)
        if func is not None:
            yield (name, func, None)
            continue
        owner = None
        if inspect.isclass(attr) and attr.__module__ == cls.__module__:
            nested = attr
        elif not callable(attr) and type(attr).__module__ == cls.__module__ and inspect.isclass(type(attr)):
            nested = type(attr)
            owner = attr
        else:
            continue
        for sub_name, sub_attr in vars(nested).items():
            if sub_name.startswith('_'):
                continue
            sub_func = _as_function(sub_attr)
            if sub_func is not None:
                yield (f'{name}.{sub_name}', sub_func, owner)

def _parse_factory_func(func, owner: Any, cls: type) -> tuple[dict[str, Any], dict[str, str]] | None:
    try:
        source = textwrap.dedent(inspect.getsource(func))
        fn = ast.parse(source).body[0]
    except (OSError, TypeError, SyntaxError, IndexError):
        return None
    if not isinstance(fn, ast.FunctionDef):
        return None
    returns = [s for s in ast.walk(fn) if isinstance(s, ast.Return)]
    if len(returns) != 1 or not isinstance(returns[0].value, ast.Call):
        return None
    call = returns[0].value
    if not (isinstance(call.func, ast.Name) and call.func.id in ('cls', cls.__name__)):
        return None
    props: dict[str, Any] = {}
    socket_params: dict[str, str] = {}
    if call.args:
        try:
            init_params = [param for param in _signature(cls.__init__).parameters.values() if param.name != 'self' and param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        except (TypeError, ValueError):
            return None
        if len(call.args) > len(init_params):
            return None
        for arg, param in zip(call.args, init_params):
            if not isinstance(arg, ast.Name):
                return None
            socket_params[_normalize(param.name)] = arg.id
    for kw in call.keywords:
        if kw.arg is None:
            return None
        value = kw.value
        if isinstance(value, ast.Constant):
            props[kw.arg] = value.value
        elif isinstance(value, ast.Name):
            socket_params[_normalize(kw.arg)] = value.id
        elif isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name) and (value.value.id == 'self') and (owner is not None) and hasattr(owner, value.attr):
            props[kw.arg] = getattr(owner, value.attr)
        else:
            return None
    if not props:
        return None
    return (props, socket_params)

def _factory_param_defaults(func) -> dict[str, Any] | None:
    try:
        sig = _signature(func)
    except (TypeError, ValueError):
        return None
    defaults: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name in ('self', 'cls'):
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            return None
        defaults[name] = param.default
    return defaults

def _class_factories(cls: type) -> list[_Factory]:
    cached = _FACTORY_CACHE.get(cls)
    if cached is not None:
        return cached
    factories: list[_Factory] = []
    for path, func, owner in _iter_factory_funcs(cls):
        parsed = _parse_factory_func(func, owner, cls)
        if parsed is None:
            continue
        defaults = _factory_param_defaults(func)
        if defaults is None:
            continue
        props, socket_params = parsed
        keyword_only = {name for name, param in _signature(func).parameters.items() if param.kind is inspect.Parameter.KEYWORD_ONLY}
        prop_params = {key: param for key, param in socket_params.items() if param in keyword_only}
        socket_params = {key: param for key, param in socket_params.items() if param not in keyword_only}
        factories.append(_Factory(path, props, socket_params, defaults, prop_params))
    _FACTORY_CACHE[cls] = factories
    return factories

def _input_socket_by_kwarg(node, kwarg_name: str):
    normalized = _normalize(kwarg_name)
    for socket in node.inputs:
        if _normalize(socket.identifier) == normalized:
            return socket
    return None

def _factory_state_matches(node, props: dict[str, Any]) -> bool:
    rna_props = getattr(getattr(node, 'bl_rna', None), 'properties', None)
    for key, value in props.items():
        if rna_props is not None and key in rna_props:
            if getattr(node, key) != value:
                return False
            continue
        socket = _input_socket_by_kwarg(node, key)
        if socket is None or socket.is_linked or (not hasattr(socket, 'default_value')) or (not _eq(socket.default_value, value)):
            return False
    return True
_TYPE_FACTORY_PROPS = frozenset({'data_type', 'domain', 'input_type', 'socket_type'})
_DATA_TYPE_PROPS = frozenset({'data_type', 'input_type', 'socket_type'})

def _factory_call(func_prefix: str, node, cls: type, prop_values: dict[str, Any], socket_kwargs: dict[str, Expr], skip_input_id: str | None) -> Call | None:
    skip_key = _normalize(skip_input_id) if skip_input_id else None
    best: tuple[_Factory, dict[str, Expr], tuple[bool, int, int]] | None = None
    for factory in _class_factories(cls):
        if not _factory_state_matches(node, factory.props):
            continue
        covered = {_normalize(key) for key in factory.props}
        passed = {key: value for key, value in prop_values.items() if key not in factory.props and _normalize(key) in factory.prop_params}
        if set(prop_values) - set(factory.props) - set(passed):
            continue
        if not (factory.props and set(factory.props) <= _TYPE_FACTORY_PROPS or set(prop_values) or covered & set(socket_kwargs)):
            continue
        call_kwargs: dict[str, Expr] = {factory.prop_params[_normalize(key)]: Lit(value) for key, value in passed.items()}
        for key, expr in socket_kwargs.items():
            if key in covered:
                continue
            param = factory.socket_params.get(key)
            if param is None:
                break
            call_kwargs[param] = expr
        else:
            faithful = True
            for key, param in factory.socket_params.items():
                if param in call_kwargs or key == skip_key:
                    continue
                default = factory.param_defaults.get(param, inspect.Parameter.empty)
                if default is inspect.Parameter.empty or default is None or isinstance(default, Default):
                    continue
                socket = _input_socket_by_kwarg(node, key)
                if socket is None:
                    faithful = False
                    break
                if socket.is_linked or not hasattr(socket, 'default_value'):
                    continue
                if not _eq(socket.default_value, default):
                    call_kwargs[param] = Lit(socket.default_value)
            rank = (bool(_DATA_TYPE_PROPS & set(factory.props)), len(factory.props), -len(passed))
            if faithful and (best is None or rank > best[2]):
                ordered = {param: call_kwargs[param] for param in factory.param_defaults if param in call_kwargs}
                best = (factory, ordered, rank)
    if best is None:
        return None
    factory, call_kwargs, _ = best
    args: list[Expr] = []
    keyword_only = set(factory.prop_params.values())
    for param in factory.param_defaults:
        if param not in call_kwargs or param in keyword_only:
            break
        args.append(call_kwargs.pop(param))
    return Call(f'{func_prefix}.{factory.path}', args=args, kwargs=call_kwargs)

@dataclass(frozen=True)
class SocketMethodSpec:
    receiver: str
    method: str
    output: str | None = None
    params: tuple[tuple[str, str], ...] = ()
    require: tuple[tuple[str, Any], ...] = ()
    consumed_props: tuple[str, ...] = ()
    prop_kwargs: tuple[tuple[str, Any], ...] = ()
    receiver_socket_type: str | None = None
    require_sockets: tuple[tuple[str, str], ...] = ()
    always_args: int = 0
    max_positional: int | None = None
    receiver_list_prop: str | None = None
    receiver_structure: str | None = None

@dataclass(frozen=True)
class DissolveSpec:
    receiver: str
    outputs: tuple[tuple[str, str], ...]
    require: tuple[tuple[str, Any], ...] = ()
    consumed_props: tuple[str, ...] = ()
    receiver_socket_type: str | None = None
    receiver_structure: str | None = None

@dataclass(frozen=True)
class TupleMethodSpec:
    receiver: str
    method: str
    outputs: tuple[tuple[str, str], ...]
    params: tuple[tuple[str, str], ...] = ()
    receiver_socket_type: str | None = None
    require_sockets: tuple[tuple[str, str], ...] = ()
_DOMAIN_ATTR = {'POINT': 'point', 'EDGE': 'edge', 'FACE': 'face', 'CORNER': 'corner', 'CURVE': 'spline', 'INSTANCE': 'instance', 'LAYER': 'layer'}
_SWITCH_METHOD = {'FLOAT': 'float', 'INT': 'integer', 'BOOLEAN': 'boolean', 'VECTOR': 'vector', 'RGBA': 'color', 'ROTATION': 'rotation', 'MATRIX': 'matrix', 'STRING': 'string', 'MENU': 'menu', 'OBJECT': 'object', 'IMAGE': 'image', 'GEOMETRY': 'geometry', 'COLLECTION': 'collection', 'MATERIAL': 'material', 'BUNDLE': 'bundle', 'CLOSURE': 'closure', 'FONT': 'font', 'SOUND': 'sound'}
_DATA_TYPE_SOCKET = {'FLOAT': 'VALUE', 'INT': 'INT', 'FLOAT_VECTOR': 'VECTOR', 'BOOLEAN': 'BOOLEAN', 'FLOAT_COLOR': 'RGBA', 'QUATERNION': 'ROTATION', 'FLOAT4X4': 'MATRIX', 'TRANSFORM': 'MATRIX', 'VECTOR': 'VECTOR', 'RGBA': 'RGBA', 'ROTATION': 'ROTATION', 'MATRIX': 'MATRIX', 'STRING': 'STRING'}
_FIELD_PROPS = ('domain', 'data_type')
_FIELD_STAT_PARAMS = (('Group Index', 'group_index'),)
_MAP_RANGE_PROP_KWARGS = (('clamp', True), ('interpolation_type', 'LINEAR'))

def _field_spec(method: str, output: str, *params) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Value', method=method, output=output, params=tuple(params), consumed_props=_FIELD_PROPS, receiver_socket_type='{data_type}')

def _vector_op_spec(operation: str, method: str, output: str, *params, always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Vector', method=method, output=output, params=tuple(params), require=(('operation', operation),), consumed_props=('operation',), receiver_socket_type='VECTOR', always_args=always_args)

def _string_spec(method: str, output: str, *params, case: str | None=None, always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='String', method=method, output=output, params=tuple(params), require_sockets=(('Case', case),) if case else (), receiver_socket_type='STRING', always_args=always_args)

def _match_string_spec(method: str, operation: str) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='String', method=method, output='Result', params=(('Key', 'search'),), require_sockets=(('Operation', operation),), receiver_socket_type='STRING', always_args=1)

def _matrix_spec(method: str, output: str) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Matrix', method=method, output=output, receiver_socket_type='MATRIX')

def _math_unary_spec(operation: str, method: str, *args: str, always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Value', method=method, output='Value', params=tuple(((f'Value_{i + 1:03d}', arg) for i, arg in enumerate(args))), require=(('operation', operation),), consumed_props=('operation',), receiver_socket_type='VALUE', always_args=always_args)

def _int_math_unary_spec(operation: str, method: str, *args: str, always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Value', method=method, output='Value', params=tuple(((f'Value_{i + 1:03d}', arg) for i, arg in enumerate(args))), require=(('operation', operation),), consumed_props=('operation',), receiver_socket_type='INT', always_args=always_args)

def _list_spec(method: str, output: str, *params: tuple[str, str], type_prop: str='socket_type', always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='List', method=method, output=output, params=tuple(params), consumed_props=(type_prop,), receiver_list_prop=type_prop, always_args=always_args)

def _mix_spec(data_type: str, attr: str, suffix: str) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Factor_Float', method=f'mix.{attr}', output=f'Result_{suffix}', params=((f'A_{suffix}', 'a'), (f'B_{suffix}', 'b')), require=(('data_type', data_type),), consumed_props=('data_type',), receiver_socket_type='VALUE', always_args=2)

def _grid_spec(method: str, output: str, *params: tuple[str, str], receiver_socket_type: str='{data_type}', data_type: bool=True, always_args: int=0) -> SocketMethodSpec:
    return SocketMethodSpec(receiver='Grid', method=method, output=output, params=tuple(params), consumed_props=('data_type',) if data_type else (), receiver_socket_type=receiver_socket_type, receiver_structure='GRID', always_args=always_args)
_SOCKET_METHODS: dict[str, list[SocketMethodSpec]] = {'GeometryNodeSwitch': [SocketMethodSpec(receiver='Switch', method='switch.{input_type}', output='Output', params=(('False', 'false'), ('True', 'true')), consumed_props=('input_type',), receiver_socket_type='BOOLEAN')], 'ShaderNodeMapRange': [SocketMethodSpec(receiver='Value', method='map_range', output='Result', params=(('From Min', 'from_min'), ('From Max', 'from_max'), ('To Min', 'to_min'), ('To Max', 'to_max'), ('Steps', 'steps')), require=(('data_type', 'FLOAT'),), consumed_props=('data_type',), prop_kwargs=_MAP_RANGE_PROP_KWARGS, receiver_socket_type='VALUE', max_positional=4), SocketMethodSpec(receiver='Vector', method='map_range', output='Vector', params=(('From_Min_FLOAT3', 'from_min'), ('From_Max_FLOAT3', 'from_max'), ('To_Min_FLOAT3', 'to_min'), ('To_Max_FLOAT3', 'to_max'), ('Steps_FLOAT3', 'steps')), require=(('data_type', 'FLOAT_VECTOR'),), consumed_props=('data_type',), prop_kwargs=_MAP_RANGE_PROP_KWARGS, receiver_socket_type='VECTOR', max_positional=4)], 'GeometryNodeFieldAtIndex': [_field_spec('{domain}.at', 'Value', ('Index', 'index'))], 'GeometryNodeFieldOnDomain': [_field_spec('{domain}.evaluate', 'Value')], 'GeometryNodeAccumulateField': [_field_spec('{domain}.leading', 'Leading', *_FIELD_STAT_PARAMS), _field_spec('{domain}.trailing', 'Trailing', *_FIELD_STAT_PARAMS), _field_spec('{domain}.total', 'Total', *_FIELD_STAT_PARAMS)], 'GeometryNodeFieldAverage': [_field_spec('{domain}.mean', 'Mean', *_FIELD_STAT_PARAMS), _field_spec('{domain}.median', 'Median', *_FIELD_STAT_PARAMS)], 'GeometryNodeFieldMinAndMax': [_field_spec('{domain}.min', 'Min', *_FIELD_STAT_PARAMS), _field_spec('{domain}.max', 'Max', *_FIELD_STAT_PARAMS)], 'GeometryNodeFieldVariance': [_field_spec('{domain}.std_dev', 'Standard Deviation', *_FIELD_STAT_PARAMS), _field_spec('{domain}.variance', 'Variance', *_FIELD_STAT_PARAMS)], 'ShaderNodeVectorMath': [_vector_op_spec('DOT_PRODUCT', 'dot', 'Value', ('Vector_001', 'vector')), _vector_op_spec('LENGTH', 'length', 'Value'), _vector_op_spec('NORMALIZE', 'normalize', 'Vector'), _vector_op_spec('CROSS_PRODUCT', 'cross', 'Vector', ('Vector_001', 'other')), _vector_op_spec('DISTANCE', 'distance', 'Value', ('Vector_001', 'other')), _vector_op_spec('PROJECT', 'project', 'Vector', ('Vector_001', 'other')), _vector_op_spec('REFLECT', 'reflect', 'Vector', ('Vector_001', 'normal')), _vector_op_spec('MULTIPLY_ADD', 'mul_add', 'Vector', ('Vector_001', 'multiplier'), ('Vector_002', 'addend'), always_args=2), *(_vector_op_spec(op, method, 'Vector') for op, method in (('FLOOR', 'floor'), ('CEIL', 'ceil'), ('ROUND', 'round'), ('FRACTION', 'fraction'), ('SIGN', 'sign'), ('SINE', 'sin'), ('COSINE', 'cos'), ('TANGENT', 'tan'))), _vector_op_spec('MINIMUM', 'min', 'Vector', ('Vector_001', 'value'), always_args=1), _vector_op_spec('MAXIMUM', 'max', 'Vector', ('Vector_001', 'value'), always_args=1), _vector_op_spec('SNAP', 'snap', 'Vector', ('Vector_001', 'increment'), always_args=1), _vector_op_spec('WRAP', 'wrap', 'Vector', ('Vector_002', 'min'), ('Vector_001', 'max'), always_args=2), _vector_op_spec('FACEFORWARD', 'faceforward', 'Vector', ('Vector_001', 'incident'), ('Vector_002', 'reference'), always_args=2), _vector_op_spec('REFRACT', 'refract', 'Vector', ('Vector_001', 'normal'), ('Scale', 'ior'), always_args=2)], 'FunctionNodeRotateVector': [SocketMethodSpec(receiver='Vector', method='rotate', output='Vector', params=(('Rotation', 'rotation'),), receiver_socket_type='VECTOR', always_args=1)], 'FunctionNodeTransformPoint': [SocketMethodSpec(receiver='Vector', method='transform', output='Vector', params=(('Transform', 'matrix'),), receiver_socket_type='VECTOR', always_args=1)], 'ShaderNodeMath': [_math_unary_spec(*args) for args in [('SINE', 'sin'), ('COSINE', 'cos'), ('TANGENT', 'tan'), ('ARCSINE', 'asin'), ('ARCCOSINE', 'acos'), ('ARCTANGENT', 'atan'), ('HYPERBOLIC_SINE', 'sinh'), ('HYPERBOLIC_COSINE', 'cosh'), ('HYPERBOLIC_TANGENT', 'tanh'), ('EXPONENTIAL', 'exp'), ('TRUNC', 'truncate'), ('FRACT', 'fraction'), ('SQRT', 'sqrt'), ('FLOOR', 'floor'), ('CEIL', 'ceil'), ('ROUND', 'round'), ('RADIANS', 'to_radians'), ('DEGREES', 'to_degrees'), ('SIGN', 'sign'), ('MULTIPLY_ADD', 'mul_add', 'multiplier', 'addend'), ('PINGPONG', 'ping_pong', 'value'), ('LOGARITHM', 'log', 'base'), ('ARCTAN2', 'atan2', 'value'), ('INVERSE_SQRT', 'inverse_sqrt')]] + [_math_unary_spec(op, method, 'value', 'distance', always_args=2) for op, method in (('SMOOTH_MIN', 'smooth_min'), ('SMOOTH_MAX', 'smooth_max'))] + [_math_unary_spec(op, method, 'value', always_args=1) for op, method in (('MINIMUM', 'min'), ('MAXIMUM', 'max'))] + [SocketMethodSpec(receiver='Value', method='wrap', output='Value', params=(('Value_002', 'min'), ('Value_001', 'max')), require=(('operation', 'WRAP'),), consumed_props=('operation',), receiver_socket_type='VALUE')], 'FunctionNodeIntegerMath': [_int_math_unary_spec(*args) for args in (('SIGN', 'sign'), ('MULTIPLY_ADD', 'mul_add', 'multiplier', 'addend'))] + [_int_math_unary_spec(op, method, *args, always_args=1) for op, method, *args in (('MINIMUM', 'min', 'value'), ('MAXIMUM', 'max', 'value'), ('DIVIDE_ROUND', 'divide_round', 'divisor'), ('DIVIDE_CEIL', 'divide_ceiling', 'divisor'), ('GCD', 'gcd', 'value'), ('LCM', 'lcm', 'value'))], 'GeometryNodeListLength': [_list_spec('list_length', 'Length', type_prop='data_type')], 'GeometryNodeFilterList': [_list_spec('filter', 'Selection', ('Selection', 'selection'))], 'GeometryNodeSortList': [_list_spec('sort', 'List', ('Sort Weight', 'sort_weight'), ('Group ID', 'group_id'), ('Selection', 'selection'), always_args=1)], 'ShaderNodeClamp': [SocketMethodSpec(receiver='Value', method='clamp', output='Result', params=(('Min', 'min'), ('Max', 'max')), require=(('clamp_type', 'MINMAX'),), consumed_props=('clamp_type',), receiver_socket_type='VALUE')], 'FunctionNodeSliceString': [_string_spec('slice', 'String', ('Position', 'position'), ('Length', 'length'))], 'FunctionNodeReplaceString': [_string_spec('replace', 'String', ('Find', 'find'), ('Replace', 'replace'), always_args=2)], 'FunctionNodeReverseString': [_string_spec('reverse', 'String')], 'FunctionNodeStringLength': [_string_spec('length', 'Length')], 'FunctionNodeMatchString': [_match_string_spec('starts_with', 'Starts With'), _match_string_spec('ends_with', 'Ends With'), _match_string_spec('contains', 'Contains')], 'FunctionNodeSetStringCase': [_string_spec('uppercase', 'String', case='Uppercase'), _string_spec('lowercase', 'String', case='Lowercase')], 'FunctionNodeTrimString': [_string_spec('trim', 'String', ('Characters', 'characters'), ('Whitespace', 'whitespace'), ('Start', 'start'), ('End', 'end'))], 'FunctionNodeSplitString': [_string_spec('split', 'List', ('Separator', 'separator'))], 'FunctionNodeStringToValue': [SocketMethodSpec(receiver='String', method='to_float', output='Value', require=(('data_type', 'FLOAT'),), consumed_props=('data_type',), receiver_socket_type='STRING'), SocketMethodSpec(receiver='String', method='to_integer', output='Value', params=(('Base', 'base'),), require=(('data_type', 'INT'),), consumed_props=('data_type',), receiver_socket_type='STRING')], 'FunctionNodeValueToString': [SocketMethodSpec(receiver='Value', method='to_string', output='String', params=(('Decimals', 'decimals'),), require=(('data_type', 'FLOAT'),), consumed_props=('data_type',), receiver_socket_type='VALUE'), SocketMethodSpec(receiver='Value', method='to_string', output='String', params=(('Base', 'base'), ('Padding', 'padding')), require=(('data_type', 'INT'),), consumed_props=('data_type',), receiver_socket_type='INT')], 'FunctionNodeInvertMatrix': [_matrix_spec('invert', 'Matrix')], 'FunctionNodeTransposeMatrix': [_matrix_spec('transpose', 'Matrix')], 'FunctionNodeMatrixDeterminant': [_matrix_spec('determinant', 'Determinant')], 'FunctionNodeTransformDirection': [SocketMethodSpec(receiver='Direction', method='transform_direction', output='Direction', params=(('Transform', 'matrix'),), receiver_socket_type='VECTOR', always_args=1)], 'FunctionNodeInvertRotation': [SocketMethodSpec(receiver='Rotation', method='invert', output='Rotation', receiver_socket_type='ROTATION')], 'FunctionNodeRotateRotation': [SocketMethodSpec(receiver='Rotation', method='rotate', output='Rotation', params=(('Rotate By', 'rotation'),), prop_kwargs=(('rotation_space', 'GLOBAL'),), receiver_socket_type='ROTATION', always_args=1)], 'FunctionNodeRotationToEuler': [SocketMethodSpec(receiver='Rotation', method='to_euler', output='Euler', receiver_socket_type='ROTATION')], 'FunctionNodeBitMath': [SocketMethodSpec(receiver='A', method=method, output='Value', params=(('Shift', 'amount'),), require=(('operation', operation),), consumed_props=('operation',), receiver_socket_type='INT', always_args=1) for operation, method in (('SHIFT', 'shift'), ('ROTATE', 'rotate'))], 'FunctionNodeProjectPoint': [SocketMethodSpec(receiver='Vector', method='project_point', output='Vector', params=(('Transform', 'matrix'),), receiver_socket_type='VECTOR', always_args=1)], 'FunctionNodeEulerToRotation': [SocketMethodSpec(receiver='Euler', method='euler_to_rotation', output='Rotation', receiver_socket_type='VECTOR')], 'NodeImplicitConversion': [SocketMethodSpec(receiver='Value', method='to_float', output='Value', require=(('data_type', 'FLOAT'),), consumed_props=('data_type',), receiver_socket_type='INT')], 'ShaderNodeGamma': [SocketMethodSpec(receiver='Color', method='gamma', output='Color', params=(('Gamma', 'gamma'),), receiver_socket_type='RGBA', always_args=1)], 'FunctionNodeHashValue': [SocketMethodSpec(receiver='Value', method='hash', output='Hash', params=(('Seed', 'seed'),), consumed_props=('data_type',), receiver_socket_type='{data_type}')], 'GeometryNodeBlurAttribute': [SocketMethodSpec(receiver='Value', method='blur', output='Value', params=(('Iterations', 'iterations'), ('Weight', 'weight')), consumed_props=('data_type',), receiver_socket_type='{data_type}')], 'GeometryNodeMaterialSelection': [SocketMethodSpec(receiver='Material', method='selection', output='Selection', receiver_socket_type='MATERIAL')], 'GeometryNodeGetGeometryBundle': [SocketMethodSpec(receiver='Geometry', method='bundle', output='Bundle', receiver_socket_type='GEOMETRY')], 'GeometryNodeSetGeometryBundle': [SocketMethodSpec(receiver='Geometry', method='set_bundle', output='Geometry', params=(('Bundle', 'bundle'),), receiver_socket_type='GEOMETRY', always_args=1)], 'NodeGetBundleItem': [SocketMethodSpec(receiver='Bundle', method='get.{socket_type}', output='Item', params=(('Path', 'path'),), consumed_props=('socket_type',), receiver_socket_type='BUNDLE', always_args=1), SocketMethodSpec(receiver='Bundle', method='has', output='Exists', params=(('Path', 'path'),), require=(('socket_type', 'FLOAT'),), receiver_socket_type='BUNDLE', always_args=1)], 'NodeGetNestedBundlePaths': [SocketMethodSpec(receiver='Bundle', method='paths', output='Paths', params=(('Mode', 'mode'), ('Pattern Mode', 'pattern_mode'), ('Bundle Type', 'bundle_type'), ('Data Type', 'data_type')), receiver_socket_type='BUNDLE')], 'ShaderNodeMix': [_mix_spec('FLOAT', 'float', 'Float'), _mix_spec('VECTOR', 'vector', 'Vector'), _mix_spec('RGBA', 'color', 'Color'), _mix_spec('ROTATION', 'rotation', 'Rotation')], 'GeometryNodeSetGridBackground': [_grid_spec('set_background', 'Grid', ('Background', 'background'), ('Update Inactive', 'update_inactive'), always_args=1)], 'GeometryNodeSetGridTransform': [_grid_spec('set_transform', 'Grid', ('Transform', 'matrix'), always_args=1)], 'GeometryNodeGridAdvect': [_grid_spec('advect', 'Grid', ('Velocity', 'velocity'), ('Time Step', 'time_step'), ('Integration Scheme', 'integration_scheme'), ('Limiter', 'limiter'), always_args=1)], 'GeometryNodeGridMean': [_grid_spec('mean', 'Grid', ('Width', 'width'), ('Iterations', 'iterations'))], 'GeometryNodeGridMedian': [_grid_spec('median', 'Grid', ('Width', 'width'), ('Iterations', 'iterations'))], 'GeometryNodeGridGradient': [_grid_spec('gradient', 'Gradient', receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeGridLaplacian': [_grid_spec('laplacian', 'Laplacian', receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridFillet': [_grid_spec('sdf_fillet', 'Grid', ('Iterations', 'iterations'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridLaplacian': [_grid_spec('sdf_laplacian', 'Grid', ('Iterations', 'iterations'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridMean': [_grid_spec('sdf_mean', 'Grid', ('Width', 'width'), ('Iterations', 'iterations'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridMeanCurvature': [_grid_spec('sdf_mean_curvature', 'Grid', ('Iterations', 'iterations'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridMedian': [_grid_spec('sdf_median', 'Grid', ('Width', 'width'), ('Iterations', 'iterations'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeSDFGridOffset': [_grid_spec('sdf_offset', 'Grid', ('Distance', 'distance'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeGridToMesh': [_grid_spec('to_mesh', 'Mesh', ('Threshold', 'threshold'), ('Adaptivity', 'adaptivity'), receiver_socket_type='VALUE', data_type=False)], 'GeometryNodeGridCurl': [_grid_spec('curl', 'Curl', receiver_socket_type='VECTOR', data_type=False)], 'GeometryNodeGridDivergence': [_grid_spec('divergence', 'Divergence', receiver_socket_type='VECTOR', data_type=False)], 'GeometryNodeSampleGrid': [_grid_spec('sample', 'Value', ('Position', 'position'), ('Interpolation', 'interpolation'))], 'GeometryNodeSampleGridIndex': [_grid_spec('sample_index', 'Value', ('X', 'x'), ('Y', 'y'), ('Z', 'z'))], 'GeometryNodeGridClip': [_grid_spec('clip', 'Grid', ('Min X', 'min_x'), ('Min Y', 'min_y'), ('Min Z', 'min_z'), ('Max X', 'max_x'), ('Max Y', 'max_y'), ('Max Z', 'max_z'))], 'GeometryNodeGridDilateAndErode': [_grid_spec('dilate_erode', 'Grid', ('Steps', 'steps'), ('Connectivity', 'connectivity'), ('Tiles', 'tiles'))], 'GeometryNodeGridPrune': [_grid_spec('prune', 'Grid', ('Threshold', 'threshold'), ('Mode', 'mode'), always_args=1)], 'GeometryNodeGridVoxelize': [_grid_spec('voxelize', 'Grid')]}
_DISSOLVE_SPECS: dict[str, DissolveSpec] = {'ShaderNodeSeparateXYZ': DissolveSpec(receiver='Vector', outputs=(('X', 'x'), ('Y', 'y'), ('Z', 'z')), receiver_socket_type='VECTOR'), 'FunctionNodeSeparateTransform': DissolveSpec(receiver='Transform', outputs=(('Translation', 'translation'), ('Rotation', 'rotation'), ('Scale', 'scale')), receiver_socket_type='MATRIX'), 'FunctionNodeSeparateColor': DissolveSpec(receiver='Color', outputs=(('Red', 'r'), ('Green', 'g'), ('Blue', 'b'), ('Alpha', 'a')), require=(('mode', 'RGB'),), receiver_socket_type='RGBA'), 'GeometryNodeGridInfo': DissolveSpec(receiver='Grid', outputs=(('Transform', 'transform'), ('Background Value', 'background_value')), consumed_props=('data_type',), receiver_socket_type='{data_type}', receiver_structure='GRID')}
_TUPLE_METHODS: dict[str, TupleMethodSpec] = {'FunctionNodeFindInString': TupleMethodSpec(receiver='String', method='find', outputs=(('First Found', 'first_found'), ('Count', 'count')), params=(('Search', 'search'),), receiver_socket_type='STRING', require_sockets=(('Mode', 'From Start'),)), 'FunctionNodeMatrixSVD': TupleMethodSpec(receiver='Matrix', method='svd', outputs=(('U', 'u'), ('S', 's'), ('V', 'v')), receiver_socket_type='MATRIX'), 'FunctionNodeRotationToQuaternion': TupleMethodSpec(receiver='Rotation', method='to_quaternion', outputs=(('W', 'w'), ('X', 'x'), ('Y', 'y'), ('Z', 'z')), receiver_socket_type='ROTATION'), 'GeometryNodeCollectionChildren': TupleMethodSpec(receiver='Collection', method='children', outputs=(('Collections', 'collections'), ('Objects', 'objects')), params=(('Recursive', 'recursive'),), receiver_socket_type='COLLECTION'), 'FunctionNodeRotationToAxisAngle': TupleMethodSpec(receiver='Rotation', method='to_axis_angle', outputs=(('Axis', 'axis'), ('Angle', 'angle')), receiver_socket_type='ROTATION')}

def _format_method(spec: SocketMethodSpec, node) -> str | None:
    method = spec.method
    if '{domain}' in method:
        attr = _DOMAIN_ATTR.get(getattr(node, 'domain', ''))
        if attr is None:
            return None
        method = method.replace('{domain}', attr)
    if '{input_type}' in method:
        attr = _SWITCH_METHOD.get(getattr(node, 'input_type', ''))
        if attr is None:
            return None
        method = method.replace('{input_type}', attr)
    if '{socket_type}' in method:
        attr = _SWITCH_METHOD.get(getattr(node, 'socket_type', ''))
        if attr is None:
            return None
        method = method.replace('{socket_type}', attr)
    return method

def _input_socket_by_identifier(node, identifier: str):
    for socket in node.inputs:
        if socket.identifier == identifier:
            return socket
    return None

def _list_receiver_ok(node, link, type_prop: str) -> bool:
    if getattr(link.from_socket, 'inferred_structure_type', None) != 'LIST':
        return False
    prop = getattr(node, type_prop, None)
    return prop is not None and prop.replace('FLOAT', 'VALUE') == link.from_socket.type

def _receiver_reproduces_structure(ctx: EmitContext, link, structure: str) -> bool:
    if getattr(link.from_socket, 'inferred_structure_type', None) != structure:
        return False
    return _fresh_output_structure(ctx.node_tree.bl_idname, link.from_node.bl_idname, link.from_socket.identifier) == structure

def _match_socket_method(ctx: EmitContext, node) -> tuple[SocketMethodSpec, str, str] | None:
    specs = _SOCKET_METHODS.get(node.bl_idname)
    if not specs:
        return None
    found = _find_cls(node.bl_idname)
    if found is None:
        return None
    incoming = {link.to_socket.identifier: link for link in ctx.incoming.get(node.name, ())}
    for spec in specs:
        if any((getattr(node, key, None) != value for key, value in spec.require)):
            continue
        receiver_link = incoming.get(spec.receiver)
        if receiver_link is None:
            continue
        expected_type = spec.receiver_socket_type
        if expected_type == '{data_type}':
            expected_type = _DATA_TYPE_SOCKET.get(getattr(node, 'data_type', ''))
            if expected_type is None:
                continue
        if expected_type is not None and receiver_link.from_socket.type != expected_type:
            continue
        if spec.receiver_structure is not None and (not _receiver_reproduces_structure(ctx, receiver_link, spec.receiver_structure)):
            continue
        if spec.receiver_list_prop is not None and (not _list_receiver_ok(node, receiver_link, spec.receiver_list_prop)):
            continue
        if not all(((socket := _input_socket_by_identifier(node, identifier)) is not None and (not socket.is_linked) and hasattr(socket, 'default_value') and _eq(socket.default_value, value) for identifier, value in spec.require_sockets)):
            continue
        method = _format_method(spec, node)
        if method is None:
            continue
        out_id = spec.output or (node.outputs[0].identifier if node.outputs else '')
        if any((link.from_socket.identifier != out_id for link in ctx.outgoing.get(node.name, ()))):
            continue
        param_ids = {pid for pid, _ in spec.params}
        if set(incoming) - {spec.receiver} - param_ids:
            continue
        _, cls = found
        uncovered = set(_non_default_props(node, cls)) - set(spec.consumed_props) - {key for key, _ in spec.require} - {key for key, _ in spec.prop_kwargs}
        if uncovered:
            continue
        spec_ids = param_ids | {spec.receiver} | {i for i, _ in spec.require_sockets}
        fresh_defaults = _get_blender_socket_defaults(node.id_data.bl_idname, node.bl_idname)
        if any((socket.identifier not in spec_ids and socket.identifier not in incoming and socket.enabled and hasattr(socket, 'default_value') and ((fresh := fresh_defaults.get(socket.identifier)) is not None) and (not _eq(socket.default_value, fresh)) for socket in node.inputs)):
            continue
        return (spec, method, out_id)
    return None

def _socket_method_val(ctx: EmitContext, node) -> _Val | None:
    dissolve = _DISSOLVE_SPECS.get(node.bl_idname)
    if dissolve is not None:
        return _dissolve_val(ctx, node, dissolve)
    tuple_spec = _TUPLE_METHODS.get(node.bl_idname)
    if tuple_spec is not None:
        return _tuple_method_val(ctx, node, tuple_spec)
    matched = _match_socket_method(ctx, node)
    if matched is None:
        return None
    spec, method, out_id = matched
    incoming = {link.to_socket.identifier: link for link in ctx.incoming.get(node.name, ())}
    receiver = ctx.socket_expr(incoming[spec.receiver])
    kwargs: dict[str, Expr] = {}
    blender_defaults: dict[str, object] | None = None
    for index, (identifier, param) in enumerate(spec.params):
        link = incoming.get(identifier)
        if link is not None:
            kwargs[param] = ctx.upstream_expr(link)
            continue
        socket = _input_socket_by_identifier(node, identifier)
        if socket is None or not hasattr(socket, 'default_value'):
            continue
        value = socket.default_value
        if index >= spec.always_args:
            if blender_defaults is None:
                blender_defaults = _get_blender_socket_defaults(ctx.node_tree.bl_idname, node.bl_idname)
            default = blender_defaults.get(identifier)
            if default is not None:
                if _eq(value, default):
                    continue
            elif _is_zero(value):
                continue
        kwargs[param] = Lit(value)
    for prop, default in spec.prop_kwargs:
        current = getattr(node, prop)
        if current != default:
            kwargs[prop] = Lit(current)
    args: list[Expr] = []
    for _, param in spec.params:
        if param not in kwargs:
            break
        if spec.max_positional is not None and len(args) >= spec.max_positional:
            break
        args.append(kwargs.pop(param))
    return _Val(MethodCall(receiver, method, args=args, kwargs=kwargs), is_socket=True, socket_id=out_id)

def _dissolve_val(ctx: EmitContext, node, spec: DissolveSpec) -> _Val | None:
    if any((getattr(node, key, None) != value for key, value in spec.require)):
        return None
    links = ctx.incoming.get(node.name, ())
    if len(links) != 1 or links[0].to_socket.identifier != spec.receiver:
        return None
    source = links[0].from_socket
    siblings = sum((1 for out in ctx.outgoing.get(links[0].from_node.name, ()) if out.from_socket.identifier == source.identifier and out.to_node.bl_idname == node.bl_idname and (out.to_socket.identifier == spec.receiver)))
    if siblings > 1:
        return None
    expected_type = spec.receiver_socket_type
    if expected_type == '{data_type}':
        expected_type = _DATA_TYPE_SOCKET.get(getattr(node, 'data_type', ''))
        if expected_type is None:
            return None
    if expected_type is not None and links[0].from_socket.type != expected_type:
        return None
    if spec.receiver_structure is not None and (not _receiver_reproduces_structure(ctx, links[0], spec.receiver_structure)):
        return None
    found = _find_cls(node.bl_idname)
    if found is not None:
        uncovered = set(_non_default_props(node, found[1])) - {key for key, _ in spec.require} - set(spec.consumed_props)
        if uncovered:
            return None
    out_links = ctx.outgoing.get(node.name, ())
    receiver = ctx.socket_expr(links[0])
    if len(out_links) > 1 and (not _is_stable(receiver)):
        receiver = ctx.promote_to_var(links[0], receiver)
    return _Val(None, outputs={ident: Attr(receiver, attr) for ident, attr in spec.outputs})

def _tuple_method_val(ctx: EmitContext, node, spec: TupleMethodSpec) -> _Val | None:
    incoming = {link.to_socket.identifier: link for link in ctx.incoming.get(node.name, ())}
    receiver_link = incoming.get(spec.receiver)
    if receiver_link is None:
        return None
    if spec.receiver_socket_type is not None and receiver_link.from_socket.type != spec.receiver_socket_type:
        return None
    if not all(((socket := _input_socket_by_identifier(node, identifier)) is not None and (not socket.is_linked) and hasattr(socket, 'default_value') and _eq(socket.default_value, value) for identifier, value in spec.require_sockets)):
        return None
    param_ids = {pid for pid, _ in spec.params}
    if set(incoming) - {spec.receiver} - param_ids:
        return None
    found = _find_cls(node.bl_idname)
    if found is None or _non_default_props(node, found[1]):
        return None
    out_links = ctx.outgoing.get(node.name, ())
    if not out_links:
        return None
    args: list[Expr] = []
    for identifier, _param in spec.params:
        link = incoming.get(identifier)
        if link is not None:
            args.append(ctx.upstream_expr(link))
            continue
        socket = _input_socket_by_identifier(node, identifier)
        if socket is None or not hasattr(socket, 'default_value'):
            return None
        args.append(Lit(socket.default_value))
    base: Expr = MethodCall(ctx.socket_expr(receiver_link), spec.method, args)
    if len(out_links) > 1:
        var = _make_var(node.bl_label or 'result', ctx.counter)
        ctx.pending_lines.append(f'    {var} = {base.render()}')
        base = Ref(var)
    return _Val(None, outputs={ident: Attr(base, attr) for ident, attr in spec.outputs})
EmitterFn = Callable[[Any, EmitContext], 'Expr | _Val | None']
_EMITTERS: dict[str, EmitterFn] = {}

def register_emitter(bl_idname: str) -> Callable[[EmitterFn], EmitterFn]:

    def decorator(fn: EmitterFn) -> EmitterFn:
        _EMITTERS[bl_idname] = fn
        return fn
    return decorator
_LIFT_BINARY: dict[str, dict[str, str]] = {'ShaderNodeMath': {'ADD': '+', 'SUBTRACT': '-', 'MULTIPLY': '*', 'DIVIDE': '/', 'POWER': '**', 'FLOORED_MODULO': '%'}, 'ShaderNodeVectorMath': {'ADD': '+', 'SUBTRACT': '-', 'MULTIPLY': '*', 'DIVIDE': '/', 'MODULO': '%', 'SCALE': '*'}, 'FunctionNodeIntegerMath': {'ADD': '+', 'SUBTRACT': '-', 'MULTIPLY': '*', 'POWER': '**', 'FLOORED_MODULO': '%', 'DIVIDE_FLOOR': '//'}, 'FunctionNodeBooleanMath': {'AND': '&', 'OR': '|', 'XOR': '^'}, 'FunctionNodeBitMath': {'AND': '&', 'OR': '|', 'XOR': '^'}}
_LIFT_UNARY: dict[str, dict[str, str]] = {'FunctionNodeBooleanMath': {'NOT': '~'}, 'FunctionNodeBitMath': {'NOT': '~'}, 'FunctionNodeIntegerMath': {'NEGATE': '-'}}
_LIFT_UNARY_CALL: dict[str, dict[str, str]] = {'ShaderNodeMath': {'ABSOLUTE': 'abs'}, 'ShaderNodeVectorMath': {'ABSOLUTE': 'abs'}, 'FunctionNodeIntegerMath': {'ABSOLUTE': 'abs'}}

def _lift_pair(node) -> tuple[Any, Any] | None:
    if node.bl_idname == 'ShaderNodeVectorMath' and getattr(node, 'operation', '') == 'SCALE':
        if len(node.inputs) > 3:
            return (node.inputs[0], node.inputs[3])
        return None
    if len(node.inputs) >= 2:
        return (node.inputs[0], node.inputs[1])
    return None

class _LiftPlan(NamedTuple):
    kind: str
    op: str
    sockets: tuple

def _linked_src_types(ctx: EmitContext, node) -> dict[str, str]:
    return {link.to_socket.identifier: link.from_socket.type for link in ctx.incoming.get(node.name, ())}

def _operator_dispatch_ok(node, pair, linked_ids: set[str], src_types) -> bool:
    if src_types is None:
        return True
    if node.bl_idname == 'ShaderNodeVectorMath':
        if not any((src_types.get(s.identifier) == 'VECTOR' for s in pair)):
            return False
        operation = getattr(node, 'operation', '')
        if operation in ('SCALE', 'MULTIPLY'):
            second_type = src_types.get(pair[1].identifier)
            second_is_scalar = second_type in ('VALUE', 'INT')
            if operation == 'SCALE' and second_type is not None and (not second_is_scalar):
                return False
            if operation == 'MULTIPLY' and second_is_scalar:
                return False
        return True
    if node.bl_idname == 'ShaderNodeMath':
        dispatcher = next((s.identifier for s in pair if s.identifier in linked_ids), None)
        if dispatcher is not None and src_types.get(dispatcher) in ('RGBA', 'VECTOR'):
            return False
        if getattr(node, 'operation', '') == 'DIVIDE':
            return True
        return any((s.identifier not in linked_ids or src_types.get(s.identifier) == 'VALUE' for s in pair))
    if node.bl_idname == 'FunctionNodeIntegerMath':
        return all((s.identifier not in linked_ids or src_types.get(s.identifier) == 'INT' for s in pair))
    if node.bl_idname in ('FunctionNodeBooleanMath', 'FunctionNodeBitMath'):
        return _logic_dispatch_ok(node, pair, linked_ids, src_types)
    return True

def _logic_dispatch_ok(node, sockets, linked_ids: set[str], src_types) -> bool:
    dispatcher = next((s.identifier for s in sockets if s.identifier in linked_ids), None)
    is_int = dispatcher is not None and src_types.get(dispatcher) == 'INT'
    return is_int == (node.bl_idname == 'FunctionNodeBitMath')

def _lift_plan(node, linked_ids: set[str], src_types: dict[str, str] | None=None) -> _LiftPlan | None:
    if getattr(node, 'use_clamp', False):
        return None
    operation = getattr(node, 'operation', '')
    binary = _LIFT_BINARY.get(node.bl_idname, {})
    if operation in binary:
        pair = _lift_pair(node)
        if pair is not None:
            lhs_s, rhs_s = pair
            pair_ids = {lhs_s.identifier, rhs_s.identifier}
            if linked_ids and linked_ids <= pair_ids and all((s.identifier in linked_ids or hasattr(s, 'default_value') for s in pair)):
                if not _operator_dispatch_ok(node, pair, linked_ids, src_types):
                    return None
                return _LiftPlan('binary', binary[operation], pair)
    inputs = list(node.inputs)
    if inputs:
        first_id = inputs[0].identifier
        unary = _LIFT_UNARY.get(node.bl_idname, {})
        if operation in unary and linked_ids == {first_id}:
            if src_types is not None and node.bl_idname in ('FunctionNodeBooleanMath', 'FunctionNodeBitMath') and (not _logic_dispatch_ok(node, inputs[:1], linked_ids, src_types)):
                return None
            return _LiftPlan('unary', unary[operation], (inputs[0],))
        unary_call = _LIFT_UNARY_CALL.get(node.bl_idname, {})
        if operation in unary_call and linked_ids == {first_id}:
            return _LiftPlan('unary_call', unary_call[operation], (inputs[0],))
    return None

def _lift_expr(ctx: EmitContext, node, plan: _LiftPlan) -> Expr:
    operands: list[Expr] = []
    for index, socket in enumerate(plan.sockets):
        link = ctx.input_link(node, socket.identifier)
        if index == 0 and link is not None:
            operand: Expr | None = ctx.socket_expr(link)
        else:
            operand = ctx.input_expr(node, socket)
        if operand is None:
            raise CodegenError(f"Cannot resolve operands for '{node.name}'")
        operands.append(operand)
    if plan.kind == 'binary':
        return BinOp(plan.op, operands[0], operands[1])
    if plan.kind == 'unary':
        return UnaryOp(plan.op, operands[0])
    return Call(plan.op, args=[operands[0]])

def _linked_ids(ctx: EmitContext, node) -> set[str]:
    return {link.to_socket.identifier for link in ctx.incoming.get(node.name, ())}
_CHAIN_SOCKET_TYPES = frozenset({'GEOMETRY', 'SHADER'})

def _chainable_links(ctx: EmitContext) -> dict[str, _Link]:
    socket_out: dict[tuple[str, str], int] = {}
    socket_in: dict[tuple[str, str], int] = {}
    for link in ctx.links:
        out_key = (link.from_node.name, link.from_socket.identifier)
        in_key = (link.to_node.name, link.to_socket.identifier)
        socket_out[out_key] = socket_out.get(out_key, 0) + 1
        socket_in[in_key] = socket_in.get(in_key, 0) + 1
    result: dict[str, _Link] = {}
    for link in ctx.links:
        from_node, to_node = (link.from_node, link.to_node)
        if to_node.bl_idname in _SKIP_BL_IDNAMES:
            continue
        if to_node.bl_idname in _EMITTERS:
            continue
        if link.from_socket.type not in _CHAIN_SOCKET_TYPES:
            continue
        if from_node.bl_idname != 'NodeGroupInput' and (not (from_node.outputs and from_node.outputs[0].identifier == link.from_socket.identifier)):
            continue
        if not (to_node.inputs and to_node.inputs[0].identifier == link.to_socket.identifier):
            continue
        if socket_out[from_node.name, link.from_socket.identifier] != 1:
            continue
        if socket_in[to_node.name, link.to_socket.identifier] != 1:
            continue
        result[to_node.name] = link
    return result

def _gate_short_chains(ctx: EmitContext, chain_in: dict[str, _Link], ordered: list, min_chain_length: int) -> set[str]:
    node_by_name = {n.name: n for n in ordered}
    next_map: dict[str, str] = {}
    head_from_iface: set[str] = set()
    for to_name, link in chain_in.items():
        if link.from_node.bl_idname == 'NodeGroupInput':
            head_from_iface.add(to_name)
        else:
            next_map[link.from_node.name] = to_name
    chained_consumers = set(next_map.values())
    forced: set[str] = set()
    for node in ordered:
        name = node.name
        if name in chained_consumers:
            continue
        if node.bl_idname in _EMITTERS:
            continue
        if _lift_plan(node, _linked_ids(ctx, node), _linked_src_types(ctx, node)) is not None:
            continue
        if node.bl_idname in _SOCKET_METHODS and _match_socket_method(ctx, node):
            continue
        run = [name]
        current = name
        while len(ctx.outgoing.get(current, ())) == 1 and (nxt := next_map.get(current)) and (nxt not in run):
            run.append(nxt)
            current = nxt
        tail_outs = ctx.outgoing.get(run[-1], ())
        tail_to_iface = len(tail_outs) == 1 and tail_outs[0].to_node.bl_idname == 'NodeGroupOutput'
        length = len(run) + (1 if run[0] in head_from_iface else 0) + (1 if tail_to_iface else 0)
        has_chain_syntax = len(run) > 1 or run[0] in head_from_iface or tail_to_iface
        if has_chain_syntax and length < min_chain_length:
            forced.update((n for n in run if node_by_name[n].bl_idname not in _EMITTERS))
    for name in forced:
        chain_in.pop(name, None)
    return forced
_IFACE_PARAM_ATTR = {'expanded': 'menu_expanded', 'default_attribute': 'default_attribute_name'}

def _interface_kwargs(item, method: str) -> dict[str, Any]:
    from ..builder.tree import SocketContext
    fn = getattr(SocketContext, method, None)
    if fn is None:
        return {}
    try:
        sig = _signature(fn)
    except (TypeError, ValueError):
        return {}
    defaults = _get_interface_defaults(item.id_data.bl_idname, item.socket_type)
    kwargs: dict[str, Any] = {}
    for pname, param in sig.parameters.items():
        if param.kind != inspect.Parameter.KEYWORD_ONLY:
            continue
        attr = _IFACE_PARAM_ATTR.get(pname, pname)
        try:
            current = getattr(item, attr)
        except AttributeError:
            if attr != 'optional_label':
                continue
            current = item.get(attr, False)
        if not isinstance(current, str):
            try:
                current = tuple(current)
            except TypeError:
                pass
        if attr in defaults:
            if _eq(current, defaults[attr]):
                continue
        elif param.default is None or _eq(current, param.default):
            continue
        kwargs[pname] = current
    return kwargs

def _emit_interface(item, direction: str, ctx: EmitContext, indent: str='    ') -> str:
    method = _INTERFACE_TYPE_METHOD.get(item.socket_type, 'geometry')
    var_name = _make_var(item.name, ctx.counter)
    if direction == 'inputs':
        used = any((link.from_node.bl_idname == 'NodeGroupInput' and link.from_socket.identifier == item.identifier for link in ctx.links))
    else:
        used = any((link.to_node.bl_idname == 'NodeGroupOutput' and link.to_socket.identifier == item.identifier for link in ctx.links))
    if not used:
        var_name = '_' + var_name
    ctx.var_map[f'_iface_{direction}_{item.identifier}'] = _Val(Ref(var_name), is_socket=True)
    args: list[str] = [_fmt(item.name)]
    emits_default = item.socket_type not in _NO_DEFAULT_VALUE_TYPES or item.socket_type in _DATABLOCK_IFACE_DEFAULT_TYPES
    if emits_default:
        try:
            default = item.default_value
        except (AttributeError, TypeError):
            default = None
        if direction == 'outputs' and default is not None:
            from ..builder.tree import SocketContext
            fresh = _get_interface_defaults(item.id_data.bl_idname, item.socket_type)
            param = _signature(getattr(SocketContext, method)).parameters.get('default_value')
            factory_default = None if param is None else param.default
            if 'default_value' in fresh and _eq(default, fresh['default_value']) and (factory_default is None or _eq(default, factory_default)):
                default = None
        if item.socket_type == 'NodeSocketMenu' and (not default):
            default = None
        if default is not None:
            args.append(_fmt(default))
    description = getattr(item, 'description', '')
    if description:
        args.append(f'description={_fmt(description)}')
    args.extend((f'{pname}={_fmt(value)}' for pname, value in _interface_kwargs(item, method).items()))
    return f"{indent}{var_name} = tree.{direction}.{method}({', '.join(args)})"

def _panel_directions(panel) -> set[str]:
    directions: set[str] = set()
    for child in panel.interface_items:
        if getattr(child, 'item_type', '') == 'SOCKET':
            directions.add(child.in_out)
        elif getattr(child, 'item_type', '') == 'PANEL':
            directions |= _panel_directions(child)
    return directions

def _panel_chain(item) -> list:
    chain = []
    parent = item.parent
    while parent is not None and parent.index != -1:
        chain.append(parent)
        parent = parent.parent
    chain.reverse()
    return chain

def _emit_interface_lines(node_tree, ctx: EmitContext) -> list[str]:
    lines: list[str] = []

    def _sibling_key(panel) -> tuple[str, int]:
        parent = panel.parent
        parent_ix = -1 if parent is None else parent.index
        return (panel.name, parent_ix)
    duplicate_keys = {key for key, count in Counter((_sibling_key(item) for item in node_tree.interface.items_tree if getattr(item, 'item_type', '') == 'PANEL')).items() if count > 1}
    handles: dict[int, str] = {}
    opened: set[int] = set()

    def _panel_open_args(panel) -> list[str]:
        panel_args = [_fmt(panel.name)]
        if panel.description:
            panel_args.append(f'description={_fmt(panel.description)}')
        if panel.default_closed:
            panel_args.append('default_closed=True')
        return panel_args
    for direction, in_out in (('inputs', 'INPUT'), ('outputs', 'OUTPUT')):
        open_stack: list[int] = []
        for item in node_tree.interface.items_tree:
            if getattr(item, 'item_type', '') != 'SOCKET' or item.in_out != in_out:
                continue
            chain = _panel_chain(item)
            keep = 0
            while keep < min(len(open_stack), len(chain)) and open_stack[keep] == chain[keep].index:
                keep += 1
            del open_stack[keep:]
            for panel in chain[keep:]:
                indent = '    ' * (1 + len(open_stack))
                if panel.index in handles:
                    lines.append(f'{indent}with tree.panel({handles[panel.index]}):')
                    open_stack.append(panel.index)
                    continue
                panel_args = _panel_open_args(panel)
                mixed = len(_panel_directions(panel)) > 1
                ambiguous = _sibling_key(panel) in duplicate_keys
                suffix = ''
                if mixed and ambiguous:
                    panel_args.append('reuse=False')
                    var = f'_panel_{panel.index}'
                    handles[panel.index] = var
                    suffix = f' as {var}'
                target = 'tree' if mixed else f'tree.{direction}'
                lines.append(f"{indent}with {target}.panel({', '.join(panel_args)}){suffix}:")
                open_stack.append(panel.index)
                opened.add(panel.index)
            lines.append(_emit_interface(item, direction, ctx, indent='    ' * (1 + len(open_stack))))
    for panel in node_tree.interface.items_tree:
        if getattr(panel, 'item_type', '') != 'PANEL' or panel.index in opened:
            continue
        depth = 1
        for ancestor in _panel_chain(panel):
            indent = '    ' * depth
            if ancestor.index in handles:
                lines.append(f'{indent}with tree.panel({handles[ancestor.index]}):')
            else:
                lines.append(f'{indent}with tree.panel({_fmt(ancestor.name)}):')
            depth += 1
        args = [*_panel_open_args(panel), 'reuse=False']
        lines.append(f"{'    ' * depth}with tree.panel({', '.join(args)}):")
        lines.append(f"{'    ' * (depth + 1)}pass")
        opened.add(panel.index)
    return lines

def _format_with_ruff(code: str) -> str:
    try:
        from ruff import find_ruff_bin
    except ImportError:
        return code
    import subprocess
    ruff = find_ruff_bin()
    for command in (['check', '--fix-only', '-'], ['format', '-']):
        try:
            result = subprocess.run([ruff, *command], input=code, capture_output=True, encoding='utf-8', check=True)
        except (OSError, subprocess.SubprocessError):
            return code
        code = result.stdout or code
    return code

def to_python(tree: NodeTree | TreeBuilder[Any], min_chain_length: int=3, strict: bool=True, max_inline_width: int | None=88, top_level: Literal['with', 'class']='with', format: bool=True, nodebpy_pkg: str='omoonodes', group_class_names: Mapping[str, str] | None=None, external_groups: Collection[str] | None=None, typed_groups: Collection[str] | None=None, root_interface: GroupInterface | None=None, in_place: bool=False) -> str:
    node_tree: NodeTree = tree.tree if hasattr(tree, 'tree') else tree
    class_names = dict(group_class_names or {})
    externals = set(external_groups or ())
    if (missing := (externals - class_names.keys())):
        raise ValueError(f'external_groups without a group_class_names entry: {sorted(missing)}')
    collector = _GroupCollector(min_chain_length=min_chain_length, strict=strict, max_inline_width=max_inline_width, group_class_names=class_names, external_groups=externals, typed_groups=set(typed_groups or ()), root_interface=root_interface, root_tree_name=node_tree.name if root_interface is not None else None, used_names=set(class_names.values()))
    emission: _TreeEmission | None = None
    if top_level == 'class':
        collector.register(node_tree)
        used_aliases = collector.used_aliases
    else:
        emission = _emit_tree(node_tree, collector)
        used_aliases = emission.used_aliases | collector.used_aliases
    import_parts = [f'{_ALIAS_MODULES[alias]} as {alias}' for alias in ('g', 's', 'c') if alias in used_aliases]
    import_names = import_parts + ['TreeBuilder']
    lines: list[str] = []
    if collector.tree_param_types:
        lines.append('from bpy.types import ' + ', '.join(sorted(collector.tree_param_types)))
    if import_names:
        lines.append(f'from {nodebpy_pkg} import ' + ', '.join(import_names))
    if collector.bases_used:
        lines.append(f'from {nodebpy_pkg}.builder import ' + ', '.join(sorted(collector.bases_used)))
    for class_def in collector.class_defs:
        lines.extend(['', '', class_def])
    if top_level == 'with':
        assert emission is not None
        lines.append('')
        if collector.class_defs:
            lines.append('')
        constructor = _TREE_CONSTRUCTORS.get(node_tree.bl_idname, 'TreeBuilder')
        ctor_args = [_fmt(node_tree.name)]
        if in_place:
            ctor_args.append('clear=True')
        tree_props = _tree_prop_overrides(node_tree)
        for flag in ('is_modifier', 'is_tool'):
            if tree_props.get(flag):
                ctor_args.append(f'{flag}=True')
        lines.append(f"with {constructor}({', '.join(ctor_args)}) as tree:")
        lines.extend(_assemble_tree_body(emission))
    if any((re.search('\\bmath\\.(pi|tau|e)\\b', line) for line in lines)):
        lines.insert(0, 'import math')
    if any(('bpy.data.' in line for line in lines)):
        lines.insert(0, 'import bpy')
    code = '\n'.join(lines)
    return _format_with_ruff(code) if format else code

def _assemble_tree_body(emission: _TreeEmission) -> list[str]:
    iface_lines, body, out_lines = (emission.iface_lines, emission.body_lines, emission.out_lines)
    lines = list(iface_lines)
    if iface_lines and (body or out_lines):
        lines.append('')
    lines.extend(body)
    if out_lines:
        if body:
            lines.append('')
        lines.extend(out_lines)
    if not (iface_lines or body or out_lines):
        lines.append('    pass')
    return lines

@dataclass
class _TreeEmission:
    iface_lines: list[str]
    body_lines: list[str]
    out_lines: list[str]
    used_aliases: set[str]

@dataclass
class GroupInterface:
    docstring: str
    body: str
    base: str | None = None
    attr_lines: list[str] = field(default_factory=list)
_GROUP_BASES = {'GeometryNodeGroup': 'CustomGeometryGroup', 'ShaderNodeGroup': 'CustomShaderGroup', 'CompositorNodeGroup': 'CustomCompositorGroup'}
_GROUP_BASE_FOR_TREE = {'GeometryNodeTree': 'CustomGeometryGroup', 'ShaderNodeTree': 'CustomShaderGroup', 'CompositorNodeTree': 'CustomCompositorGroup'}

@dataclass
class _GroupCollector:
    min_chain_length: int
    strict: bool
    max_inline_width: int | None
    group_class_names: dict[str, str] = field(default_factory=dict)
    external_groups: set[str] = field(default_factory=set)
    typed_groups: set[str] = field(default_factory=set)
    root_interface: GroupInterface | None = None
    root_tree_name: str | None = None
    class_defs: list[str] = field(default_factory=list)
    names_by_tree: dict[str, str] = field(default_factory=dict)
    used_names: set[str] = field(default_factory=set)
    bases_used: set[str] = field(default_factory=set)
    used_aliases: set[str] = field(default_factory=set)
    tree_param_types: set[str] = field(default_factory=set)

    def register(self, node_tree: NodeTree) -> str:
        existing = self.names_by_tree.get(node_tree.name)
        if existing is not None:
            return existing
        if node_tree.name in self.external_groups:
            class_name = self.group_class_names[node_tree.name]
            self.names_by_tree[node_tree.name] = class_name
            return class_name
        class_name = self._unique_name(node_tree.name)
        self.names_by_tree[node_tree.name] = class_name
        emission = _emit_tree(node_tree, self)
        self.used_aliases |= emission.used_aliases
        base = _GROUP_BASE_FOR_TREE.get(node_tree.bl_idname, 'CustomGeometryGroup')
        interface = self.root_interface if node_tree.name == self.root_tree_name else None
        if interface is not None and interface.base:
            base = interface.base
        self.bases_used.add(base)
        if node_tree.bl_idname in _GROUP_BASE_FOR_TREE:
            self.tree_param_types.add(node_tree.bl_idname)
        self.class_defs.append(_render_group_class(class_name, node_tree, base, emission, interface))
        return class_name

    def _unique_name(self, tree_name: str) -> str:
        assigned = self.group_class_names.get(tree_name)
        if assigned is not None:
            self.used_names.add(assigned)
            return assigned
        base = _class_name(tree_name)
        name, n = (base, 1)
        while name in self.used_names:
            n += 1
            name = f'{base}{n}'
        self.used_names.add(name)
        return name

def _class_name(name: str) -> str:
    cleaned = ''.join((p[:1].upper() + p[1:] for p in re.split('\\W+', name) if p))
    if not cleaned or cleaned[0].isdigit():
        cleaned = f'Group{cleaned}'
    if keyword.iskeyword(cleaned):
        cleaned += '_'
    return cleaned
_TREE_PROP_CANDIDATES = ('description', 'default_group_node_width', 'node_tool_idname', 'show_modifier_manage_panel', 'is_modifier', 'is_strip_modifier', 'is_tool', 'is_mode_object', 'is_mode_edit', 'is_mode_sculpt', 'is_mode_paint', 'use_wait_for_click', 'is_type_mesh', 'is_type_curve', 'is_type_pointcloud', 'is_type_grease_pencil', 'allow_usage_in_scene_compositor_effect')
_TREE_PROP_DEFAULTS: dict[str, dict[str, Any]] = {}

def _tree_prop_overrides(node_tree) -> dict[str, Any]:
    tree_idname = node_tree.bl_idname
    if tree_idname not in _TREE_PROP_DEFAULTS:

        def collect(probe) -> dict[str, Any]:
            return {name: getattr(probe, name) for name in _TREE_PROP_CANDIDATES if hasattr(probe, name)}
        _TREE_PROP_DEFAULTS[tree_idname] = _with_probe_tree(tree_idname, collect, {})
    return {name: value for name, default in _TREE_PROP_DEFAULTS[tree_idname].items() if (value := getattr(node_tree, name)) != default}

def _node_prop_lines(node) -> list[str]:
    lines: list[str] = []
    for prop in node.bl_rna.properties:
        if prop.type == 'POINTER' and prop.identifier not in {'rna_type', 'id_data', 'parent', 'node_tree'}:
            value = getattr(node, prop.identifier)
            if value is not None and hasattr(value, 'id_type'):
                lines.append(f'{prop.identifier} = {_fmt(value)}')
    if node.label:
        lines.append(f'label = {_fmt(node.label)}')
    if getattr(node, 'mute', False):
        lines.append('mute = True')
    if getattr(node, 'warning_propagation', 'ALL') != 'ALL':
        lines.append(f'warning_propagation = {_fmt(node.warning_propagation)}')
    return lines
_MAPPING_ATTRS = ('extend', 'tone', 'use_clip', 'clip_min_x', 'clip_min_y', 'clip_max_x', 'clip_max_y', 'black_level', 'white_level')

def _mapping_attr_value(mapping, name):
    value = getattr(mapping, name)
    if isinstance(value, (str, bool, int, float)):
        return value
    return tuple(value)

def _mapping_state(mapping) -> tuple:
    attrs = tuple(((name, _norm_floats(_mapping_attr_value(mapping, name))) for name in _MAPPING_ATTRS if hasattr(mapping, name)))
    curves = tuple((tuple(((_norm_floats(tuple(point.location)), point.handle_type, bool(point.select)) for point in curve.points)) for curve in mapping.curves))
    return (attrs, curves)

def _norm_floats(value):
    if isinstance(value, float):
        return round(value, 5)
    if isinstance(value, tuple):
        return tuple((_norm_floats(v) for v in value))
    return value
_FRESH_MAPPING_CACHE: dict[tuple[str, str], tuple | None] = {}
_MAPPING_POINTS_AS_ITEMS = {'ShaderNodeFloatCurve'}

def _fresh_mapping_state(tree_idname: str, bl_idname: str) -> tuple | None:
    key = (tree_idname, bl_idname)
    if key not in _FRESH_MAPPING_CACHE:

        def probe(tree):
            node = tree.nodes.new(bl_idname)
            mapping = getattr(node, 'mapping', None)
            if mapping is None or not hasattr(mapping, 'curves'):
                return None
            return _mapping_state(mapping)
        _FRESH_MAPPING_CACHE[key] = _with_probe_tree(tree_idname, probe, None)
    return _FRESH_MAPPING_CACHE[key]

def _has_custom_mapping(node, tree_idname: str) -> bool:
    mapping = getattr(node, 'mapping', None)
    if mapping is None or not hasattr(mapping, 'curves'):
        return False
    state = _mapping_state(mapping)
    fresh = _fresh_mapping_state(tree_idname, node.bl_idname)
    if node.bl_idname in _MAPPING_POINTS_AS_ITEMS:
        selected = any((select for curve in state[1] for _, _, select in curve))
        return fresh is None or state[0] != fresh[0] or selected
    return state != fresh

def _node_mapping_lines(node, tree_idname: str, accessor: str, counter: dict[str, int]) -> list[str]:
    mapping = node.mapping
    fresh = _fresh_mapping_state(tree_idname, node.bl_idname)
    fresh_attrs = dict(fresh[0]) if fresh is not None else {}
    map_ref = f'{accessor}.mapping'
    lines: list[str] = []
    for name in _MAPPING_ATTRS:
        if not hasattr(mapping, name):
            continue
        value = _mapping_attr_value(mapping, name)
        if fresh is None or fresh_attrs.get(name) != _norm_floats(value):
            lines.append(f'{map_ref}.{name} = {_fmt(value)}')
    fresh_curves = fresh[1] if fresh is not None else None
    state_curves = _mapping_state(mapping)[1]
    curves = () if node.bl_idname in _MAPPING_POINTS_AS_ITEMS else mapping.curves
    for index, curve in enumerate(curves):
        if fresh_curves is not None and index < len(fresh_curves) and (state_curves[index] == fresh_curves[index]):
            continue
        var = _make_var('curve', counter)
        lines.append(f'{var} = {map_ref}.curves[{index}]')
        fresh_count = len(fresh_curves[index]) if fresh_curves is not None and index < len(fresh_curves) else 2
        for extra in range(len(curve.points) - fresh_count):
            lines.append(f'{var}.points.new({1000000.0 + extra}, 0.0)')
        for _ in range(fresh_count - len(curve.points)):
            lines.append(f'{var}.points.remove({var}.points[-1])')
        for j, point in enumerate(curve.points):
            lines.append(f'{var}.points[{j}].location = {_fmt(tuple(point.location))}')
            if point.handle_type != 'AUTO':
                lines.append(f'{var}.points[{j}].handle_type = {_fmt(point.handle_type)}')
            lines.append(f'{var}.points[{j}].select = {point.select}')
    lines.append(f'{map_ref}.update()')
    if node.bl_idname in _MAPPING_POINTS_AS_ITEMS:
        for index, curve in enumerate(mapping.curves):
            for j, point in enumerate(curve.points):
                if point.select:
                    lines.append(f'{map_ref}.curves[{index}].points[{j}].select = True')
    return lines

def _render_group_class(class_name: str, node_tree, base: str, emission: _TreeEmission, interface: GroupInterface | None=None) -> str:
    header = [f'class {class_name}({base}):']
    if interface is not None:
        header.extend([interface.docstring, ''])
    header.append(f'    _name = {_fmt(node_tree.name)}')
    if interface is not None:
        header.extend((f'    {line}' for line in interface.attr_lines))
    color = getattr(node_tree, 'color_tag', 'NONE')
    if color and color != 'NONE':
        header.append(f'    _color_tag = {_fmt(color)}')
    tree_props = _tree_prop_overrides(node_tree)
    if tree_props:
        rendered = ', '.join((f'{_fmt(key)}: {_fmt(value)}' for key, value in tree_props.items()))
        header.append(f'    _tree_properties = {{{rendered}}}')
    if interface is not None:
        header.extend(['', interface.body])
    annotation = f'TreeBuilder[{node_tree.bl_idname}]' if node_tree.bl_idname in _GROUP_BASE_FOR_TREE else 'TreeBuilder'
    header.extend(['', f'    def _build_group(self, tree: {annotation}) -> None:'])
    inner = _assemble_tree_body(emission)
    body = ['    ' + line if line else '' for line in inner]
    return '\n'.join(header + body)

def _emit_tree(node_tree, collector: _GroupCollector) -> _TreeEmission:
    links = _effective_links(node_tree)
    incoming: dict[str, list[_Link]] = {}
    outgoing: dict[str, list[_Link]] = {}
    for link in links:
        incoming.setdefault(link.to_node.name, []).append(link)
        outgoing.setdefault(link.from_node.name, []).append(link)
    ctx = EmitContext(node_tree, links, incoming, outgoing, collector=collector)
    skip = _SKIP_BL_IDNAMES
    ordered = [n for n in _topo_sort(node_tree) if n.bl_idname not in skip]
    ordered, frame_path_of, frame_nodes = _frame_order(node_tree, ordered)
    iface_lines = _emit_interface_lines(node_tree, ctx)
    chain_in = _chainable_links(ctx)
    gated_nodes = _gate_short_chains(ctx, chain_in, ordered, collector.min_chain_length)
    tagged_body: list[tuple[tuple[str, ...], str]] = []
    consumed_out_links: set[int] = set()
    for node in ordered:
        name = node.name
        frame = frame_path_of.get(name, ())
        val: _Val | None = None
        emitter = _EMITTERS.get(node.bl_idname)
        if emitter is not None:
            emitted = emitter(node, ctx)
            if emitted is not None:
                val = emitted if isinstance(emitted, _Val) else _Val(emitted)
        if val is None:
            val = _socket_method_val(ctx, node)
        if val is None:
            plan = _lift_plan(node, _linked_ids(ctx, node), _linked_src_types(ctx, node))
            if plan is not None:
                val = _Val(_lift_expr(ctx, node, plan), is_socket=True, socket_id=node.outputs[0].identifier if node.outputs else None)
        if val is None:
            if _find_cls(node.bl_idname) is None:
                message = f"unsupported node '{name}' ({node.bl_idname})"
                if collector.strict:
                    raise CodegenError(f'Cannot generate code: {message}. Register an emitter with register_emitter() or pass strict=False.')
                var = _make_var(_node_var_label(node), ctx.counter)
                if not ctx.outgoing.get(name):
                    var = '_' + var
                ctx.var_map[name] = _Val(Ref(var))
                tagged_body.append((frame, f'    {var} = None  # TODO: {message}'))
                continue
            chain_link = chain_in.get(name)
            call = ctx.constructor(node, skip_input_id=chain_link.to_socket.identifier if chain_link else None)
            expr: Expr = BinOp('>>', ctx.upstream_expr(chain_link, pipeline=True), call) if chain_link else call
            val = _Val(expr)
        if ctx.pending_lines:
            tagged_body.extend(((frame, line) for line in ctx.pending_lines))
            ctx.pending_lines.clear()
        if val.outputs is not None:
            ctx.var_map[name] = val
            continue
        out_links = ctx.outgoing.get(name, ())
        group_outs = [link for link in out_links if link.to_node.bl_idname == 'NodeGroupOutput']
        node_prop_lines = _node_prop_lines(node)
        custom_mapping = _has_custom_mapping(node, node_tree.bl_idname)
        if not node_prop_lines and (not custom_mapping) and (len(out_links) == 1) and (not group_outs) and (frame == frame_path_of.get(out_links[0].to_node.name, ())) and (collector.max_inline_width is None or chain_in.get(out_links[0].to_node.name) is out_links[0] or len(val.require_expr().render()) <= collector.max_inline_width):
            ctx.var_map[name] = val
            continue
        if not node_prop_lines and (not custom_mapping) and (len(out_links) == 1) and group_outs and (name not in gated_nodes):
            link = group_outs[0]
            out_ref = ctx.var_map.get(f'_iface_outputs_{link.to_socket.identifier}')
            if out_ref is None:
                raise CodegenError(f"Group output socket '{link.to_socket.name}' has no interface variable")
            source = _output_expr(val, node, link.from_socket, pipeline=True)
            chain = BinOp('>>', source, out_ref.require_expr())
            width = _MAX_LINE_WIDTH - 4 * len(frame)
            tagged_body.extend(((frame, line) for line in _stmt_lines(chain, width=width)))
            consumed_out_links.add(id(link))
            continue
        var = _make_var(_node_var_label(node), ctx.counter)
        if not out_links and (not node_prop_lines) and (not custom_mapping):
            var = '_' + var
        width = _MAX_LINE_WIDTH - 4 * len(frame)
        tagged_body.extend(((frame, line) for line in _stmt_lines(val.require_expr(), assign=var, width=width)))
        for prop_line in node_prop_lines:
            tagged_body.append((frame, f'    {var}.node.{prop_line}'))
        if custom_mapping:
            tagged_body.extend(((frame, f'    {line}') for line in _node_mapping_lines(node, node_tree.bl_idname, f'{var}.node', ctx.counter)))
        ctx.var_map[name] = _Val(Ref(var), is_socket=val.is_socket, socket_id=val.socket_id)
    frame_alias = _TREE_ALIAS.get(node_tree.bl_idname, 'g')
    body: list[str] = []
    open_path: tuple[str, ...] = ()
    for path, line in tagged_body:
        common = 0
        while common < len(open_path) and common < len(path) and (open_path[common] == path[common]):
            common += 1
        for depth in range(common, len(path)):
            ctx.used_aliases.add(frame_alias)
            frame_node = frame_nodes[path[depth]]
            label = _fmt(frame_node.label) if frame_node.label else ''
            body.append(f"{'    ' * (depth + 1)}with {frame_alias}.Frame({label}):")
        open_path = path
        body.append('    ' * len(path) + line)
    out_lines: list[str] = []
    for link in links:
        if link.to_node.bl_idname != 'NodeGroupOutput':
            continue
        if id(link) in consumed_out_links:
            continue
        out_ref = ctx.var_map.get(f'_iface_outputs_{link.to_socket.identifier}')
        if out_ref is None:
            raise CodegenError(f"Group output socket '{link.to_socket.name}' has no interface variable")
        source = ctx.upstream_expr(link, pipeline=True)
        out_lines.extend(_stmt_lines(BinOp('>>', source, out_ref.require_expr())))
    return _TreeEmission(iface_lines, body, out_lines, ctx.used_aliases)

@register_emitter('ShaderNodeValue')
def _emit_value(node, ctx: EmitContext) -> Call:
    call = ctx.constructor(node)
    if node.outputs:
        value = node.outputs[0].default_value
        if not _eq(value, 0.0):
            call.args.append(Lit(value))
    return call
_COMPARE_LIFT = {'LESS_THAN': '<', 'GREATER_THAN': '>', 'LESS_EQUAL': '<=', 'GREATER_EQUAL': '>=', 'EQUAL': '==', 'NOT_EQUAL': '!='}
_COMPARE_DISPATCH = {'VALUE': 'FLOAT', 'INT': 'INT', 'VECTOR': 'VECTOR'}
_OPERATOR_EPSILON = 9.999999747378752e-05

def _lift_compare(node: FunctionNodeCompare, ctx: EmitContext) -> _Val | None:
    op = _COMPARE_LIFT.get(node.operation)
    in_a = _input_socket_by_identifier(node, 'A')
    in_b = _input_socket_by_identifier(node, 'B')
    if (in_a.links and in_b.links) and in_a.links[0].from_socket.type != in_b.links[0].from_socket.type:
        return None
    if op is None or node.mode != 'ELEMENT':
        return None
    linked = _linked_ids(ctx, node)
    if 'A' not in linked or not linked <= {'A', 'B'}:
        return None
    a_link = ctx.input_link(node, 'A')
    assert a_link is not None
    if _COMPARE_DISPATCH.get(a_link.from_socket.type) != node.data_type:
        return None
    if node.operation in ('EQUAL', 'NOT_EQUAL'):
        epsilon = _input_socket_by_identifier(node, 'Epsilon')
        if epsilon is None or not _eq(epsilon.default_value, _OPERATOR_EPSILON):
            return None
    b_link = ctx.input_link(node, 'B')
    if b_link is not None:
        rhs: Expr = ctx.upstream_expr(b_link)
    else:
        b_socket = _input_socket_by_identifier(node, 'B')
        if b_socket is None:
            return None
        rhs = Lit(b_socket.default_value)
    return _Val(CompareOp(op, ctx.upstream_expr(a_link), rhs), is_socket=True, socket_id=node.outputs[0].identifier)

@register_emitter('FunctionNodeCompare')
def _emit_compare(node, ctx: EmitContext) -> Expr | _Val | None:
    lifted = _lift_compare(node, ctx)
    if lifted is not None:
        return lifted
    call = ctx.constructor(node)
    if node.data_type == 'VECTOR':
        call.kwargs['mode'] = Lit(node.mode)
    return call

@register_emitter('FunctionNodeFormatString')
def _emit_format_string(node, ctx: EmitContext) -> Expr | _Val | None:
    items: dict[str, Expr] = {}
    for socket in node.inputs:
        if socket.identifier == 'Format' or socket.identifier.startswith('__extend__'):
            continue
        link = ctx.input_link(node, socket.identifier)
        items[socket.name] = ctx.upstream_expr(link) if link is not None else Lit(socket.default_value)
    format_link = ctx.input_link(node, 'Format')
    if format_link is not None:
        return _Val(MethodCall(ctx.socket_expr(format_link), 'format', [DictExpr(items)]), is_socket=True, socket_id=node.outputs[0].identifier)
    format_socket = _input_socket_by_identifier(node, 'Format')
    args: list[Expr] = [Lit(format_socket.default_value if format_socket is not None else '')]
    kwargs: dict[str, Expr] = {'items': DictExpr(items)} if items else {}
    ctx.used_aliases.add('g')
    return Call('g.FormatString', args, kwargs)

@register_emitter('GeometryNodeStringJoin')
def _emit_join_strings(node, ctx: EmitContext) -> Expr | _Val | None:
    entries = [(link.sort_id, ctx.upstream_expr(link)) for link in ctx.incoming.get(node.name, ()) if link.to_socket.identifier == 'Strings']
    entries.sort(key=lambda e: e[0], reverse=True)
    strings = TupleExpr([e[1] for e in entries])
    delimiter_link = ctx.input_link(node, 'Delimiter')
    if delimiter_link is not None:
        return _Val(MethodCall(ctx.socket_expr(delimiter_link), 'join', [strings]), is_socket=True, socket_id=node.outputs[0].identifier)
    ctx.used_aliases.add('g')
    kwargs: dict[str, Expr] = {}
    delimiter = _input_socket_by_identifier(node, 'Delimiter')
    if delimiter is not None and delimiter.default_value:
        kwargs['delimiter'] = Lit(delimiter.default_value)
    return Call('g.JoinStrings', [strings], kwargs)

@register_emitter('GeometryNodeGeometryToInstance')
def _emit_geometry_to_instance(node, ctx: EmitContext) -> Expr | _Val | None:
    entries = [(link.sort_id, ctx.upstream_expr(link)) for link in ctx.incoming.get(node.name, ()) if link.to_socket.identifier == 'Geometry']
    entries.sort(key=lambda e: e[0], reverse=True)
    ctx.used_aliases.add('g')
    return Call('g.GeometryToInstance', args=[expr for _, expr in entries])

@register_emitter('GeometryNodeListGetItem')
def _emit_list_get_item(node, ctx: EmitContext) -> _Val | None:
    list_link = ctx.input_link(node, 'List')
    if list_link is None or not _list_receiver_ok(node, list_link, 'socket_type'):
        return None
    found = _find_cls(node.bl_idname)
    if found is not None and set(_non_default_props(node, found[1])) - {'socket_type'}:
        return None
    receiver = ctx.socket_expr(list_link)
    index_link = ctx.input_link(node, 'Index')
    if index_link is not None:
        index: Expr = ctx.upstream_expr(index_link)
    else:
        socket = _input_socket_by_identifier(node, 'Index')
        index = Lit(socket.default_value if socket is not None else 0)
    return _Val(Subscript(receiver, index), is_socket=True, socket_id='Value')
_SWITCH_FACTORY_NAMES = {'FLOAT': 'float', 'INT': 'integer', 'BOOLEAN': 'boolean', 'VECTOR': 'vector', 'RGBA': 'color', 'ROTATION': 'rotation', 'MATRIX': 'matrix', 'STRING': 'string', 'MENU': 'menu', 'OBJECT': 'object', 'GEOMETRY': 'geometry', 'COLLECTION': 'collection', 'IMAGE': 'image', 'MATERIAL': 'material', 'BUNDLE': 'bundle', 'CLOSURE': 'closure', 'SHADER': 'shader', 'FONT': 'font', 'SOUND': 'sound'}

def _switch_item_exprs(node, ctx: EmitContext, skip_id: str) -> list[tuple[str, Expr]]:
    out: list[tuple[str, Expr]] = []
    for socket in node.inputs:
        if socket.identifier == skip_id or socket.identifier.startswith('__extend__'):
            continue
        link = ctx.input_link(node, socket.identifier)
        if link is not None:
            expr: Expr = ctx.upstream_expr(link)
        elif hasattr(socket, 'default_value'):
            expr = Lit(socket.default_value)
        else:
            expr = Lit(None)
        out.append((socket.name, expr))
    return out

@register_emitter('GeometryNodeMenuSwitch')
def _emit_menu_switch(node, ctx: EmitContext) -> Expr | _Val | None:
    factory = _SWITCH_FACTORY_NAMES.get(node.data_type)
    if factory is None:
        return None
    alias = _TREE_ALIAS.get(ctx.node_tree.bl_idname, 'g')
    ctx.used_aliases.add(alias)
    item_exprs: dict[str, Expr] = {}
    for (name, expr), item in zip(_switch_item_exprs(node, ctx, 'Menu'), node.enum_items):
        if item.description:
            expr = TupleExpr([expr, Lit(item.description)])
        item_exprs[name] = expr
    items = DictExpr(item_exprs)
    menu_link = ctx.input_link(node, 'Menu')
    if menu_link is not None:
        return Call(f'{alias}.MenuSwitch.{factory}', [ctx.upstream_expr(menu_link), items])
    menu_socket = _input_socket_by_identifier(node, 'Menu')
    first_name = node.enum_items[0].name if node.enum_items else ''
    if menu_socket is not None and menu_socket.default_value != first_name:
        return Call(f'{alias}.MenuSwitch.{factory}', [Lit(menu_socket.default_value), items])
    return Call(f'{alias}.MenuSwitch.{factory}', kwargs={'items': items})

@register_emitter('GeometryNodeIndexSwitch')
def _emit_index_switch(node, ctx: EmitContext) -> Expr | _Val | None:
    factory = _SWITCH_FACTORY_NAMES.get(node.data_type)
    if factory is None:
        return None
    ctx.used_aliases.add('g')
    items = TupleExpr([expr for _, expr in _switch_item_exprs(node, ctx, 'Index')])
    index_link = ctx.input_link(node, 'Index')
    if index_link is not None:
        return Call(f'g.IndexSwitch.{factory}', [ctx.upstream_expr(index_link), items])
    index_socket = _input_socket_by_identifier(node, 'Index')
    if index_socket is not None and index_socket.default_value:
        return Call(f'g.IndexSwitch.{factory}', [Lit(index_socket.default_value), items])
    return Call(f'g.IndexSwitch.{factory}', kwargs={'items': items})
_UNSET = object()

@dataclass(frozen=True)
class _ItemsNodeSpec:
    collection: str
    fixed: tuple[tuple[str, str], ...] = ()
    factory_prop: str | None = None
    factory_map: dict[str, str] | None = None
_ITEMS_NODE_SPECS = {'GeometryNodeFieldToList': _ItemsNodeSpec(collection='list_items', fixed=(('Count', 'count'),))}
_CAPTURE_ITEM_METHOD = {'FLOAT': 'float', 'INT': 'integer', 'BOOLEAN': 'boolean', 'FLOAT_VECTOR': 'vector', 'FLOAT_COLOR': 'color', 'QUATERNION': 'rotation', 'FLOAT4X4': 'matrix'}

@dataclass(frozen=True)
class _TypedItemsNodeSpec(_ItemsNodeSpec):
    label: str = 'node'
    method_map: dict[str, str] | None = None
    fixed_outputs: tuple[tuple[str, str], ...] = ()
_TYPED_ITEMS_NODE_SPECS = {'GeometryNodeCaptureAttribute': _TypedItemsNodeSpec(label='capture', collection='capture_items', fixed=(('Geometry', 'geometry'), ('Selection', 'selection')), factory_prop='domain', factory_map={'POINT': 'point', 'EDGE': 'edge', 'FACE': 'face', 'CORNER': 'corner', 'CURVE': 'curve', 'INSTANCE': 'instance', 'LAYER': 'layer'}, method_map=_CAPTURE_ITEM_METHOD, fixed_outputs=(('Geometry', 'o.geometry'), ('Selection', 'o.selection'))), 'GeometryNodeBake': _TypedItemsNodeSpec(label='bake', collection='bake_items'), 'GeometryNodeFieldToGrid': _TypedItemsNodeSpec(label='field_to_grid', collection='grid_items', fixed=(('Topology', 'topology'),), factory_prop='data_type', factory_map={'FLOAT': 'float', 'INT': 'integer', 'VECTOR': 'vector', 'BOOLEAN': 'boolean'})}

def _items_fixed_kwargs(node, ctx: EmitContext, spec: _ItemsNodeSpec, fixed_inputs) -> dict[str, Expr] | None:
    fixed_ids = {ident for ident, _ in spec.fixed}
    for socket in fixed_inputs:
        if socket.identifier not in fixed_ids and ctx.input_link(node, socket.identifier):
            return None
    fresh_defaults = _get_blender_socket_defaults(node.id_data.bl_idname, node.bl_idname)
    kwargs: dict[str, Expr] = {}
    for ident, param in spec.fixed:
        link = ctx.input_link(node, ident)
        if link is not None:
            kwargs[param] = ctx.upstream_expr(link)
            continue
        socket = _input_socket_by_identifier(node, ident)
        if socket is None or not hasattr(socket, 'default_value'):
            continue
        fresh = fresh_defaults.get(ident, _UNSET)
        if fresh is _UNSET or not _eq(socket.default_value, fresh):
            kwargs[param] = Lit(socket.default_value)
    return kwargs

def _items_node_ctor(alias: str, cls, spec: _ItemsNodeSpec, node, kwargs: dict[str, Expr]) -> Call:
    if spec.factory_prop is not None:
        prop_value = getattr(node, spec.factory_prop)
        method = (spec.factory_map or {}).get(prop_value)
        if method is not None:
            return Call(f'{alias}.{cls.__name__}.{method}', kwargs=kwargs)
        kwargs[spec.factory_prop] = Lit(prop_value)
    return Call(f'{alias}.{cls.__name__}', kwargs=kwargs)

def _emit_items_node(node, ctx: EmitContext) -> Expr | _Val | None:
    spec = _ITEMS_NODE_SPECS.get(node.bl_idname)
    found = _find_cls(node.bl_idname)
    if spec is None or found is None:
        return None
    alias, cls = found
    n_items = len(getattr(node, spec.collection))
    in_sockets = [s for s in node.inputs if not s.identifier.startswith('__extend__')]
    split = len(in_sockets) - n_items
    fixed_inputs, item_inputs = (in_sockets[:split], in_sockets[split:])
    kwargs = _items_fixed_kwargs(node, ctx, spec, fixed_inputs)
    if kwargs is None:
        return None
    items: dict[str, Expr] = {}
    for socket, item in zip(item_inputs, getattr(node, spec.collection)):
        link = ctx.input_link(node, socket.identifier)
        if link is not None:
            items[socket.name] = ctx.upstream_expr(link)
        elif hasattr(socket, 'default_value'):
            items[socket.name] = Lit(socket.default_value)
        else:
            items[socket.name] = Lit(getattr(item, 'socket_type', None) or getattr(item, 'data_type', ''))
    kwargs['items'] = DictExpr(items)
    ctx.used_aliases.add(alias)
    return _items_node_ctor(alias, cls, spec, node, kwargs)
for _items_bl_idname in _ITEMS_NODE_SPECS:
    register_emitter(_items_bl_idname)(_emit_items_node)

def _emit_typed_items_node(node, ctx: EmitContext) -> Expr | _Val | None:
    spec = _TYPED_ITEMS_NODE_SPECS.get(node.bl_idname)
    found = _find_cls(node.bl_idname)
    if spec is None or found is None:
        return None
    alias, cls = found
    items = list(getattr(node, spec.collection))
    method_map = spec.method_map or _SWITCH_METHOD
    if any((_item_socket_type(item) not in method_map for item in items)):
        return None
    in_sockets = [s for s in node.inputs if not s.identifier.startswith('__extend__')]
    out_sockets = [s for s in node.outputs if not s.identifier.startswith('__extend__')]
    fixed_inputs, item_inputs = (in_sockets[:len(in_sockets) - len(items)], in_sockets[len(in_sockets) - len(items):])
    item_outputs = out_sockets[len(out_sockets) - len(items):]
    kwargs = _items_fixed_kwargs(node, ctx, spec, fixed_inputs)
    if kwargs is None:
        return None
    ctx.used_aliases.add(alias)
    var_name = _make_var(spec.label, ctx.counter)
    prop_lines = _node_prop_lines(node)
    if not items and (not prop_lines) and (not ctx.outgoing.get(node.name)):
        var_name = '_' + var_name
    ref = Ref(var_name)
    ctor = _items_node_ctor(alias, cls, spec, node, kwargs)
    ctx.pending_lines.append(f'    {ref.name} = {ctor.render()}')
    for prop_line in prop_lines:
        ctx.pending_lines.append(f'    {ref.name}.node.{prop_line}')
    outputs: dict[str, Expr] = {ident: Attr(ref, attr) for ident, attr in spec.fixed_outputs}
    consumed = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    for in_socket, out_socket, item in zip(item_inputs, item_outputs, items):
        args, kwargs = _item_decl_args(ctx, node, item, in_socket)
        method = method_map[_item_socket_type(item)]
        call = Call(f'{ref.name}.items.{method}', args, kwargs)
        if out_socket.identifier in consumed:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            outputs[out_socket.identifier] = Attr(handle, 'output')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    return _Val(None, outputs=outputs)
for _items_bl_idname in _TYPED_ITEMS_NODE_SPECS:
    register_emitter(_items_bl_idname)(_emit_typed_items_node)

@register_emitter('GeometryNodeCurveSetHandles')
def _emit_set_handle_type(node, ctx: EmitContext) -> Expr | _Val | None:
    call = ctx.constructor(node)
    if 'LEFT' not in node.mode:
        call.kwargs['left'] = Lit(False)
    if 'RIGHT' not in node.mode:
        call.kwargs['right'] = Lit(False)
    return call
_COLOR_RAMP_SETTINGS = {'color_interpolation': 'interpolation', 'hue_interpolation': 'hue_interpolation', 'mode': 'color_mode'}

@register_emitter('ShaderNodeValToRGB')
def _emit_color_ramp(node, ctx: EmitContext) -> Expr | _Val | None:
    call = ctx.constructor(node)
    ramp = node.color_ramp
    found = _find_cls(node.bl_idname)
    assert found is not None
    params = _signature(found[1].__init__).parameters
    stops = tuple(((element.position, tuple(element.color)) for element in ramp.elements))
    if _norm_floats(stops) != _norm_floats(params['items'].default):
        call.kwargs['items'] = Lit(stops)
    for param, attr in _COLOR_RAMP_SETTINGS.items():
        value = getattr(ramp, attr)
        if value != params[param].default:
            call.kwargs[param] = Lit(value)
    return call

@register_emitter('ShaderNodeFloatCurve')
def _emit_float_curve(node, ctx: EmitContext) -> Expr | _Val | None:
    call = ctx.constructor(node)
    found = _find_cls(node.bl_idname)
    assert found is not None
    default = _signature(found[1].__init__).parameters['items'].default
    points = tuple((tuple(point.location) if point.handle_type == 'AUTO' else (*point.location, point.handle_type) for point in node.mapping.curves[0].points))
    if _norm_floats(points) != _norm_floats(default):
        call.kwargs['items'] = Lit(points)
    return call

@register_emitter('NodeReroute')
def _emit_reroute(node, ctx: EmitContext) -> Expr | _Val | None:
    ctx.used_aliases.add('g')
    link = ctx.input_link(node, node.inputs[0].identifier)
    if link is None:
        return Call('g.Reroute')
    return Call('g.Reroute', kwargs={'input': ctx.socket_expr(link)})

@register_emitter('GeometryNodeViewer')
def _emit_viewer(node, ctx: EmitContext) -> Expr | _Val | None:
    ctx.used_aliases.add('g')
    kwargs: dict[str, Expr] = {}
    if node.domain != 'AUTO':
        kwargs['domain'] = Lit(node.domain)
    if getattr(node, 'ui_shortcut', 0):
        kwargs['ui_shortcut'] = Lit(node.ui_shortcut)
    order = {s.identifier: i for i, s in enumerate(node.inputs)}
    links = sorted(ctx.incoming.get(node.name, ()), key=lambda link: order.get(link.to_socket.identifier, 0))
    var = _make_var('viewer', ctx.counter)
    if not links:
        var = '_' + var
    ctx.pending_lines.append(f"    {var} = {Call('g.Viewer', kwargs=kwargs).render()}")
    for link in links:
        statement = BinOp('>>', ctx.upstream_expr(link, pipeline=True), Ref(var))
        ctx.pending_lines.extend(_stmt_lines(statement))
    return _Val(None, outputs={})

def _bundle_item_call(receiver: str, item, args: list[Expr], method_map: dict[str, str], kwargs: dict[str, Expr] | None=None) -> Call:
    kwargs = dict(kwargs or {})
    if getattr(item, 'structure_type', 'AUTO') != 'AUTO':
        kwargs['structure_type'] = Lit(item.structure_type)
    return Call(f'{receiver}.{method_map[item.socket_type]}', args, kwargs)

def _item_decl_args(ctx: EmitContext, node, item, socket) -> tuple[list[Expr], dict[str, Expr]]:
    return _decl_args(ctx.input_link(node, socket.identifier), socket, item.name, ctx)

def _decl_args(link: _Link | None, default_socket, name: str, ctx: EmitContext) -> tuple[list[Expr], dict[str, Expr]]:
    value: Expr | None = None
    if link is not None:
        value = _zone_value_expr(ctx, link)
    elif default_socket is not None:
        default = _significant_default(default_socket)
        if default is not None:
            value = Lit(default)
    if value is None:
        return ([], {'name': Lit(name)})
    return ([value, Lit(name)], {})

def _combine_bundle_dict(node, ctx: EmitContext) -> Expr:
    items: dict[str, Expr] = {}
    for socket, item in zip((s for s in node.inputs if not s.identifier.startswith('__extend__')), node.bundle_items):
        link = ctx.input_link(node, socket.identifier)
        items[socket.name] = ctx.upstream_expr(link) if link is not None else Lit(item.socket_type)
    kwargs: dict[str, Expr] = {'items': DictExpr(items)}
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    return Call('g.CombineBundle', kwargs=kwargs)

@register_emitter('NodeCombineBundle')
def _emit_combine_bundle(node, ctx: EmitContext) -> Expr | _Val | None:
    items = list(node.bundle_items)
    ctx.used_aliases.add('g')
    if any((item.socket_type not in _SWITCH_METHOD for item in items)):
        return _combine_bundle_dict(node, ctx)
    kwargs: dict[str, Expr] = {}
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    var_name = _make_var('combine_bundle', ctx.counter)
    if not items and (not ctx.outgoing.get(node.name)):
        var_name = '_' + var_name
    ref = Ref(var_name)
    ctor = Call('g.CombineBundle', kwargs=kwargs)
    ctx.pending_lines.append(f'    {ref.name} = {ctor.render()}')
    for socket, item in zip(_prefixed_sockets(node, 'Item_'), items):
        args, kwargs = _item_decl_args(ctx, node, item, socket)
        call = _bundle_item_call(f'{ref.name}.items', item, args, _SWITCH_METHOD, kwargs)
        ctx.pending_lines.append(f'    {call.render()}')
    return _Val(None, outputs={'Bundle': Attr(ref, 'o.bundle')})

def _separate_bundle_dict(node, ctx: EmitContext) -> Expr:
    items: dict[str, Expr] = {item.name: Lit(item.socket_type) for item in node.bundle_items}
    bundle_link = ctx.input_link(node, 'Bundle')
    args = [ctx.upstream_expr(bundle_link)] if bundle_link is not None else []
    kwargs: dict[str, Expr] = {'items': DictExpr(items)}
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    return Call('g.SeparateBundle', args, kwargs)

@register_emitter('NodeSeparateBundle')
def _emit_separate_bundle(node, ctx: EmitContext) -> Expr | _Val | None:
    items = list(node.bundle_items)
    ctx.used_aliases.add('g')
    if any((item.socket_type not in _SWITCH_METHOD for item in items)):
        return _separate_bundle_dict(node, ctx)
    bundle_link = ctx.input_link(node, 'Bundle')
    args = [ctx.upstream_expr(bundle_link)] if bundle_link is not None else []
    kwargs: dict[str, Expr] = {}
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    var_name = _make_var('separate_bundle', ctx.counter)
    if not items:
        var_name = '_' + var_name
    ref = Ref(var_name)
    ctor = Call('g.SeparateBundle', args, kwargs)
    ctx.pending_lines.append(f'    {ref.name} = {ctor.render()}')
    outputs: dict[str, Expr] = {}
    consumed = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    for socket, item in zip(_prefixed_sockets(node, 'Item_', output=True), items):
        call = _bundle_item_call(f'{ref.name}.items', item, [Lit(item.name)], _SWITCH_METHOD)
        if socket.identifier in consumed:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            outputs[socket.identifier] = Attr(handle, 'output')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    return _Val(None, outputs=outputs)

def _closure_to_list_kwargs(node, ctx: EmitContext) -> dict[str, Expr]:
    kwargs: dict[str, Expr] = {}
    count_link = ctx.input_link(node, 'Count')
    if count_link is not None:
        kwargs['count'] = ctx.upstream_expr(count_link)
    else:
        socket = _input_socket_by_identifier(node, 'Count')
        fresh = _get_blender_socket_defaults(ctx.node_tree.bl_idname, node.bl_idname).get('Count')
        if socket is not None and (not _eq(socket.default_value, fresh)):
            kwargs['count'] = Lit(socket.default_value)
    closure_link = ctx.input_link(node, 'Closure')
    if closure_link is not None:
        kwargs['closure'] = ctx.upstream_expr(closure_link)
    return kwargs

def _closure_to_list_dict(node, ctx: EmitContext) -> Expr:
    kwargs = _closure_to_list_kwargs(node, ctx)
    kwargs['items'] = DictExpr({item.name: Lit(item.socket_type) for item in node.list_items})
    return Call('g.ClosureToList', kwargs=kwargs)

@register_emitter('GeometryNodeClosureToList')
def _emit_closure_to_list(node, ctx: EmitContext) -> Expr | _Val | None:
    items = list(node.list_items)
    ctx.used_aliases.add('g')
    if any((item.socket_type not in _SWITCH_METHOD for item in items)):
        return _closure_to_list_dict(node, ctx)
    var_name = _make_var('closure_to_list', ctx.counter)
    if not items:
        var_name = '_' + var_name
    ref = Ref(var_name)
    ctor = Call('g.ClosureToList', kwargs=_closure_to_list_kwargs(node, ctx))
    ctx.pending_lines.append(f'    {ref.name} = {ctor.render()}')
    outputs: dict[str, Expr] = {}
    consumed = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    for socket, item in zip(_prefixed_sockets(node, 'List_', output=True), items):
        call = _bundle_item_call(f'{ref.name}.items', item, [Lit(item.name)], _SWITCH_METHOD)
        if socket.identifier in consumed:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            outputs[socket.identifier] = Attr(handle, 'output')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    return _Val(None, outputs=outputs)

def _evaluate_closure_dict(node, ctx: EmitContext) -> Expr:
    input_items: dict[str, Expr] = {}
    in_sockets = (s for s in node.inputs if s.identifier != 'Closure' and (not s.identifier.startswith('__extend__')))
    for socket, item in zip(in_sockets, node.input_items):
        link = ctx.input_link(node, socket.identifier)
        input_items[socket.name] = ctx.upstream_expr(link) if link is not None else Lit(item.socket_type)
    output_items: dict[str, Expr] = {item.name: Lit(item.socket_type) for item in node.output_items}
    closure_link = ctx.input_link(node, 'Closure')
    args = [ctx.upstream_expr(closure_link)] if closure_link is not None else []
    kwargs: dict[str, Expr] = {}
    if input_items:
        kwargs['input_items'] = DictExpr(input_items)
    if output_items:
        kwargs['output_items'] = DictExpr(output_items)
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    return Call('g.EvaluateClosure', args, kwargs)

@register_emitter('NodeEvaluateClosure')
def _emit_evaluate_closure(node, ctx: EmitContext) -> Expr | _Val | None:
    in_items = list(node.input_items)
    out_items = list(node.output_items)
    ctx.used_aliases.add('g')
    if any((i.socket_type not in _SWITCH_METHOD for i in in_items + out_items)):
        return _evaluate_closure_dict(node, ctx)
    closure_link = ctx.input_link(node, 'Closure')
    args = [ctx.upstream_expr(closure_link)] if closure_link is not None else []
    kwargs: dict[str, Expr] = {}
    if node.define_signature:
        kwargs['define_signature'] = Lit(True)
    var_name = _make_var('evaluate_closure', ctx.counter)
    if not in_items and (not out_items):
        var_name = '_' + var_name
    ref = Ref(var_name)
    ctor = Call('g.EvaluateClosure', args, kwargs)
    ctx.pending_lines.append(f'    {ref.name} = {ctor.render()}')
    for socket, item in zip(_prefixed_sockets(node, 'Item_'), in_items):
        args, kwargs = _item_decl_args(ctx, node, item, socket)
        call = _bundle_item_call(f'{ref.name}.inputs', item, args, _SWITCH_METHOD, kwargs)
        ctx.pending_lines.append(f'    {call.render()}')
    outputs: dict[str, Expr] = {}
    consumed = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    for socket, item in zip(_prefixed_sockets(node, 'Item_', output=True), out_items):
        call = _bundle_item_call(f'{ref.name}.outputs', item, [Lit(item.name)], _SWITCH_METHOD)
        if socket.identifier in consumed:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            outputs[socket.identifier] = Attr(handle, 'output')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    return _Val(None, outputs=outputs)

def _group_input_defaults(node_tree) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for item in node_tree.interface.items_tree:
        if getattr(item, 'item_type', '') != 'SOCKET' or item.in_out != 'INPUT':
            continue
        if not hasattr(item, 'default_value'):
            continue
        value = item.default_value
        try:
            value = tuple(value)
        except TypeError:
            pass
        defaults[item.identifier] = value
    return defaults

def _emit_group_node(node, ctx: EmitContext) -> Expr | _Val | None:
    inner = node.node_tree
    if inner is None:
        alias = _TREE_ALIAS[node.id_data.bl_idname]
        ctx.used_aliases.add(alias)
        return Call(f'{alias}.Group')
    if ctx.collector is None:
        return None
    class_name = ctx.collector.register(inner) if inner.library is None or inner.name in ctx.collector.external_groups else None
    iface_defaults = _group_input_defaults(inner)
    typed_params: dict[str, str] | None = None
    if inner.name in ctx.collector.typed_groups:
        from ..builder._utils import typed_param_names
        typed_params = typed_param_names(node.inputs)
    names = [s.name for s in node.inputs if not s.identifier.startswith('__extend__')]
    items: dict[str, Expr] = {}
    named_links: list[tuple[str, Expr]] = []

    def _add(socket, value: Expr) -> None:
        if typed_params is not None:
            items[typed_params[socket.identifier]] = value
        elif names.count(socket.name) > 1:
            named_links.append((socket.name, value))
        else:
            items[socket.name] = value
    for socket in node.inputs:
        if socket.identifier.startswith('__extend__'):
            continue
        link = ctx.input_link(node, socket.identifier)
        if link is not None:
            _add(socket, ctx.upstream_expr(link))
            continue
        if not hasattr(socket, 'default_value'):
            continue
        current = socket.default_value
        try:
            current = tuple(current)
        except TypeError:
            pass
        iface_default = iface_defaults.get(socket.identifier, _UNSET)
        if names.count(socket.name) > 1 or iface_default is _UNSET or (not _eq(current, iface_default)):
            _add(socket, Lit(socket.default_value))
    if class_name is None:
        alias = {'GeometryNodeTree': 'g', 'ShaderNodeTree': 's', 'CompositorNodeTree': 'c'}[inner.bl_idname]
        ctx.used_aliases.add(alias)
        return GroupCall(f'{alias}.Group', {'node_tree': Lit(inner.name), **items}, named_links)
    return GroupCall(class_name, items, named_links)
for _group_bl_idname in _GROUP_BASES:
    register_emitter(_group_bl_idname)(_emit_group_node)

@dataclass
class _ZoneState:
    targets: dict[str, Expr]
    outputs: dict[str, Expr]

def _prefixed_sockets(node, prefix: str, *, output: bool=False) -> list:
    sockets = node.outputs if output else node.inputs
    return [s for s in sockets if s.identifier.startswith(prefix)]

def _item_socket_type(item) -> str:
    return getattr(item, 'socket_type', None) or item.data_type

def _significant_default(socket) -> Any | None:
    if not hasattr(socket, 'default_value'):
        return None
    try:
        value = socket.default_value
    except Exception:
        return None
    if isinstance(value, str):
        return value or None
    if value is None or _is_zero(value):
        return None
    try:
        return tuple(value)
    except TypeError:
        return value

def _zone_item_method(namespace: str, item) -> str:
    return f'{namespace}.{_SWITCH_METHOD[_item_socket_type(item)]}'

def _zone_value_expr(ctx: EmitContext, link: _Link) -> Expr:
    real_outputs = [s for s in link.from_node.outputs if s.enabled]
    if len(real_outputs) > 1:
        return ctx.socket_expr(link)
    return ctx.upstream_expr(link)

def _zone_required(node) -> Any:
    paired = getattr(node, 'paired_output', None)
    if paired is None:
        raise CodegenError(f"zone input node '{node.name}' has no paired output — the tree cannot be expressed with a zone wrapper")
    return paired

class _ZoneItemPlan(NamedTuple):
    method: str
    item: Any
    value_link: _Link | None
    default_socket: Any | None
    extra_kwargs: dict[str, Expr]
    current_id: str | None
    next_id: str | None
    result_id: str | None
    roles: tuple[str, str, str]

def _emit_zone_items(ctx: EmitContext, zone_ref: Ref, node, out_node, plans: list[_ZoneItemPlan]) -> tuple[dict[str, Expr], dict[str, Expr], dict[str, Expr]]:
    consumed_current = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    linked_next = {link.to_socket.identifier for link in ctx.incoming.get(out_node.name, ())}
    consumed_result = {link.from_socket.identifier for link in ctx.outgoing.get(out_node.name, ())}
    current_map: dict[str, Expr] = {}
    targets: dict[str, Expr] = {}
    outputs: dict[str, Expr] = {}
    for plan in plans:
        args, kwargs = _decl_args(plan.value_link, plan.default_socket, plan.item.name, ctx)
        kwargs.update(plan.extra_kwargs)
        call = Call(f'{zone_ref.name}.{plan.method}', args, kwargs)
        needed = plan.current_id in consumed_current or plan.next_id in linked_next or plan.result_id in consumed_result
        if needed:
            handle = Ref(_make_var(plan.item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            current_attr, next_attr, result_attr = plan.roles
            if plan.current_id is not None:
                current_map[plan.current_id] = Attr(handle, current_attr)
            if plan.next_id is not None:
                targets[plan.next_id] = Attr(handle, next_attr)
            if plan.result_id is not None:
                outputs[plan.result_id] = Attr(handle, result_attr)
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    return (current_map, targets, outputs)

def _emit_state_zone_input(node, ctx: EmitContext, *, ctor: str, label: str, items_attr: str, special_outputs: dict[str, str], ctor_args: list[Expr], extra_targets: dict[str, str]) -> _Val:
    out_node = _zone_required(node)
    ctx.used_aliases.add('g')
    zone_ref = Ref(_make_var(label, ctx.counter))
    ctx.pending_lines.append(f'    {zone_ref.name} = {Call(ctor, ctor_args).render()}')
    if (inspection := getattr(out_node, 'inspection_index', 0)):
        ctx.pending_lines.append(f'    {zone_ref.name}.output.node.inspection_index = {inspection}')
    items = list(getattr(out_node, items_attr))
    in_inputs = _prefixed_sockets(node, 'Item_')
    in_outputs = _prefixed_sockets(node, 'Item_', output=True)
    out_inputs = _prefixed_sockets(out_node, 'Item_')
    out_outputs = _prefixed_sockets(out_node, 'Item_', output=True)
    plans = [_ZoneItemPlan(method=_zone_item_method('items', item), item=item, value_link=ctx.input_link(node, in_inputs[i].identifier), default_socket=in_inputs[i], extra_kwargs={}, current_id=in_outputs[i].identifier, next_id=out_inputs[i].identifier, result_id=out_outputs[i].identifier, roles=('current', 'next', 'result')) for i, item in enumerate(items)]
    current_map, targets, outputs = _emit_zone_items(ctx, zone_ref, node, out_node, plans)
    for identifier, attr in special_outputs.items():
        current_map[identifier] = Attr(zone_ref, attr)
    for identifier, attr in extra_targets.items():
        targets[identifier] = Attr(zone_ref, attr)
    ctx.zones[out_node.name] = _ZoneState(targets, outputs)
    return _Val(None, outputs=current_map)

@register_emitter('GeometryNodeSimulationInput')
def _emit_simulation_input(node, ctx: EmitContext) -> _Val:
    return _emit_state_zone_input(node, ctx, ctor='g.SimulationZone', label='simulation_zone', items_attr='state_items', special_outputs={'Delta Time': 'delta_time'}, ctor_args=[], extra_targets={'Skip': 'output.i.skip'})

@register_emitter('GeometryNodeRepeatInput')
def _emit_repeat_input(node, ctx: EmitContext) -> _Val:
    ctor_args: list[Expr] = []
    link = ctx.input_link(node, 'Iterations')
    if link is not None:
        ctor_args.append(_zone_value_expr(ctx, link))
    else:
        iterations = node.inputs['Iterations'].default_value
        if iterations != 1:
            ctor_args.append(Lit(iterations))
    return _emit_state_zone_input(node, ctx, ctor='g.RepeatZone', label='repeat_zone', items_attr='repeat_items', special_outputs={'Iteration': 'iteration'}, ctor_args=ctor_args, extra_targets={})

@register_emitter('GeometryNodeForeachGeometryElementInput')
def _emit_foreach_input(node, ctx: EmitContext) -> _Val:
    out_node = _zone_required(node)
    ctx.used_aliases.add('g')
    kwargs: dict[str, Expr] = {}
    geometry_link = ctx.input_link(node, 'Geometry')
    if geometry_link is not None:
        kwargs['geometry'] = _zone_value_expr(ctx, geometry_link)
    selection_link = ctx.input_link(node, 'Selection')
    if selection_link is not None:
        kwargs['selection'] = _zone_value_expr(ctx, selection_link)
    elif node.inputs['Selection'].default_value is not True:
        kwargs['selection'] = Lit(node.inputs['Selection'].default_value)
    ctor = 'g.ForEachGeometryElementZone'
    if out_node.domain != 'POINT':
        ctor += f'.{out_node.domain.lower()}'
    zone_ref = Ref(_make_var('for_each', ctx.counter))
    ctx.pending_lines.append(f'    {zone_ref.name} = {Call(ctor, kwargs=kwargs).render()}')
    generation_items = list(out_node.generation_items)
    if not generation_items or generation_items[0].socket_type != 'GEOMETRY' or generation_items[0].name != 'Geometry':
        raise CodegenError(f"foreach zone '{node.name}': the first generation item is not the default Geometry item, which the zone wrapper cannot rebuild")
    plans: list[_ZoneItemPlan] = []
    in_inputs = _prefixed_sockets(node, 'Input_')
    in_outputs = _prefixed_sockets(node, 'Input_', output=True)
    for i, item in enumerate(out_node.input_items):
        plans.append(_ZoneItemPlan(method=_zone_item_method('items', item), item=item, value_link=ctx.input_link(node, in_inputs[i].identifier), default_socket=in_inputs[i], extra_kwargs={}, current_id=in_outputs[i].identifier, next_id=None, result_id=None, roles=('output', '', '')))
    main_inputs = _prefixed_sockets(out_node, 'Main_')
    main_outputs = _prefixed_sockets(out_node, 'Main_', output=True)
    for i, item in enumerate(out_node.main_items):
        plans.append(_ZoneItemPlan(method=_zone_item_method('main_items', item), item=item, value_link=None, default_socket=main_inputs[i], extra_kwargs={}, current_id=None, next_id=main_inputs[i].identifier, result_id=main_outputs[i].identifier, roles=('', 'input', 'output')))
    gen_inputs = _prefixed_sockets(out_node, 'Generation_')
    gen_outputs = _prefixed_sockets(out_node, 'Generation_', output=True)
    for i, item in enumerate(generation_items):
        if i == 0:
            continue
        extra: dict[str, Expr] = {}
        if item.domain != 'POINT':
            extra['domain'] = Lit(item.domain)
        plans.append(_ZoneItemPlan(method=_zone_item_method('generated_items', item), item=item, value_link=None, default_socket=gen_inputs[i], extra_kwargs=extra, current_id=None, next_id=gen_inputs[i].identifier, result_id=gen_outputs[i].identifier, roles=('', 'input', 'output')))
    current_map, targets, outputs = _emit_zone_items(ctx, zone_ref, node, out_node, plans)
    current_map['Index'] = Attr(zone_ref, 'index')
    current_map['Element'] = Attr(zone_ref, 'input.o.element')
    targets[gen_inputs[0].identifier] = Attr(zone_ref, 'generation.input')
    outputs[gen_outputs[0].identifier] = Attr(zone_ref, 'generation.output')
    outputs['Geometry'] = Attr(zone_ref, 'output')
    ctx.zones[out_node.name] = _ZoneState(targets, outputs)
    return _Val(None, outputs=current_map)

@register_emitter('GeometryNodeSimulationOutput')
@register_emitter('GeometryNodeRepeatOutput')
@register_emitter('GeometryNodeForeachGeometryElementOutput')
def _emit_zone_output(node, ctx: EmitContext) -> _Val:
    state = ctx.zones.pop(node.name, None)
    if state is None:
        raise CodegenError(f"zone output node '{node.name}' was emitted before its paired input node — is the zone paired?")
    order = {s.identifier: i for i, s in enumerate(node.inputs)}
    links = sorted(ctx.incoming.get(node.name, ()), key=lambda link: order.get(link.to_socket.identifier, 0))
    for link in links:
        target = state.targets.get(link.to_socket.identifier)
        if target is None:
            raise CodegenError(f"zone output node '{node.name}' has a link into '{link.to_socket.name}' with no emit target")
        statement = BinOp('>>', ctx.upstream_expr(link, pipeline=True), target)
        ctx.pending_lines.extend(_stmt_lines(statement))
    return _Val(None, outputs=state.outputs)

def _closure_item_call(zone_ref: Ref, namespace: str, item) -> Call:
    kwargs: dict[str, Expr] = {}
    if getattr(item, 'structure_type', 'AUTO') != 'AUTO':
        kwargs['structure_type'] = Lit(item.structure_type)
    if _item_socket_type(item) not in _SWITCH_METHOD:
        kwargs['type'] = Lit(_item_socket_type(item))
        return Call(f'{zone_ref.name}.{namespace}.new', [Lit(item.name)], kwargs)
    return Call(f'{zone_ref.name}.{_zone_item_method(namespace, item)}', [Lit(item.name)], kwargs)

@register_emitter('NodeClosureInput')
def _emit_closure_input(node, ctx: EmitContext) -> _Val:
    out_node = _zone_required(node)
    ctx.used_aliases.add('g')
    zone_ref = Ref(_make_var('closure_zone', ctx.counter))
    ctx.pending_lines.append(f"    {zone_ref.name} = {Call('g.ClosureZone').render()}")
    consumed = {link.from_socket.identifier for link in ctx.outgoing.get(node.name, ())}
    in_outputs = _prefixed_sockets(node, 'Item_', output=True)
    current_map: dict[str, Expr] = {}
    for socket, item in zip(in_outputs, out_node.input_items):
        call = _closure_item_call(zone_ref, 'inputs', item)
        if socket.identifier in consumed:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            current_map[socket.identifier] = Attr(handle, 'output')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    linked_next = {link.to_socket.identifier for link in ctx.incoming.get(out_node.name, ())}
    out_inputs = _prefixed_sockets(out_node, 'Item_')
    targets: dict[str, Expr] = {}
    for socket, item in zip(out_inputs, out_node.output_items):
        call = _closure_item_call(zone_ref, 'outputs', item)
        if socket.identifier in linked_next:
            handle = Ref(_make_var(item.name, ctx.counter))
            ctx.pending_lines.append(f'    {handle.name} = {call.render()}')
            targets[socket.identifier] = Attr(handle, 'input')
        else:
            ctx.pending_lines.append(f'    {call.render()}')
    ctx.zones[out_node.name] = _ZoneState(targets, {'Closure': Attr(zone_ref, 'closure')})
    return _Val(None, outputs=current_map)
register_emitter('NodeClosureOutput')(_emit_zone_output)

@register_emitter('CompositorNodeDisplace')
def _emit_displace(node, ctx):
    ctx.used_aliases.add('c')
    kwargs = {}
    for key in ('Image', 'Displacement', 'Interpolation', 'Extension X', 'Extension Y'):
        socket = node.inputs.get(key)
        if socket is None:
            continue
        link = ctx.input_link(node, socket.identifier)
        if link:
            kwargs[_normalize(key)] = ctx.upstream_expr(link)
        elif hasattr(socket, 'default_value'):
            kwargs[_normalize(key)] = Lit(socket.default_value)
    if 'Vector' in node.inputs:
        link = ctx.input_link(node, 'Vector')
        vector = ctx.upstream_expr(link) if link else Lit(node.inputs['Vector'].default_value)
        scales = []
        for key in ('X Scale', 'Y Scale'):
            link = ctx.input_link(node, key)
            scales.append(ctx.upstream_expr(link) if link else Lit(node.inputs[key].default_value))
        if not all((not ctx.input_link(node, key) and node.inputs[key].default_value == 1 for key in ('X Scale', 'Y Scale'))):
            ctx.used_aliases.add('g')
            vector = Call('g.VectorMath.multiply', [vector, Call('g.CombineXYZ', kwargs={'x': scales[0], 'y': scales[1]})])
        kwargs['displacement'] = vector
        kwargs['interpolation'] = Lit('Anisotropic')
    return Call('c.Displace', kwargs=kwargs)
