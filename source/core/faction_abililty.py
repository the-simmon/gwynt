from __future__ import annotations

import random
from operator import xor
from typing import Optional, TYPE_CHECKING

from source.core.card import Card
from source.core.player import Faction, Player

if TYPE_CHECKING:
    from source.core.board import Board
    from source.core.gameenvironment import GameEnvironment


def monster_ability_get_card_to_survive(board: Board, player: Player) -> Optional[Card]:
    """Keep random card on board"""
    if player.faction is Faction.MONSTER:
        cards = board.cards[player.id].get_all_cards()
        if cards:
            return random.choice(cards)
    return None


def nilfgaard_check_draw(environment: GameEnvironment):
    """Nilfgaard wins draw"""
    player1 = environment.player1
    player2 = environment.player2

    if xor(player1.faction is Faction.NILFGAARD, player2.faction is Faction.NILFGAARD):
        if player1.faction is Faction.NILFGAARD:
            player1.rounds_won += 1
        else:
            player2.rounds_won += 1
    else:
        player1.rounds_won += 1
        player2.rounds_won += 1


def northern_realms_check_extra_card(player: Player):
    """Nothern Reamls gets an extra card when winning a round"""
    if player.faction is Faction.NOTHERN_REALMS:
        player.pick_random_from_deck()
