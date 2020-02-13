import tkinter as tk

from source.core.comabt_row import CombatRow
from source.core.gameenvironment import CardSource, CardDestination, GameEnvironment
from source.gui.widgets.card_editor import CardEditor
from source.gui.widgets.enum_combobox import EnumCombobox


class CheatMenu(tk.LabelFrame):

    def __init__(self, master, environment: GameEnvironment):
        super().__init__(master, text='Cheat menu')

        tk.Label(self, text='Source').grid(row=0, column=0)
        values = [CardSource.HAND, CardSource.GRAVEYARD, CardSource.ENEMY_GRAVEYARD, CardSource.BOARD]
        self.source_box = EnumCombobox[CardSource](self, CardSource, default=CardSource.HAND, values=values)
        self.source_box.grid(row=0, column=1)

        tk.Label(self, text='Destination').grid(row=0, column=2)
        self.destination_box = EnumCombobox[CardDestination](self, CardDestination, default=CardDestination.BOARD)
        self.destination_box.grid(row=0, column=3)

        self.card_editor = CardEditor(self)
        self.card_editor.grid(row=1, column=0, columnspan=4)

        row_frame = tk.Frame(self)
        row_frame.grid(row=2, column=0, columnspan=4)
        tk.Label(row_frame, text='Target row').grid(row=0, column=0)
        self.target_row_box = EnumCombobox[CombatRow](row_frame, CombatRow)
        self.target_row_box.grid(row=0, column=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=4)
        tk.Button(button_frame, text='Play Card').grid(row=0, column=0)
        tk.Button(button_frame, text='Play Leader').grid(row=0, column=1)
        tk.Button(button_frame, text='Pass').grid(row=0, column=2)
