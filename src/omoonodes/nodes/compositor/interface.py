# Adapted from nodebpy 520.34.1, Brady Johnston; GPL-3.0-or-later.
from __future__ import annotations
from omoonodes.native import set_property
import typing
T = typing.TypeVar('T')
from typing import TYPE_CHECKING, Literal
import bpy
from ...builder import BaseNode, SocketAccessor
from ...builder.socket import BooleanSocket, ColorSocket, FloatSocket, FontSocket, IntegerSocket, MatrixSocket, MenuSocket, ObjectSocket, RotationSocket, StringSocket, VectorSocket
from ...socket_types import InputAny, InputBoolean, InputColor, InputFloat, InputFont, InputInteger, InputIntegerVector, InputMatrix, InputMenu, InputObject, InputRotation, InputString, InputVector

class EnableOutput(BaseNode):
    _bl_idname = 'NodeEnableOutput'

    def __init__(self, enable: InputBoolean=False, value: InputAny=None, *, data_type: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']='FLOAT'):
        super().__init__()
        key_args = {'Enable': enable, 'Value': value}
        self.data_type = data_type
        self._establish_links(**key_args)

    @classmethod
    def float(cls, enable: InputBoolean=False, value: InputFloat=None) -> 'EnableOutput[FloatSocket]':
        return EnableOutput(data_type='FLOAT', enable=enable, value=value)

    @classmethod
    def integer(cls, enable: InputBoolean=False, value: InputInteger=None) -> 'EnableOutput[IntegerSocket]':
        return EnableOutput(data_type='INT', enable=enable, value=value)

    @classmethod
    def boolean(cls, enable: InputBoolean=False, value: InputBoolean=None) -> 'EnableOutput[BooleanSocket]':
        return EnableOutput(data_type='BOOLEAN', enable=enable, value=value)

    @classmethod
    def vector(cls, enable: InputBoolean=False, value: InputVector=None) -> 'EnableOutput[VectorSocket]':
        return EnableOutput(data_type='VECTOR', enable=enable, value=value)

    @classmethod
    def color(cls, enable: InputBoolean=False, value: InputColor=None) -> 'EnableOutput[ColorSocket]':
        return EnableOutput(data_type='RGBA', enable=enable, value=value)

    @classmethod
    def rotation(cls, enable: InputBoolean=False, value: InputRotation=None) -> 'EnableOutput[RotationSocket]':
        return EnableOutput(data_type='ROTATION', enable=enable, value=value)

    @classmethod
    def matrix(cls, enable: InputBoolean=False, value: InputMatrix=None) -> 'EnableOutput[MatrixSocket]':
        return EnableOutput(data_type='MATRIX', enable=enable, value=value)

    @classmethod
    def string(cls, enable: InputBoolean=False, value: InputString=None) -> 'EnableOutput[StringSocket]':
        return EnableOutput(data_type='STRING', enable=enable, value=value)

    @classmethod
    def menu(cls, enable: InputBoolean=False, value: InputMenu=None) -> 'EnableOutput[MenuSocket]':
        return EnableOutput(data_type='MENU', enable=enable, value=value)

    @classmethod
    def object(cls, enable: InputBoolean=False, value: InputObject=None) -> 'EnableOutput[ObjectSocket]':
        return EnableOutput(data_type='OBJECT', enable=enable, value=value)

    @classmethod
    def font(cls, enable: InputBoolean=False, value: InputFont=None) -> 'EnableOutput[FontSocket]':
        return EnableOutput(data_type='FONT', enable=enable, value=value)

    @classmethod
    def integer_vector(cls, enable: InputBoolean=False, value: InputIntegerVector=None) -> 'EnableOutput[IntegerSocket]':
        return EnableOutput(data_type='INT_VECTOR', enable=enable, value=value)

    @property
    def data_type(self) -> Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']:
        return self.node.data_type

    @data_type.setter
    def data_type(self, value: Literal['FLOAT', 'INT', 'BOOLEAN', 'VECTOR', 'RGBA', 'ROTATION', 'MATRIX', 'STRING', 'MENU', 'OBJECT', 'FONT', 'INT_VECTOR']) -> None:
        set_property(self.node, 'data_type', value)

    @classmethod
    def __class_getitem__(cls, item):
        return cls
