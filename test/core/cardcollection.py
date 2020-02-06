import unittest

from source.core.card import Ability, Card
from source.core.cardcollection import CardCollection
from source.core.comabt_row import CombatRow
from source.core.weather import Weather


class CardCollectionTest(unittest.TestCase):

    def setUp(self):
        self.max_cards = 5
        self.close_cards = [Card(CombatRow.CLOSE, 5, Ability.NONE), Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND),
                            Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND),
                            Card(CombatRow.CLOSE, 0, Ability.COMMANDERS_HORN)]
        self.range_cards = [Card(CombatRow.RANGE, 6, Ability.NONE, hero=True)]
        self.card_collection = CardCollection(self.close_cards + self.range_cards)

    def test_calculate_damage_clear_weather(self):
        expected = 40
        self.assertEqual(expected, self.card_collection.calculate_damage([Weather.CLEAR], []))

    def test_calculate_damage_frost_weather(self):
        expected = 16
        self.assertEqual(expected, self.card_collection.calculate_damage([Weather.FROST], []))

    def test_calculate_damage_hero_weather(self):
        expected = 40
        self.assertEqual(expected, self.card_collection.calculate_damage([Weather.FOG], []))

    def test_get_all_cards(self):
        expected = self.close_cards + self.range_cards
        self.assertCountEqual(expected, self.card_collection.get_all_cards())
