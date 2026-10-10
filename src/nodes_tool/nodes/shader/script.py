# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from nodes_tool.native import set_property
import typing
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor

class Script(BaseNode):
    _bl_idname = 'ShaderNodeScript'

    def __init__(self, filepath: str='', mode: Literal['INTERNAL', 'EXTERNAL']='INTERNAL', use_auto_update: bool=False, bytecode: str='', bytecode_hash: str=''):
        super().__init__()
        key_args = {}
        self.filepath = filepath
        self.mode = mode
        self.use_auto_update = use_auto_update
        self.bytecode = bytecode
        self.bytecode_hash = bytecode_hash
        self._establish_links(**key_args)

    @classmethod
    def internal(cls, *, bytecode: str='', bytecode_hash: str='') -> 'Script':
        return cls(mode='INTERNAL', bytecode=bytecode, bytecode_hash=bytecode_hash)

    @classmethod
    def external(cls, *, filepath: str='', use_auto_update: bool=False, bytecode: str='', bytecode_hash: str='') -> 'Script':
        return cls(mode='EXTERNAL', filepath=filepath, use_auto_update=use_auto_update, bytecode=bytecode, bytecode_hash=bytecode_hash)

    @property
    def filepath(self) -> str:
        return self.node.filepath

    @filepath.setter
    def filepath(self, value: str) -> None:
        set_property(self.node, 'filepath', value)

    @property
    def mode(self) -> Literal['INTERNAL', 'EXTERNAL']:
        return self.node.mode

    @mode.setter
    def mode(self, value: Literal['INTERNAL', 'EXTERNAL']) -> None:
        set_property(self.node, 'mode', value)

    @property
    def use_auto_update(self) -> bool:
        return self.node.use_auto_update

    @use_auto_update.setter
    def use_auto_update(self, value: bool) -> None:
        set_property(self.node, 'use_auto_update', value)

    @property
    def bytecode(self) -> str:
        return self.node.bytecode

    @bytecode.setter
    def bytecode(self, value: str) -> None:
        set_property(self.node, 'bytecode', value)

    @property
    def bytecode_hash(self) -> str:
        return self.node.bytecode_hash

    @bytecode_hash.setter
    def bytecode_hash(self, value: str) -> None:
        set_property(self.node, 'bytecode_hash', value)
