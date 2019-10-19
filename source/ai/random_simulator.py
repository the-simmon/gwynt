from typing import List

from source.ai.mcts.node import PlayerType
import random

from source.core.card import CombatRow, Card
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment, current_player: Player) -> Player:
    game_over = False
    while not game_over:
        round_over = False
        pass_ = False
        potential_cards = _get_potential_cards(current_player)
        if potential_cards:
            random_card = random.choice(_get_potential_cards(current_player))
            row = random.choice(CombatRow.get_possible_rows(random_card.combat_row))
        else:
            random_card, row = None, None
            pass_ = True
        round_over, game_over = environment.step(current_player, row, random_card, pass_)
        current_player = environment.board.get_enemy_player(current_player)

    board = environment.board
    winner = board.player1 if board.player1.rounds_won is 2 else board.player2
    return winner


def _get_potential_cards(player: Player) -> List[Card]:
    return player.active_cards.get_all_cards()
