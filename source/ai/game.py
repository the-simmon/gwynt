import random
from typing import Tuple

from source.ai.mcts.mcts import MCTS
from source.core.card import CombatRow, Card
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class Game:

    def __init__(self, player: Player, enemy: Player):
        self.player = player
        self.enemy = enemy
        self.environment = GameEnvironment(player, enemy, _revive)
        self.game_over = False
        self.current_player = player

    def calculate_step(self) -> Tuple[Card, CombatRow]:
        mcts = MCTS(self.environment, self.current_player)
        card, row = mcts.run()
        _, self.game_over = self.environment.step(self.current_player, row, card)
        self.current_player = self.get_current_player()
        return card, row

    def get_current_player(self) -> Player:
        return self.environment.board.get_enemy_player(self.current_player)


def _revive(environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
    if player.graveyard.get_all_cards():
        card = random.choice(player.graveyard.get_all_cards())
        row = random.choice(CombatRow.get_possible_rows(card.combat_row))
    else:
        card, row = None, None
    return card, row
