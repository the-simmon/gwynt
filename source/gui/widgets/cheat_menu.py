import tkinter as tk

from source.core.gameenvironment import CardSource, CardDestination
from source.gui.widgets.card_editor import CardEditor
from source.gui.widgets.enum_combobox import EnumCombobox


class CheatMenu(tk.LabelFrame):

    def __init__(self):
        super().__init__(text='Cheat menu')

        tk.Label(self, text='Source').grid(row=0, column=0)
        values = [CardSource.HAND, CardSource.GRAVEYARD, CardSource.ENEMY_GRAVEYARD, CardSource.BOARD]
        self.source_box = EnumCombobox[CardSource](self, CardSource, default=CardSource.HAND, values=values)
        self.source_box.grid(row=0, column=1)

        tk.Label(self, text='Destination').grid(row=0, column=2)
        self.source_box = EnumCombobox[CardDestination](self, CardDestination, default=CardDestination.BOARD)
        self.source_box.grid(row=0, column=3)

        self.card_editor = CardEditor(self)
        self.card_editor.grid(row=1, column=0, columnspan=4)

        frame = tk.Frame(self)
        frame.grid(row=2, column=0, columnspan=4)
        tk.Button(frame, text='Play Card').grid(row=0, column=0)
        tk.Button(frame, text='Play Leader').grid(row=0, column=1)
        tk.Button(frame, text='Pass').grid(row=0, column=2)
