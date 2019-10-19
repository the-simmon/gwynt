from __future__ import annotations

import math
import random
import sys
from copy import deepcopy
from enum import Enum
from math import sqrt
from typing import List

from source.ai.random_simulator import simulate_random_game
from source.core.card import Card, Ability, CombatRow
from source.core.cardcollection import CardCollection
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
        current_player = environment_copy.board.get_player(self.player)
        self._add_random_cards_to_enemy(environment_copy)

        winner = simulate_random_game(environment_copy, current_player)

        winning_type = PlayerType.SELF
        if winner.id is not self.player.id:
            winning_type = PlayerType.ENEMEY

        self.backpropagate(winning_type)

    def _add_random_cards_to_enemy(self, environment: GameEnvironment):
        player_to_add_cards = self.player
        if self.player_type is PlayerType.ENEMEY:
            player_to_add_cards = environment.board.get_enemy_player(self.player)

        all_cards = get_cards(player_to_add_cards.faction)
        played_cards = environment.board.cards[player_to_add_cards].get_all_cards()
        played_cards.extend(player_to_add_cards.graveyard.get_all_cards())
        for card in played_cards:
            if card in all_cards:
                all_cards.remove(card)
        random.shuffle(all_cards)

        number_of_played_cards = len(environment.board.cards[player_to_add_cards].get_all_cards())
        player_to_add_cards.active_cards = CardCollection(22, all_cards[:10 - number_of_played_cards])
        player_to_add_cards.deck = CardCollection(22, all_cards[11:])

    def backpropagate(self, winner: PlayerType):
        self.simulations += 1
        if winner is self.player_type:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(winner)
