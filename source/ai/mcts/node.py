from __future__ import annotations

import math
import random
import sys
from copy import deepcopy
from enum import Enum
from typing import List, Optional

from source.ai.random_simulator import simulate_random_game
from source.core.card import Card, Ability
from source.core.cardcollection import CardCollection
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


class PlayerType(Enum):
    SELF = 0
    ENEMY = 1

    def invert(self):
        if self is PlayerType.SELF:
            return PlayerType.ENEMY
        return PlayerType.SELF


class Node:
    ADD_HALF = False

    def __init__(self, environment: GameEnvironment, parent: Node, player_type: PlayerType, current_player: Player,
                 card: Card, row: CombatRow, replaced_card: Optional[Card] = None):
        self.environment = environment
        self.parent = parent
        self.current_player = current_player
        self.current_player_type = player_type
        self.next_player_type = self._get_next_player_type(self.environment.next_player)
        self.next_player = self.environment.next_player
        self.card = card
        self.row = row
        # if the node represents a decoy, it must contain the replaced card
        self.replaced_card = replaced_card

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
            if self.simulations == 0:
                self.simulate()
            else:
                if self.environment.game_over():
                    self.simulate()
                else:
                    self.expand()
                    self.select()

    def get_ucb1(self):
        simulations = self.simulations or sys.float_info.epsilon * 10
        return self.wins / simulations + 1.414 * math.sqrt(math.log(self.parent.simulations) / simulations)

    def expand(self):
        self.expanded = True

        self._add_pass_node()
        self._add_leader_node()

        potential_cards = self._get_potential_cards()
        for card in potential_cards:
            if card.ability is Ability.DECOY and self.environment.next_card_source is CardSource.HAND:
                self._add_decoys(card)
            else:
                for row in card.combat_row.get_possible_rows(card):
                    # only one commanders horn per row is possible
                    if self.environment.board.check_commanders_horn(self.next_player, card, row):
                        environment_copy = deepcopy(self.environment)
                        player_copy = environment_copy.board.get_player(self.next_player)

                        # enemy player gets all possible cards assigned
                        # for technical reasons, the card has to be added to the player
                        # (active cards will be overwritten in next node/ random simulation)
                        if self.next_player_type is PlayerType.ENEMY:
                            environment_copy.add_card_to_source(player_copy, card)

                        environment_copy.step(player_copy, row, card)

                        node = Node(environment_copy, self, self.next_player_type, self.next_player, card, row)
                        self.leafs.append(node)

    def _get_potential_cards(self) -> List[Card]:
        obfuscate = self.next_player_type is PlayerType.ENEMY
        cards = self.environment.card_tracker.get_possible_cards(obfuscate)
        if Node.ADD_HALF and self.next_player_type is PlayerType.ENEMY:
            random.shuffle(cards)
            cards = cards[:round(len(cards) / 2)]
        return cards

    def _get_next_player_type(self, next_player: Player) -> PlayerType:
        player_type = deepcopy(self.current_player_type)
        if next_player.id != self.current_player.id:
            player_type = deepcopy(self.current_player_type.invert())
        return player_type

    def _add_pass_node(self):
        environment_copy = deepcopy(self.environment)
        player_copy = environment_copy.board.get_player(self.next_player)
        environment_copy.step(player_copy, None, None)

        node = Node(environment_copy, self, self.next_player_type, self.next_player, None, None)
        self.leafs.append(node)

    def _add_decoys(self, decoy: Card):
        for row, card_list in self.environment.board.cards[self.next_player.id].items():
            for card in card_list:
                if card.ability is not Ability.DECOY and card.ability is not Ability.SPECIAL_COMMANDERS_HORN and not card.hero:
                    environment_copy = deepcopy(self.environment)
                    player_copy = environment_copy.board.get_player(self.next_player)

                    # for technical reasons, the card has to be added to the player
                    if self.next_player_type is PlayerType.ENEMY:
                        player_copy.hand.add(decoy.combat_row, decoy)

                    environment_copy.step_decoy(player_copy, row, decoy, card)

                    node = Node(environment_copy, self, self.next_player_type, self.next_player, decoy, row, card)
                    self.leafs.append(node)

    def _add_leader_node(self):
        if self.next_player.leader:
            environment_copy = deepcopy(self.environment)
            player_copy = environment_copy.board.get_player(self.next_player)
            leader = player_copy.leader
            environment_copy.step_leader(player_copy, leader)
            node = Node(environment_copy, self, self.next_player_type, self.next_player, leader, None, None)
            self.leafs.append(node)

    def simulate(self):
        environment_copy = deepcopy(self.environment)

        if self.next_player_type is PlayerType.SELF:
            player_to_add_cards = environment_copy.board.get_enemy_player(self.next_player)
        else:
            player_to_add_cards = environment_copy.board.get_player(self.next_player)

        self._add_random_cards_to_enemy(player_to_add_cards)
        winner = simulate_random_game(environment_copy)

        self.backpropagate(winner)

    def _add_random_cards_to_enemy(self, player_to_add_cards: Player):
        all_cards = self.environment.card_tracker.get_possible_cards(True)
        total_hand = len(player_to_add_cards.hand.get_all_cards())
        random.shuffle(all_cards)

        player_to_add_cards.hand = CardCollection(all_cards[:total_hand + 1])
        player_to_add_cards.deck = CardCollection(all_cards[total_hand + 1:])

    def backpropagate(self, winner: Player):
        self.simulations += 1
        if winner and winner.id is self.current_player.id:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(winner)
