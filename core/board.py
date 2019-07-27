from collections import defaultdict
from typing import DefaultDict, List

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
        if ability is Ability.CLEAR_WEATHER or ability is Ability.FROST or ability is Ability.RAIN or ability is Ability.FOG:
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

    def _get_selected_player(self, player_id: int):
        if player_id is 0:
            return self.player1
        return self.player2

    def _get_enemy_player(self, player_id):
        if player_id is 0:
            return self.player2
        return self.player1

    def add(self, player_id: int, row: CombatRow, card: Card):
        player = self._get_selected_player(player_id)

        if card.ability is Ability.SPY:
            enemy = self._get_enemy_player(player_id)
            self.cards[enemy].add(row, card)
        else:
            self.cards[player].add(row, card)

        self._check_ability(player, card)

    def remove(self, player_id: int, row: CombatRow, card: Card):
        player = self._get_selected_player(player_id)
        self.cards[player].remove(row, card)

    def _check_ability(self, player: Player, card: Card) -> bool:
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
            raise NotImplementedError

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
            self._scorch_highest_card(enemy)
            self._scorch_highest_card(player)
        else:
            enemy_damage = self.cards[enemy].calculate_damage_for_row(card.combat_row, self.weather)
            if enemy_damage > 10:
                self._scorch_highest_card(enemy, card.combat_row)

    def _scorch_highest_card(self, player: Player, selected_row: CombatRow = None):
        max_damage = 0
        if selected_row:
            max_damage = max([card.damage for card in self.cards[player][selected_row]])
            self._remove_damage_from_row(player, selected_row, max_damage)
        else:
            max_row = None
            for row, cards in self.cards.items():
                damage = max([card.damage for card in self.cards[player][row]])
                if damage > max_damage:
                    max_damage = damage
                    max_row = row
            self._remove_damage_from_row(player, max_row, max_damage)

    def _remove_damage_from_row(self, player: Player, row: CombatRow, damage: int) -> List[Card]:
        return [card for card in self.cards[player][row] if card.damage is not damage]
