from __future__ import annotations

import math
import random
import sys
from copy import deepcopy
from enum import Enum
from math import sqrt
from typing import List

from source.core.card import Card, Ability, CombatRow
from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class PlayerType(Enum):
    SELF = 0
    ENEMEY = 0

    def invert(self):
        if self.value is PlayerType.SELF:
            return PlayerType.ENEMEY
        return PlayerType.SELF


class Node:

    def __init__(self, environment: GameEnvironment, parent: Node, player_type: PlayerType, player: Player, card: Card,
                 row: CombatRow):
        self.environment = environment
        self.board = environment.board
        self.parent = parent
        self.player_type = player_type
        self.player = player
        self.card = card
        self.row = row
        self.leafs: List[Node] = []
        self.simulations = 0
        self.wins = 0

    def select(self):
        if self.leafs:
            max_index = 0
            max_value = 0
            for i, node in enumerate(self.leafs):
                value = node.get_ucb1()
                if value > max_value:
                    max_value = value
                    max_index = i

            self.leafs[max_index].select()
        else:
            if self.simulations is 0:
                self.simulate()
            else:
                self.expand()
                self.select()

    def get_ucb1(self):
        simulations = self.simulations or sys.float_info.epsilon * 10
        return self.wins / simulations + sqrt(math.log(self.parent.simulations) / simulations)

    def expand(self):
        potential_cards = self._get_potential_cards(self.player)

        for card in potential_cards:
            for row in card.combat_row.get_possible_rows(card.combat_row):
                environment_copy = deepcopy(self.environment)
                environment_copy.board.add(self.player, row, card)

                enemy = environment_copy.board.get_enemy_player(self.player)
                node = Node(environment_copy, self, deepcopy(self.player_type.invert()), enemy, card, row)
                if card.ability is Ability.MEDIC:
                    self._expand_medic(node)
                self.leafs.append(node)

    def _get_potential_cards(self, player: Player) -> List[Card]:
        return player.active_cards.get_all_cards()

    def _expand_medic(self, node: Node):
        for card in self.player.graveyard.get_all_cards():
            for row in CombatRow.get_possible_rows(card.combat_row):
                environment_copy = deepcopy(self.environment)
                environment_copy.board.add(self.player, row, card)
                node.leafs.append(
                    Node(environment_copy, node, deepcopy(self.player_type),
                         environment_copy.board.get_enemy_player(self.player),
                         card, row))

    def simulate(self):
        environment_copy = deepcopy(self.environment)
        current_player = deepcopy(self.player)
        current_player_type = deepcopy(self.player_type)

        game_over = False
        while not game_over:
            pass_ = False
            potential_cards = self._get_potential_cards(current_player)
            if potential_cards:
                random_card = random.choice(self._get_potential_cards(current_player))
                row = random.choice(CombatRow.get_possible_rows(random_card.combat_row))
            else:
                random_card, row = None, None
                pass_ = True
            game_over, _ = environment_copy.step(current_player, row, random_card, pass_)

            current_player = environment_copy.board.get_enemy_player(current_player)
            current_player_type = current_player_type.invert()

        if current_player.rounds_won is not 2:
            current_player_type = current_player_type.invert()
        self.backpropagate(current_player_type)

    def backpropagate(self, winner: PlayerType):
        self.simulations += 1
        if winner is self.player_type:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(winner)
