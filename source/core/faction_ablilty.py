from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING

from source.core.card import Card
from source.core.player import Faction, Player

if TYPE_CHECKING:
    from source.core.board import Board


def monster_ability_get_card_to_survive(board: Board, player: Player) -> Optional[Card]:
    """Keep random card on board"""
    if player.faction is Faction.MONSTER:
        cards = board.cards[player.id].get_all_cards()
        if cards:
            return random.choice(cards)
    return None
