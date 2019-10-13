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
        return PlayerType.SELF if self.value is PlayerType.ENEMEY else PlayerType.ENEMEY


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
        simulations = self.simulations or sys.float_info.epislon
        return self.wins / simulations + sqrt(math.log(self.parent.simulations) / simulations)

    def expand(self):
        enemy = self.board.get_enemy_player(self.player)
        potential_cards = self._get_potential_cards(enemy)

        for card in potential_cards:
            for row in card.combat_row.get_possible_rows():
                environment_copy = deepcopy(self.environment)
                environment_copy.board.add(self.player, row, card)

                node = Node(environment_copy, self, self.player_type.invert(), enemy, card, row)
                if card.ability is Ability.MEDIC:
                    self._expand_medic(node)
                self.leafs.append(node)

    def _get_potential_cards(self, enemy: Player) -> List[Card]:
        if self.player_type is PlayerType.SELF:
            potential_cards = self.player.active_cards.get_all_cards()
        else:
            potential_cards = get_cards(enemy.faction)

            played_cards = self.board.cards[enemy].get_all_cards()
            played_cards.extend(enemy.graveyard.get_all_cards())

            for played_card in played_cards:
                potential_cards.remove(played_card)

        return potential_cards

    def _expand_medic(self, node: Node):
        for card in self.player.graveyard.get_all_cards():
            for row in CombatRow.get_possible_rows(card.combat_row):
                environment_copy = deepcopy(self.environment)
                environment_copy.board.add(self.player, row, card)
                node.leafs.append(
                    Node(environment_copy, node, self.player_type, self.board.get_enemy_player(self.player), card, row))

    def simulate(self):
        environment_copy = deepcopy(self.environment)
        current_player = self.player
        current_player_type = self.player_type

        while environment_copy.current_round is not 2:
            enemy = environment_copy.board.get_enemy_player(self.player)
            random_card = random.choice(self._get_potential_cards(enemy))
            row = random.choice(CombatRow.get_possible_rows(random_card.combat_row))
            environment_copy.board.add(current_player, row, random_card)

            current_player = enemy
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
