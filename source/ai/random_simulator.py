import random
from typing import List

from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment, current_player: Player, card_source: CardSource) -> Player:
    game_over = False
    while not game_over:
        potential_cards = _get_potential_cards(current_player, card_source)
        potential_cards.append(None)  # None == pass

        random_card = random.choice(potential_cards)
        if random_card:
            row = random.choice(CombatRow.get_possible_rows(random_card.combat_row))
        else:
            row = None
        game_over, current_player, card_source = environment.step(current_player, row, random_card)

    board = environment.board
    winner = None
    if environment.player1.rounds_won is 2 and environment.player2.rounds_won is not 2:
        winner = environment.player1
    elif environment.player2.rounds_won is 2 and environment.player1.rounds_won is not 2:
        winner = environment.player2
    return winner


def _get_potential_cards(player: Player, next_card_source: CardSource) -> List[Card]:
    if next_card_source is CardSource.HAND:
        return player.active_cards.get_all_cards()
    return player.graveyard.get_all_cards()
