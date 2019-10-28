import random
from typing import List

from source.core.card import CombatRow, Card
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment, current_player: Player) -> Player:
    game_over = False
    while not game_over:
        potential_cards = _get_potential_cards(current_player)
        potential_cards.append(None)  # None == pass

        random_card = random.choice(potential_cards)
        row = random.choice(CombatRow.get_possible_rows(random_card.combat_row))
        game_over, current_player, card_source = environment.step(current_player, row, random_card)

    board = environment.board
    winner = board.player1 if board.player1.rounds_won is 2 else board.player2
    return winner


def _get_potential_cards(player: Player) -> List[Card]:
    return player.active_cards.get_all_cards()
