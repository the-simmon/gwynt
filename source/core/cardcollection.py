from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, List, Callable

from source.core.card import Card, Ability, LeaderAbility
from source.core.comabt_row import CombatRow
from source.core.weather import Weather


class CardCollection(DefaultDict[CombatRow, List[Card]]):

    def __init__(self, cards: List[Card]):
        super().__init__(list)

        for card in cards:
            self[card.combat_row].append(card)

    def add(self, row: CombatRow, card: Card):
        self[row].append(card)

    def remove(self, row: CombatRow, card: Card):
        self[row].remove(card)

    def calculate_damage(self, weather: List[Weather], passive_leaders: List[LeaderAbility]) -> int:
        result = 0
        for row, cards in self.items():
            result += self.calculate_damage_for_row(row, weather, passive_leaders)
        return result

    def calculate_damage_for_row(self, row: CombatRow, weather: List[Weather],
                                 passive_leaders: List[LeaderAbility]) -> int:
        cards = _calculate_damage_for_row(self[row], row, weather, passive_leaders)
        return sum([card.damage for card in cards])

    def get_damage_adjusted_cards(self, row: CombatRow, weather: List[Weather], passive_leaders: List[LeaderAbility]) -> \
            List[Card]:
        return _calculate_damage_for_row(self[row], row, weather, passive_leaders)

    def get_all_cards(self) -> List[Card]:
        result = []
        for cards in self.values():
            result.extend(cards)
        return result

    def __deepcopy__(self, memodict={}):
        copy = CardCollection([])
        for row, cards in self.items():
            copy[row] = deepcopy(cards)
        return copy


def _calculate_damage_for_row(cards: List[Card], row: CombatRow, weather: List[Weather],
                              passive_leaders: List[LeaderAbility]) -> List[Card]:
    def double_spy_leader(cards: List[Card]) -> List[Card]:
        for card in cards:
            if card.ability is Ability.SPY:
                card.damage *= 2
        return cards

    def check_weather(cards: List[Card], weather: List[Weather]) -> List[Card]:
        affected_rows: List[CombatRow] = []
        if Weather.FROST in weather:
            affected_rows.append(CombatRow.CLOSE)
        if Weather.FOG in weather:
            affected_rows.append(CombatRow.RANGE)
        if Weather.RAIN in weather:
            affected_rows.append(CombatRow.SIEGE)

        if row in affected_rows:
            for card in cards:
                if card.damage > 0 and not card.hero:
                    card.damage = 1
        return cards

    def check_tight_bond(cards: List[Card]) -> List[Card]:
        bonds: DefaultDict[Card, int] = defaultdict(int)
        for card in deepcopy(cards):
            if card.ability is Ability.TIGHT_BOND:
                current_damage = bonds[card]
                if current_damage == 0:
                    bonds.update({card: card.damage})
                else:
                    bonds.update({card: current_damage * 2})

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
                if card != current_card and not card.hero and card.combat_row is not CombatRow.SPECIAL:
                    f(card)

        # there are two types of commanders horn, dandelion and the generic horn
        horn_applied = False
        special_horn_applied = False
        for current_card in cards:
            if current_card.ability is Ability.MORALE_BOOST:
                apply_function(morale_boost, cards, current_card)

            elif current_card.ability is Ability.COMMANDERS_HORN and not horn_applied:
                apply_function(horn, cards, current_card)
                horn_applied = True

            elif current_card.ability is Ability.SPECIAL_COMMANDERS_HORN and not special_horn_applied:
                apply_function(horn, cards, current_card)
                special_horn_applied = True

        return cards

    cards = deepcopy(cards)
    if LeaderAbility.SPY_DAMAGE in passive_leaders:
        cards = double_spy_leader(cards)
    cards = check_weather(cards, weather)
    cards = check_tight_bond(cards)
    cards = check_other_abilities(cards)

    return cards
