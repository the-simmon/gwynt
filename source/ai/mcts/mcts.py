import time
from typing import Tuple, Optional, Union

from source.ai.mcts.node import Node, PlayerType
from source.core.card import Card, LeaderCard
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class MCTS:

    def __init__(self, environment: GameEnvironment, player: Player, max_time=5):
        self.environment = environment
        self.player = player
        self.max_time = max_time
        self.start_time = None
        enemy = self.environment.board.get_enemy_player(player)
        self.node = Node(environment, None, PlayerType.ENEMY, enemy, None, None)

    def run(self) -> Tuple[Union[Card, LeaderCard], CombatRow, Optional[Card]]:
        self.start_time = time.time()
        while time.time() - self.start_time < self.max_time:
            self.node.select()

        max_simulations = 0
        best_card: Card = None
        row: CombatRow = None

        # for decoys
        replaced_card: Card = None
        for node in self.node.leafs:
            if node.simulations > max_simulations:
                max_simulations = node.simulations
                best_card = node.card
                row = node.row
                replaced_card = node.replaced_card

        return best_card, row, replaced_card
