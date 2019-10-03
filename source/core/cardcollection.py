from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List, Callable

from .weather import Weather
from .card import CombatRow, Card, Ability


class CardCollection(DefaultDict[CombatRow, List[Card]]):

    def __init__(self, max_cards: int, cards: List[Card]):
        super().__init__(list)
        self.max_cards = max_cards

        for card in cards:
            self[card.combat_row].append(card)

    def add(self, row: CombatRow, card: Card):
        self[row].append(card)

    def remove(self, row: CombatRow, card: Card):
        self[row].remove(card)

    def repr_list(self, exclude_card: Card = None) -> List[int]:
        result = []
        for row in CombatRow:
            result.extend(self._one_hot_from_row(self[row], exclude_card))
        return result

    def _one_hot_from_row(self, cards: List[Card], exclude_card: Card = None) -> List[int]:
        result = []
        exclude_once = False
        empty_cards = self.max_cards - len(cards)

        for card in cards:
            if card != exclude_card or exclude_once:
                result.extend(card.repr_list())
            else:
                exclude_once = True
                empty_cards += 1

        for _ in range(empty_cards):
            result.extend(Card.empty_card_repr())

        return result

    def calculate_damage(self, weather: Weather) -> int:
        result = 0
        for row, cards in self.items():
            result += self.calculate_damage_for_row(row, weather)
        return result

    def calculate_damage_for_row(self, row: CombatRow, weather: Weather) -> int:
        cards = _calculate_damage_for_row(self[row], weather)
        return sum([card.damage for card in cards])

    def get_damage_adjusted_cards(self, row: CombatRow, weather: Weather) -> List[Card]:
        return _calculate_damage_for_row(self[row], weather)

    def get_all_cards(self) -> List[Card]:
        result = []
        for cards in self.values():
            result.extend(cards)
        return result

    def __deepcopy__(self, memodict={}):
        copy = CardCollection(self.max_cards, [])
        for row, cards in self.items():
            copy[row] = deepcopy(cards)
        copy.max_cards = self.max_cards
        return copy

    def __str__(self):
        result = ''
        for row, cards in self.cards.items():
            result += '{}: '.format(row.name)
            for card in cards:
                result += '({}) '.format(str(card))
            result += '\n'
        return result


def _calculate_damage_for_row(cards: List[Card], weather: Weather) -> List[Card]:
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
            if card.combat_row is affected_row and card.damage > 0 and not card.hero:
                card.damage = 1
        return cards

    def check_tight_bond(cards: List[Card]) -> List[Card]:
        bonds: DefaultDict[Card, int] = defaultdict(int)
        for card in deepcopy(cards):
            if card.ability is Ability.TIGHT_BOND:
                current_damage = bonds[card]
                bonds.update({card: current_damage + card.damage})

        for bond_card, new_damage in bonds.items():
            for card in cards:
                if card == bond_card:
                    card.damage = new_damage

        return cards

    def check_other_abilities(cards: List[Card]) -> List[Card]:
        def morale_boost(card: Card):
            card.damage += 1

        def horn(card: Card):
            card.damage *= 2

        def apply_function(f: Callable[[Card], None], cards: List[Card], current_card: Card):
            for card in cards:
                if card != current_card:
                    f(card)

        horn_applied = False
        for current_card in cards:
            if current_card.ability is Ability.MORALE_BOOST:
                apply_function(morale_boost, cards, current_card)

            elif current_card.ability is Ability.COMMANDERS_HORN and not horn_applied:
                apply_function(horn, cards, current_card)
                horn_applied = True

        return cards

    cards = deepcopy(cards)
    cards = check_weather(cards, weather)
    cards = check_tight_bond(cards)
    cards = check_other_abilities(cards)

    return cards
