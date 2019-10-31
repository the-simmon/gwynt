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
        self.environment = GameEnvironment(player, enemy)
        self.game_over = False
        self.current_player = player

    def calculate_step(self) -> Tuple[Card, CombatRow]:
        mcts = MCTS(self.environment, self.current_player)
        card, row = mcts.run()
        self.game_over, self.current_player, card_source = self.environment.step(self.current_player, row, card)
        return card, row
