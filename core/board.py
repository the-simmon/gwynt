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
    def ability_to_weather(cls, ability: Ability) -> Weather:
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

    def __init__(self):
        self.cards: DefaultDict[Player, CardCollection] = defaultdict(CardCollection)
        self.weather: Weather = Weather.CLEAR

    def add(self, player: Player, row: CombatRow, card: Card, player2: Player = None):
        if player2:
            self.cards[player2].add(row, card)
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
            self.add(card)

