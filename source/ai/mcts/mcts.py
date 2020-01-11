import time
from collections import defaultdict
from typing import Tuple, List, Dict, Optional

from source.ai.mcts.node import Node, PlayerType
from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class MCTS:

    def __init__(self, environment: GameEnvironment, player: Player, card_source, max_time=5):
        self.environment = environment
        self.player = player
        self.max_time = max_time
        self.start_time = None
        self.node = Node(environment, None, PlayerType.ENEMY, player, None, None, card_source,
                         self._initialize_played_cards())

    def _initialize_played_cards(self) -> Dict[int, List[Card]]:
        result_dict = {}
        for player in [self.environment.player1, self.environment.player2]:
            result_list = []
            for card in self.environment.board.cards[player.id].values():
                result_list.extend(card)
            result_dict[player.id] = result_list
        return result_dict

    def run(self) -> Tuple[Card, CombatRow, Optional[Card]]:
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
