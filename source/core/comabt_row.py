from __future__ import annotations

import enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from source.core.card import Card


class CombatRow(enum.Enum):
    CLOSE = 0
    RANGE = 1
    SIEGE = 2
    SPECIAL = 3
    AGILE = 4
    NONE = 5

    @staticmethod
    def get_possible_rows(card: Card) -> List[CombatRow]:
        result = []
        if card.combat_row is CombatRow.AGILE or card.combat_row is CombatRow.SPECIAL:
            result.append(CombatRow.CLOSE)
            result.append(CombatRow.RANGE)
            if card.combat_row is CombatRow.SPECIAL:
                result.append(CombatRow.SIEGE)
        else:
            result.append(card.combat_row)
        return result
