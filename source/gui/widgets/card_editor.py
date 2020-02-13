import tkinter as tk

from source.core.card import Ability, Muster, Card, LeaderAbility, LeaderCard
from source.core.comabt_row import CombatRow
from source.gui.widgets.enum_combobox import EnumCombobox


class CardEditor(tk.LabelFrame):

    def __init__(self, master):
        super().__init__(master, text='Card editor', borderwidth=2, relief=tk.SOLID)
        tk.Label(self, text="Row").grid(row=0, column=0)
        self.row_box = EnumCombobox[CombatRow](self, CombatRow, default=CombatRow.NONE)
        self.row_box.grid(row=0, column=1)

        tk.Label(self, text="Damage").grid(row=1, column=0)
        self.damage = tk.IntVar()
        tk.Spinbox(self, textvariable=self.damage, from_=0, to_=15).grid(row=1, column=1)
        self.is_hero = tk.BooleanVar()
        tk.Checkbutton(self, text="Hero", variable=self.is_hero).grid(row=1, column=2)

        tk.Label(self, text="Ability").grid(row=2, column=0)
        self.ability_box = EnumCombobox[Ability](self, Ability, default=Ability.NONE)
        self.ability_box.grid(row=2, column=1)

        tk.Label(self, text="Muster").grid(row=3, column=0)
        self.muster_box = EnumCombobox[Muster](self, Muster, default=Muster.NONE)
        self.muster_box.grid(row=3, column=1)

    def get_card(self) -> Card:
        row = self.row_box.get_value()
        damage = self.damage.get()
        hero = self.is_hero.get()
        ability = self.ability_box.get_value()
        muster = self.muster_box.get_value()
        return Card(row, damage, ability, hero, muster)


class LeaderCardEditor(CardEditor):

    def __init__(self, master):
        super().__init__(master)
        self.config(text='LeaderCard editor')

        tk.Label(self, text="LeaderAbility").grid(row=4, column=0)
        self.leader_ability_box = EnumCombobox[LeaderAbility](self, LeaderAbility, default=LeaderAbility.NONE)
        self.leader_ability_box.grid(row=4, column=1)

    def get_card(self) -> LeaderCard:
        row = self.row_box.get_value()
        damage = self.damage.get()
        hero = self.is_hero.get()
        ability = self.ability_box.get_value()
        muster = self.muster_box.get_value()
        leader_ability = self.leader_ability_box.get_value()
        return LeaderCard(row, damage, ability, hero, muster, leader_ability)
