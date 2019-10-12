from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List, TYPE_CHECKING

from .card import CombatRow, Card, Ability
from .cardcollection import CardCollection
from .player import Player
from .weather import Weather

if TYPE_CHECKING:
    from ..ai.abstract_ai import AbstractAI
    from .gameenvironment import GameEnvironment


class Board:

    def __init__(self, player1: Player, player2: Player, ai: AbstractAI, environment: GameEnvironment):
        self.cards: DefaultDict[Player, CardCollection] = defaultdict(lambda: CardCollection(max_cards=22, cards=[]))
        self.weather: Weather = Weather.CLEAR
        self.player1 = player1
        self.player2 = player2
        self.ai = ai
        self.environment = environment

    def get_enemy_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player2
        return self.player1

    def add(self, player: Player, row: CombatRow, card: Card):
        if row is not CombatRow.SPECIAL:
            if card.ability is Ability.SPY:
                enemy = self.get_enemy_player(player)
                self.cards[enemy].add(row, card)
            else:
                self.cards[player].add(row, card)

        self._check_ability(player, card)

    def remove(self, player: Player, row: CombatRow, card: Card):
        self.cards[player].remove(row, card)
        player.graveyard.add(card.combat_row, card)

    def calculate_damage(self, player: Player) -> int:
        return self.cards[player].calculate_damage(self.weather)

    def all_cards_to_graveyard(self, player: Player):
        for row, cards in self.cards[player].items():
            for card in deepcopy(cards):
                self.remove(player, row, card)

    def repr_list(self, player: Player, excluded_card: Card):
        enemy = self.get_enemy_player(player)
        return [len(enemy.active_cards)] + enemy.repr_list() + player.repr_list(include_deck_and_active=True,
                                                                                exclude_card=excluded_card) + \
               self.cards[enemy].repr_list() + self.cards[player].repr_list() + self.weather.one_hot()

    def _check_ability(self, player: Player, card: Card):
        ability = card.ability

        if ability is Ability.NONE:
            pass
        elif Weather.ability_is_weather(ability):
            self.weather = Weather.ability_to_weather(ability)
        elif ability is Ability.MEDIC:
            card, row = self.ai.choose_revive(self.environment, player)
            self.add(player, row, card)
        elif ability is Ability.MUSTER:
            self._check_muster(player, card)
        elif ability is Ability.SPY:
            player.pick_random_from_deck()
            player.pick_random_from_deck()
        elif ability is Ability.SCORCH:
            self._check_scorch(card, player)

    def _check_muster(self, player: Player, card: Card):

        def search_and_remove(muster_card: Card, card_collection: CardCollection) -> List[Card]:
            result = []
            for current_card in card_collection.get_all_cards():
                if current_card.muster is muster_card.muster:
                    result.append(current_card)
                    card_collection.remove(current_card.combat_row, current_card)
            return result

        cards_to_add = search_and_remove(card, player.active_cards)
        cards_to_add.extend(search_and_remove(card, player.deck))

        for card in cards_to_add:
            self.add(player, card.combat_row, card)

    def _check_scorch(self, card: Card, player: Player):
        enemy = self.get_enemy_player(player)
        if card.combat_row is CombatRow.SPECIAL:
            self._scorch_special()
        else:
            enemy_damage = self.cards[enemy].calculate_damage_for_row(card.combat_row, self.weather)
            if enemy_damage > 10:
                self._scorch_highest_cards(enemy, card.combat_row)

    def _scorch_highest_cards(self, player: Player, selected_row: CombatRow):
        damage = _get_highest_index_and_damage(self.cards[player].get_damage_adjusted_cards(selected_row, self.weather))

        for card in self.cards[player][selected_row]:
            if card.damage == damage:
                self.remove(player, selected_row, card)

    def _scorch_special(self):
        max_damage = 0
        for player in [self.player1, self.player2]:
            for row in self.cards[player].keys():
                damage = _get_highest_index_and_damage(self.cards[player].get_damage_adjusted_cards(row, self.weather))
                if damage > max_damage:
                    max_damage = damage
        self._scorch_by_damage(max_damage)

    def _scorch_by_damage(self, scorch_damage):
        for player in [self.player1, self.player2]:
            for row in self.cards[player].keys():
                cards_to_remove = []
                for index, card in enumerate(self.cards[player].get_damage_adjusted_cards(row, self.weather)):
                    if card.damage is scorch_damage and not card.hero:
                        card_to_remove = self.cards[player][row][index]
                        cards_to_remove.append(card_to_remove)
                for card_to_remove in cards_to_remove:
                    self.remove(player, row, card_to_remove)

    def __str__(self):
        result = ''
        for player in self.cards.keys():
            result += self._str_for_player(player)
            result += '\n\n=====================\n\n'
        return result

    def _str_for_player(self, player: Player):
        result = ''
        for row, cards in self.cards[player].items():
            result += '{} {}: '.format(row.name, self.cards[player].calculate_damage_for_row(row))
            for card in cards:
                result += '({}) '.format(str(card))
            result += '\n'
        return result


def _get_highest_index_and_damage(cards: List[Card]) -> int:
    max_damage = 0
    for i, card in enumerate(cards):
        if card.damage > max_damage and not card.hero:
            max_damage = card.damage
    return max_damage
