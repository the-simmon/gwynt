from __future__ import annotations

import enum
from typing import List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from source.core.card import Card


class CombatRow(enum.Enum):
    CLOSE = 0
    RANGE = 1
    SIEGE = 2
    SPECIAL = 3
    AGILE = 4
    NONE = 5

    def __lt__(self, other):
        return self.value < other.value

    @staticmethod
    def get_possible_rows(input: Union[Card, CombatRow]) -> List[CombatRow]:
        combat_row = input if type(input) is CombatRow else input.combat_row
        result = []
        if combat_row is CombatRow.AGILE or combat_row is CombatRow.SPECIAL:
            result.append(CombatRow.CLOSE)
            result.append(CombatRow.RANGE)
            if combat_row is CombatRow.SPECIAL:
                result.append(CombatRow.SIEGE)
        else:
            result.append(combat_row)
        return result
