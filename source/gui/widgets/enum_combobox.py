import tkinter as tk
import tkinter.ttk as ttk
from enum import Enum
from typing import TypeVar, Generic

T = TypeVar('T', bound=Enum)


class EnumCombobox(ttk.Combobox, Generic[T]):

    def __init__(self, master, enum_: T):
        self.enum = enum_
        self.var = tk.StringVar()
        values = [x.name for x in self.enum]
        super().__init__(master, textvariable=self.var, values=values)

    def get_value(self) -> T:
        return self.enum[self.var.get()]
