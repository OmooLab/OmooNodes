# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket
from ...socket_types import InputColor

class FileOutput(BaseNode):
    _bl_idname = 'CompositorNodeOutputFile'

    def __init__(self, directory: str='', file_name: str='', save_as_render: bool=False, use_file_extension: bool=False):
        super().__init__()
        key_args = {}
        self.directory = directory
        self.file_name = file_name
        self.save_as_render = save_as_render
        self.use_file_extension = use_file_extension
        self._establish_links(**key_args)

    @property
    def directory(self) -> str:
        return self.node.directory

    @directory.setter
    def directory(self, value: str) -> None:
        set_property(self.node, 'directory', value)

    @property
    def file_name(self) -> str:
        return self.node.file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        set_property(self.node, 'file_name', value)

    @property
    def save_as_render(self) -> bool:
        return self.node.save_as_render

    @save_as_render.setter
    def save_as_render(self, value: bool) -> None:
        set_property(self.node, 'save_as_render', value)

    @property
    def use_file_extension(self) -> bool:
        return self.node.use_file_extension

    @use_file_extension.setter
    def use_file_extension(self, value: bool) -> None:
        set_property(self.node, 'use_file_extension', value)

class Viewer(BaseNode):
    _bl_idname = 'CompositorNodeViewer'

    def __init__(self, image: InputColor=(0.0, 0.0, 0.0, 1.0), *, ui_shortcut: int=0):
        super().__init__()
        key_args = {'Image': image}
        self.ui_shortcut = ui_shortcut
        self._establish_links(**key_args)

    @property
    def ui_shortcut(self) -> int:
        return self.node.ui_shortcut

    @ui_shortcut.setter
    def ui_shortcut(self, value: int) -> None:
        set_property(self.node, 'ui_shortcut', value)
