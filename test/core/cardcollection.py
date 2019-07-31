import unittest
from copy import deepcopy

from source.core.card import CombatRow, Ability, Card
from source.core.cardcollection import CardCollection
from source.core.weather import Weather


class CardCollectionTest(unittest.TestCase):

    def setUp(self):
        self.max_cards = 5
        self.close_cards = [Card(CombatRow.CLOSE, 5, Ability.NONE), Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND),
                            Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND), Card(CombatRow.CLOSE, 0, Ability.COMMANDERS_HORN)]
        self.range_cards = [Card(CombatRow.RANGE, 6, Ability.NONE, hero=True)]
        self.card_collection = CardCollection(max_cards=self.max_cards, cards=self.close_cards + self.range_cards)

    def test_repr_list(self):
        expected = []
        for card in self.close_cards:
            expected.extend(card.repr_list())
        for _ in range(self.max_cards - len(self.close_cards)):
            expected.extend(Card.empty_card_repr())

        for card in self.range_cards:
            expected.extend(card.repr_list())
        for _ in range(self.max_cards - len(self.range_cards)):
            expected.extend(Card.empty_card_repr())

        for _ in range(2):
            for _ in range(self.max_cards):
                expected.extend(Card.empty_card_repr())
        self.assertEqual(expected, self.card_collection.repr_list())

    def test_repr_list_with_excluded_card(self):

        expected = []

        for card in self.close_cards[1:]:
            expected.extend(card.repr_list())
        for _ in range(self.max_cards - len(self.close_cards[1:])):
            expected.extend(Card.empty_card_repr())

        for card in self.range_cards:
            expected.extend(card.repr_list())
        for _ in range(self.max_cards - len(self.range_cards)):
            expected.extend(Card.empty_card_repr())

        for _ in range(2):
            for _ in range(self.max_cards):
                expected.extend(Card.empty_card_repr())

        self.assertEqual(expected, self.card_collection.repr_list(exclude_card=self.close_cards[0]))

    def test_calculate_damage_clear_weather(self):
        expected = 40
        self.assertEqual(expected, self.card_collection.calculate_damage(Weather.CLEAR))

    def test_calculate_damage_frost_weather(self):
        expected = 16
        self.assertEqual(expected, self.card_collection.calculate_damage(Weather.FROST))

    def test_calculate_damage_hero_weather(self):
        expected = 40
        self.assertEqual(expected, self.card_collection.calculate_damage(Weather.FOG))
