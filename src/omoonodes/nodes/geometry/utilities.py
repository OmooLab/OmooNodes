# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import ColorSocket
from ...socket_types import InputColor

class Reroute(BaseNode):
    _bl_idname = 'NodeReroute'

    def __init__(self, input: InputColor=(0.0, 0.0, 0.0, 1.0)):
        super().__init__()
        key_args = {'Input': input}
        self._establish_links(**key_args)
