from __future__ import annotations

import enum
from copy import deepcopy
from typing import List


class CombatRow(enum.Enum):
    CLOSE = 0
    RANGE = 1
    SIEGE = 2
    SPECIAL = 3
    AGILE = 4

    @staticmethod
    def get_possible_rows(row: CombatRow) -> List[CombatRow]:
        result = []
        if row is CombatRow.AGILE or row is CombatRow.SPECIAL:
            result.append(CombatRow.CLOSE)
            result.append(CombatRow.RANGE)
            if row is CombatRow.SPECIAL:
                result.append(CombatRow.SIEGE)
        else:
            result.append(row)
        return result


class Ability(enum.Enum):
    NONE = 0
    EMPTY_PLACEHOLDER = 1
    MEDIC = 2
    MORALE_BOOST = 3
    MUSTER = 4
    SPY = 5
    TIGHT_BOND = 6
    SCORCH = 7
    COMMANDERS_HORN = 8
    SPECIAL_COMMANDERS_HORN = 9
    CLEAR_WEATHER = 10
    FROST = 11
    FOG = 12
    RAIN = 13
    PASS = 14

    def __lt__(self, other):
        return self.value < other.value


class Muster(enum.Enum):
    NONE = 0
    ARACHAS = 1
    CRONE = 2
    DWARVEN_SKIRMISHER = 3
    ELVEN_SKIRMISHER = 4
    GHOUL = 5
    HAVEKAR_SMUGGLER = 6
    NEKKER = 7
    VAMPIRE = 8


class Card:

    def __init__(self, combat_row: CombatRow, damage: int, ability: Ability = Ability.NONE, hero: bool = False,
                 muster: Muster = Muster.NONE):
        self.combat_row = combat_row
        self.damage = damage
        self.ability = ability
        self.hero = hero
        self.muster = muster

    def __eq__(self, other):
        return other is not None and self.combat_row is other.combat_row and self.damage == other.damage and \
               self.ability is other.ability and self.muster is other.muster and self.hero is other.hero

    def __hash__(self):
        return hash(self.combat_row) + self.damage + hash(self.ability) + hash(self.muster)

    def __mul__(self, count: int):
        return [deepcopy(self) for _ in range(count)]
