from typing import List
from .one_hot_enum import OneHotEnum


class CombatRow(OneHotEnum):
    CLOSE = 0
    RANGE = 1
    SIEGE = 2
    SPECIAL = 3


class Ability(OneHotEnum):
    NONE = 0
    EMPTY_PLACEHOLDER = 1
    MEDIC = 2
    MORALE_BOOST = 3
    MUSTER = 4
    SPY = 5
    TIGHT_BOND = 6
    SCORCH = 7
    COMMANDERS_HORN = 8
    CLEAR_WEATHER = 9
    FROST = 10
    FOG = 11
    RAIN = 12


class Card:

    def __init__(self, combat_row: CombatRow, damage: int, ability: Ability, hero: bool = False, muster: str = None):
        self.combat_row = combat_row
        self.damage = damage
        self.ability = ability
        self.hero = hero
        self.muster = muster

    def repr_list(self) -> List[int]:
        return [self.damage] + self.ability.one_hot() + [int(self.hero)]

    @classmethod
    def empty_card_repr(cls) -> List[int]:
        return Card(CombatRow.CLOSE, 0, Ability.EMPTY_PLACEHOLDER).repr_list()

    def __eq__(self, other):
        return other is not None and self.combat_row is other.combat_row and self.damage == other.damage and self.ability is other.ability \
               and self.muster == other.muster and self.hero == other.hero

    def __hash__(self):
        return self.combat_row.value + self.damage + self.ability.value + hash(self.muster)
