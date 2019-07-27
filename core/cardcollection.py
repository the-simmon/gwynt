from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List

from core import Ability
from core.board import Weather
from .card import CombatRow, Card


class CardCollection:

    def __init__(self, max_cards: int, cards: List[Card]):
        self.max_cards = max_cards
        self.cards: DefaultDict[CombatRow, List[Card]] = defaultdict(list)

        for card in cards:
            self.cards[card.combat_row].append(card)

    def add(self, row: CombatRow, card: Card):
        self.cards[row].append(card)

    def remove(self, row: CombatRow, card: Card):
        self.cards[row].remove(card)

    def repr_list(self) -> List[int]:
        result = []
        for row, cards in self.cards.items():
            result.extend(self._one_hot_from_row(row, cards))
        return result

    def _one_hot_from_row(self, row: CombatRow, cards: List[Card]) -> List[int]:
        result = []
        counter = 0
        for i, card in enumerate(cards):
            result.extend(card.repr_list())
            counter = i

        if counter < self.max_cards:
            for _ in range(self.max_cards - counter):
                result.extend(Card.empty_card_repr(row))

        return result

    def calculate_damage(self, weather: Weather) -> int:
        result = 0
        for row, cards in self.cards:
            result += self.calculate_damage_for_row(row, weather)
        return result

    def calculate_damage_for_row(self, row: CombatRow, weather: Weather) -> int:
        _calculate_damage_for_row(self.cards[row], weather)

    def __len__(self):
        length = 0
        for cards in self.cards.values():
            length += len(cards)
        return length


def _calculate_damage_for_row(cards: List[Card], weather: Weather) -> int:

    def check_weather(cards: List[Card], weather: Weather) -> List[Card]:
        affected_row = None
        if weather is Weather.CLEAR:
            pass
        elif weather is Weather.FROST:
            affected_row = CombatRow.CLOSE
        elif weather is Weather.FOG:
            affected_row = CombatRow.RANGE
        elif weather is Weather.RAIN:
            affected_row = CombatRow.SIEGE

        for card in cards:
            if card.combat_row is affected_row:
                card.damage = 1
        return cards

    def check_tight_bond(cards: List[Card]) -> List[Card]:
        bonds: DefaultDict[Card, int] = defaultdict(int)
        for card in cards:
            if card.ability is Ability.TIGHT_BOND:
                current_damage = bonds[card]
                bonds.update({card: current_damage + card.damage})

        for bond_card, new_damage in bonds.items():
            for card in cards:
                if card == bond_card:
                    card.damage = new_damage

        return cards

    def check_other_abilities(cards: List[Card]) -> List[Card]:
        def morale_boost(card: Card) -> Card:
            card.damage += 1
            return card

        def horn(card: Card) -> Card:
            card.damage *= 2
            return card

        updated_cards = deepcopy(cards)
        for current_card in cards:
            if current_card.ability is Ability.MORALE_BOOST:
                updated_cards = [morale_boost(card) for card in updated_cards if card != current_card]

            elif current_card.ability is Ability.COMMANDERS_HORN:
                updated_cards = [horn(card) for card in updated_cards if card != current_card]

        return updated_cards

    cards = deepcopy(cards)
    cards = check_weather(cards, weather)
    cards = check_tight_bond(cards)
    cards = check_other_abilities(cards)

    return sum([card.damage for card in cards])
