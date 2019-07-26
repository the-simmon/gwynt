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
    HERO = 2
    MEDIC = 3
    MORALE_BOOST = 4
    MUSTER = 5
    SPY = 6
    TIGHT_BOND = 7
    SCORCH = 8
    CLEAR_WEATHER = 9
    FROST = 10
    FOG = 11
    RAIN = 12


class Card:

    def __init__(self, combat_row: CombatRow, damage: int, ability: Ability, muster: str = None):
        self.combat_row = combat_row
        self.damage = damage
        self.ability = ability
        self.muster = muster

    def repr_list(self) -> List[int]:
        return [self.damage] + self.ability.one_hot()

    @classmethod
    def empty_card_repr(cls, row) -> List[int]:
        return Card(row, 0, Ability.EMPTY_PLACEHOLDER).repr_list()




