from collections import defaultdict
from typing import DefaultDict, List, Tuple

from .one_hot_enum import OneHotEnum
from .card import CombatRow, Card, Ability
from .cardcollection import CardCollection
from .player import Player


class Weather(OneHotEnum):
    CLEAR = 0
    FROST = 1
    FOG = 2
    RAIN = 3

    @classmethod
    def ability_is_weather(cls, ability: Ability):
        if ability is Ability.CLEAR_WEATHER or ability is Ability.FROST or ability is Ability.RAIN or \
                ability is Ability.FOG:
            return True
        return False

    @classmethod
    def ability_to_weather(cls, ability: Ability) -> OneHotEnum:
        if ability is Ability.CLEAR_WEATHER:
            return Weather.CLEAR
        elif ability is Ability.FROST:
            return Weather.FROST
        elif ability is Ability.FOG:
            return Weather.FOG
        elif ability is Ability.RAIN:
            return Weather.RAIN

        raise ValueError


class Board:

    def __init__(self, player1: Player, player2: Player):
        self.cards: DefaultDict[Player, CardCollection] = defaultdict(CardCollection)
        self.weather: Weather = Weather.CLEAR
        self.player1 = player1
        self.player2 = player2

    def _get_enemy_player(self, player: Player) -> Player:
        if player.id is self.player1.id:
            return self.player2
        return self.player1

    def add(self, player: Player, row: CombatRow, card: Card):
        if card.ability is Ability.SPY:
            enemy = self._get_enemy_player(player)
            self.cards[enemy].add(row, card)
        else:
            self.cards[player].add(row, card)

        self._check_ability(player, card)

    def remove(self, player: Player, row: CombatRow, card: Card):
        self.cards[player].remove(row, card)

    def _check_ability(self, player: Player, card: Card):
        ability = card.ability

        if ability is Ability.NONE:
            pass
        elif Weather.ability_is_weather(ability):
            self.weather = Weather.ability_to_weather(ability)
        elif ability is Ability.MEDIC:
            raise NotImplementedError
        elif ability is Ability.MUSTER:
            self._check_muster(player, card)
        elif ability is Ability.SPY:
            player.pick_random_from_deck()
        elif ability is Ability.SCORCH:
            self._check_scorch(card, player)

    def _check_muster(self, player: Player, card: Card):

        def search_and_remove(muster_card: Card, card_collection: CardCollection) -> List[Card]:
            result = []
            for cards in card_collection.cards.values():
                for current_card in cards:
                    if current_card.muster is muster_card.muster:
                        result.append(current_card)
                        card_collection.remove(current_card)
            return result

        cards_to_add = search_and_remove(card, player.active_cards)
        cards_to_add.extend(search_and_remove(card, player.deck))

        for card in cards_to_add:
            self.add(player, card.combat_row, card)

    def _check_scorch(self, card: Card, player: Player):
        enemy = self._get_enemy_player(player)
        if card.combat_row is CombatRow.SPECIAL:
            self._scorch_special()
        else:
            enemy_damage = self.cards[enemy].calculate_damage_for_row(card.combat_row, self.weather)
            if enemy_damage > 10:
                self._scorch_highest_card(enemy, card.combat_row)

    def _scorch_highest_card(self, player: Player, selected_row: CombatRow):
        max_damage = 0
        max_row = None
        max_index = 0
        for row in self.cards[player].cards.keys():
            index, damage = _get_highest_index_and_damage(self.cards[player].get_damage_adjusted_cards(selected_row, self.weather))
            if damage > max_damage:
                max_damage = damage
                max_row = row
                max_index = index
        self.cards[player].cards[max_row].pop(max_index)

    def _scorch_special(self):
        max_damage = 0
        for player in [self.player1, self.player2]:
            for row in self.cards[player].cards.keys():
                _, damage = _get_highest_index_and_damage(self.cards[player].get_damage_adjusted_cards(row, self.weather))
                if damage > max_damage:
                    max_damage = damage
        self._scorch_by_damage(max_damage)

    def _scorch_by_damage(self, scorch_damage):
        for player in [self.player1, self.player2]:
            for row in self.cards[player].cards.keys():
                for index, card in enumerate(self.cards[player].get_damage_adjusted_cards(row, self.weather)):
                    if card.damage is scorch_damage and card.ability is not Ability.HERO:
                        self.cards[player].cards[row].pop(index)


def _get_highest_index_and_damage(cards: List[Card]) -> Tuple[int, int]:
    max_damage = 0
    index = 0

    for i, card in enumerate(cards):
        if card.damage > max_damage and card.ability is not Ability.HERO:
            max_damage = card.damage
            index = i
    return index, max_damage
