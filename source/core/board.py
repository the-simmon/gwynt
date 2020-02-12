from __future__ import annotations

import operator
from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List, Dict

from source.core.card import Card, Ability, LeaderAbility
from source.core.cardcollection import CardCollection
from source.core.comabt_row import CombatRow
from source.core.faction_abililty import monster_ability_get_card_to_survive
from source.core.player import Player
from source.core.weather import Weather


class Board:

    def __init__(self, player1: Player, player2: Player, passive_leaders: List[LeaderAbility]):
        self.cards: DefaultDict[int, CardCollection] = defaultdict(lambda: CardCollection(cards=[]))
        self.weather: List[Weather] = [Weather.CLEAR]
        self.player1 = player1
        self.player2 = player2
        self.passive_leaders = passive_leaders

    def get_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player1
        return self.player2

    def get_enemy_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player2
        return self.player1

    def add(self, player: Player, row: CombatRow, card: Card):
        if row is not CombatRow.NONE:
            if card.ability is Ability.SPY:
                enemy = self.get_enemy_player(player)
                self.cards[enemy.id].add(row, card)
            else:
                self.cards[player.id].add(row, card)

        self._check_ability(player, card)

    def remove(self, player: Player, row: CombatRow, card: Card, ignore_graveyard: bool = False):
        self.cards[player.id].remove(row, card)
        if not ignore_graveyard:
            player.graveyard.add(card.combat_row, card)

    def calculate_damage(self, player: Player) -> int:
        return self.cards[player.id].calculate_damage(self.weather, self.passive_leaders)

    def all_cards_to_graveyard(self, player: Player):
        # monster faction ability
        card_to_keep = monster_ability_get_card_to_survive(self, player)

        for row, cards in self.cards[player.id].items():
            for card in deepcopy(cards):
                if card != card_to_keep:
                    self.remove(player, row, card)

        # remove cards that cannot be revived
        for cards in player.graveyard.values():
            for card in cards:
                if card.hero or card.combat_row is CombatRow.SPECIAL or card.combat_row is CombatRow.NONE:
                    cards.remove(card)

    def check_commanders_horn(self, player: Player, horn_card: Card, row: CombatRow) -> bool:
        row_possible = True
        if horn_card.ability is Ability.SPECIAL_COMMANDERS_HORN or horn_card.ability is Ability.COMMANDERS_HORN:
            for card in self.cards[player.id][row]:
                if card.ability is horn_card.ability:
                    row_possible = False
                    break
        return row_possible

    def agile_to_best_row_leader(self, player: Player):
        def extract_and_remove_agile_cards(card_collection: CardCollection) -> List[Card]:
            agile_cards: List[Card] = []
            for row in CombatRow.get_possible_rows(CombatRow.AGILE):
                for card in card_collection[row]:
                    if card.combat_row is CombatRow.AGILE and not card.hero:
                        agile_cards.append(card)
                        card_collection.remove(row, card)
            return agile_cards

        damage_per_row: Dict[CombatRow, int] = {}
        card_collection = deepcopy(self.cards[player.id])
        agile_cards = extract_and_remove_agile_cards(card_collection)

        for row in CombatRow.get_possible_rows(CombatRow.AGILE):
            copy_card_collection = deepcopy(card_collection)
            for card in agile_cards:
                copy_card_collection.add(row, card)
            damage_per_row[row] = copy_card_collection.calculate_damage(self.weather, self.passive_leaders)

        best_row = max(damage_per_row.items(), key=operator.itemgetter(1))[0]
        for card in agile_cards:
            card_collection.add(best_row, card)
        self.cards[player.id] = card_collection

    def _check_ability(self, player: Player, card: Card):
        ability = card.ability

        if ability is Ability.NONE:
            pass
        elif Weather.ability_is_weather(ability):
            if Weather.CLEAR in self.weather:
                self.weather.remove(Weather.CLEAR)
            if ability is Ability.CLEAR_WEATHER:
                self.weather.clear()
            if Weather.ability_to_weather(ability) not in self.weather:
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

        cards_to_add = search_and_remove(card, player.hand)
        cards_to_add.extend(search_and_remove(card, player.deck))

        for card in cards_to_add:
            self.cards[player.id][card.combat_row].append(card)

    def _check_scorch(self, card: Card, player: Player):
        enemy = self.get_enemy_player(player)
        if card.combat_row is CombatRow.NONE:
            self._scorch_special()
        else:
            enemy_damage = self.cards[enemy.id].calculate_damage_for_row(card.combat_row, self.weather,
                                                                         self.passive_leaders)
            if enemy_damage > 10:
                self._scorch_highest_cards(enemy, card.combat_row)

    def _scorch_highest_cards(self, player: Player, selected_row: CombatRow):
        damage = _get_highest_index_and_damage(
            self.cards[player.id].get_damage_adjusted_cards(selected_row, self.weather, self.passive_leaders))

        for card in list(self.cards[player.id][selected_row]):
            if card.damage == damage:
                self.remove(player, selected_row, card)

    def _scorch_special(self):
        max_damage = 0
        for player in [self.player1, self.player2]:
            for row in self.cards[player.id].keys():
                damage = _get_highest_index_and_damage(
                    self.cards[player.id].get_damage_adjusted_cards(row, self.weather, self.passive_leaders))
                if damage > max_damage:
                    max_damage = damage
        self._scorch_by_damage(max_damage)

    def _scorch_by_damage(self, scorch_damage):
        for player in [self.player1, self.player2]:
            for row in self.cards[player.id].keys():
                cards_to_remove = []
                for index, card in enumerate(
                        self.cards[player.id].get_damage_adjusted_cards(row, self.weather, self.passive_leaders)):
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
