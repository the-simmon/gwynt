from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List, TYPE_CHECKING

from source.core.comabt_row import CombatRow
from .card import Card, Ability
from .cardcollection import CardCollection
from .player import Player
from .weather import Weather

if TYPE_CHECKING:
    from .gameenvironment import GameEnvironment


class Board:

    def __init__(self, player1: Player, player2: Player, environment: GameEnvironment):
        self.cards: DefaultDict[int, CardCollection] = defaultdict(lambda: CardCollection(cards=[]))
        self.weather: List[Weather] = [Weather.CLEAR]
        self.player1 = player1
        self.player2 = player2
        self.environment = environment

    def get_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player1
        return self.player2

    def get_enemy_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player2
        return self.player1

    def add(self, player: Player, row: CombatRow, card: Card):
        if row is not CombatRow.SPECIAL:
            if card.ability is Ability.SPY:
                enemy = self.get_enemy_player(player)
                self.cards[enemy.id].add(row, card)
            else:
                self.cards[player.id].add(row, card)

        self._check_ability(player, card)

    def remove(self, player: Player, row: CombatRow, card: Card):
        self.cards[player.id].remove(row, card)
        player.graveyard.add(card.combat_row, card)

    def calculate_damage(self, player: Player) -> int:
        return self.cards[player.id].calculate_damage(self.weather)

    def all_cards_to_graveyard(self, player: Player):
        for row, cards in self.cards[player.id].items():
            for card in deepcopy(cards):
                self.remove(player, row, card)

        # remove cards that cannot be revived
        for cards in player.graveyard.values():
            for card in cards:
                if card.hero or card.combat_row is CombatRow.SPECIAL:
                    cards.remove(card)

    def check_commanders_horn(self, player: Player, horn_card: Card, row: CombatRow) -> bool:
        row_possible = True
        if horn_card.ability is Ability.SPECIAL_COMMANDERS_HORN or horn_card.ability is Ability.COMMANDERS_HORN:
            for card in self.cards[player.id][row]:
                if card.ability is horn_card.ability:
                    row_possible = False
                    break
        return row_possible

    def _check_ability(self, player: Player, card: Card):
        ability = card.ability

        if ability is Ability.NONE:
            pass
        elif Weather.ability_is_weather(ability):
            if Weather.CLEAR in self.weather:
                self.weather.remove(Weather.CLEAR)
            self.weather.append(Weather.ability_to_weather(ability))
        elif ability is Ability.MEDIC:
            pass  # reviving is handled on environment level
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
            self.cards[player.id][card.combat_row].append(card)

    def _check_scorch(self, card: Card, player: Player):
        enemy = self.get_enemy_player(player)
        if card.combat_row is CombatRow.SPECIAL:
            self._scorch_special()
        else:
            enemy_damage = self.cards[enemy.id].calculate_damage_for_row(card.combat_row, self.weather)
            if enemy_damage > 10:
                self._scorch_highest_cards(enemy, card.combat_row)

    def _scorch_highest_cards(self, player: Player, selected_row: CombatRow):
        damage = _get_highest_index_and_damage(
            self.cards[player.id].get_damage_adjusted_cards(selected_row, self.weather))

        for card in self.cards[player.id][selected_row]:
            if card.damage == damage:
                self.remove(player, selected_row, card)

    def _scorch_special(self):
        max_damage = 0
        for player in [self.player1, self.player2]:
            for row in self.cards[player.id].keys():
                damage = _get_highest_index_and_damage(
                    self.cards[player.id].get_damage_adjusted_cards(row, self.weather))
                if damage > max_damage:
                    max_damage = damage
        self._scorch_by_damage(max_damage)

    def _scorch_by_damage(self, scorch_damage):
        for player in [self.player1, self.player2]:
            for row in self.cards[player.id].keys():
                cards_to_remove = []
                for index, card in enumerate(self.cards[player.id].get_damage_adjusted_cards(row, self.weather)):
                    if card.damage is scorch_damage and not card.hero:
                        card_to_remove = self.cards[player.id][row][index]
                        cards_to_remove.append(card_to_remove)
                for card_to_remove in cards_to_remove:
                    self.remove(player, row, card_to_remove)


def _get_highest_index_and_damage(cards: List[Card]) -> int:
    max_damage = 0
    for i, card in enumerate(cards):
        if card.damage > max_damage and not card.hero:
            max_damage = card.damage
    return max_damage
