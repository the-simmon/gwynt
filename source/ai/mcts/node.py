from __future__ import annotations

import math
import random
import sys
from copy import deepcopy
from enum import Enum
from math import sqrt
from typing import List

from source.ai.random_simulator import simulate_random_game
from source.core.card import Card, Ability
from source.core.cardcollection import CardCollection
from source.core.cards.util import get_cards
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


class PlayerType(Enum):
    SELF = 0
    ENEMY = 1

    def invert(self):
        if self.value is PlayerType.SELF:
            return PlayerType.ENEMY
        return PlayerType.SELF


class Node:

    def __init__(self, environment: GameEnvironment, parent: Node, player_type: PlayerType, player: Player, card: Card,
                 row: CombatRow, card_source: CardSource):
        self.environment = environment
        self.parent = parent
        self.player_type = player_type
        self.next_player = player
        self.card = card
        self.row = row
        self.next_card_source = card_source
        self.leafs: List[Node] = []
        self.simulations = 0
        self.wins = 0
        self.expanded = False

    def select(self):
        if self.expanded:
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
        return self.wins / simulations + 2 * sqrt(math.log(self.parent.simulations) / simulations)

    def expand(self):
        self.expanded = True
        potential_cards = self._get_potential_cards()

        for card in potential_cards:
            for row in card.combat_row.get_possible_rows(card):
                # only one commanders horn per row is possible
                if self.environment.board.check_commanders_horn(self.next_player, card, row):
                    environment_copy = deepcopy(self.environment)
                    player_copy = environment_copy.board.get_player(self.next_player)
                    game_over, next_player, card_source = environment_copy.step(player_copy, row, card)

                    player_type = self._get_next_player_type(next_player)
                    node = Node(environment_copy, self, player_type, next_player, card, row,
                                deepcopy(card_source))
                    self.leafs.append(node)

        game_over = self.environment.game_over()
        if not game_over and not self.environment.passed[self.next_player.id] \
                and self.next_card_source is CardSource.HAND:
            self._add_pass_node()

    def _get_potential_cards(self) -> List[Card]:
        if self.player_type is PlayerType.SELF:
            player = self.next_player
        else:
            player = deepcopy(self.next_player)
            self._add_random_cards_to_enemy(self.environment, player)

        if self.next_card_source is CardSource.HAND:
            return player.active_cards.get_all_cards()
        return player.graveyard.get_all_cards()

    def _get_next_player_type(self, next_player: Player) -> PlayerType:
        player_type = deepcopy(self.player_type)
        if next_player.id is not self.next_player.id:
            player_type = deepcopy(self.player_type.invert())
        return player_type

    def _add_pass_node(self):
        environment_copy = deepcopy(self.environment)
        player_copy = environment_copy.board.get_player(self.next_player)
        game_over, next_player, card_source = environment_copy.step(player_copy, None, None)

        player_type = self._get_next_player_type(next_player)
        node = Node(environment_copy, self, player_type, next_player, None, None, deepcopy(card_source))
        self.leafs.append(node)

    def simulate(self):
        environment_copy = deepcopy(self.environment)
        current_player = environment_copy.current_player

        if self.player_type is PlayerType.SELF:
            player_to_add_cards = environment_copy.board.get_enemy_player(self.next_player)
        else:
            player_to_add_cards = environment_copy.board.get_player(self.next_player)

        self._add_random_cards_to_enemy(environment_copy, player_to_add_cards)
        winner = simulate_random_game(environment_copy, current_player, environment_copy.current_card_source)

        self.backpropagate(winner)

    def _add_random_cards_to_enemy(self, environment: GameEnvironment, player_to_add_cards: Player):
        all_cards = get_cards(player_to_add_cards.faction)
        played_cards = environment.board.cards[player_to_add_cards].get_all_cards()
        played_cards.extend(player_to_add_cards.graveyard.get_all_cards())

        total_active_cards = 10
        for card in played_cards:
            if card in all_cards and card.ability is not Ability.SPY:
                all_cards.remove(card)
                total_active_cards -= 1

        # spy cards are placed on the enemy side
        enemy = environment.board.get_enemy_player(player_to_add_cards)
        enemy_cards = environment.board.cards[enemy].get_all_cards()
        for card in enemy_cards:
            if card in all_cards and card.ability is Ability.SPY:
                total_active_cards += 2
        random.shuffle(all_cards)

        number_of_played_cards = len(environment.board.cards[player_to_add_cards].get_all_cards())
        player_to_add_cards.active_cards = CardCollection(all_cards[:total_active_cards - number_of_played_cards])
        player_to_add_cards.deck = CardCollection(all_cards[total_active_cards:])

    def backpropagate(self, winner: Player):
        self.simulations += 1

        # self.card was not laid by self.next_player (as it is the next player to lay a card)
        # if self.next_player wins, the enemy (relative to this node) won
        # except the previous card was a medic (hence the CardSource.GRAVEYARD)
        if winner and winner.id is not self.next_player.id and self.next_card_source is CardSource.HAND:
            self.wins += 1
        elif winner and winner.id is self.next_player.id and self.next_card_source is CardSource.GRAVEYARD:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(winner)
