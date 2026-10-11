# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
from typing import TYPE_CHECKING
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import FloatSocket
from ...socket_types import InputFloat

class Normalize(BaseNode):
    _bl_idname = 'CompositorNodeNormalize'

    def __init__(self, value: InputFloat=1.0):
        super().__init__()
        key_args = {'Value': value}
        self._establish_links(**key_args)
