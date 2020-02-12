from __future__ import annotations

import random
from operator import xor
from tkinter import messagebox
from typing import Optional, TYPE_CHECKING, List

from source.core.card import Card, Ability, LeaderCard
from source.core.comabt_row import CombatRow
from source.core.player import Faction, Player

if TYPE_CHECKING:
    from source.core.board import Board
    from source.core.gameenvironment import GameEnvironment


def monster_ability_get_card_to_survive(board: Board, player: Player) -> Optional[Card]:
    """Keep random card on board"""
    if player.faction is Faction.MONSTER:
        cards = board.cards[player.id].get_all_cards()
        cards = _filter_cards(cards)

        if cards:
            return random.choice(cards)
    return None


def _filter_cards(cards: List[Card]) -> List[Card]:
    result = []
    for card in cards:
        if card.ability is not Ability.DECOY and not card.hero or card.combat_row is CombatRow.SPECIAL or \
                type(card) is LeaderCard:
            result.append(card)
    return result


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


def scoiatael_decide_starting_player(environment: GameEnvironment) -> Player:
    if environment.player1.faction is Faction.SCOIATAEL:
        wants_to_start = messagebox.askyesno('Scoia´tael faction ability', 'Would you like to lay the first card?')
        result = environment.player1 if wants_to_start else environment.player2
    else:
        result = random.choice([environment.player1, environment.player2])
    return result
