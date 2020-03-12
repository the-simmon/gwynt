import unittest

from source.core.card import Ability, Card, LeaderAbility
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

    def test_double_spy_leader(self):
        spy = Card(CombatRow.CLOSE, 2, Ability.SPY)
        self.card_collection.add(spy.combat_row, spy)
        expected = 48
        actual = self.card_collection.calculate_damage([Weather.CLEAR], [LeaderAbility.SPY_DAMAGE])
        self.assertEqual(expected, actual)

    def test_2tight_bond(self):
        self.card_collection = CardCollection(Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND) * 2)
        self.assertEqual(12, self.card_collection.calculate_damage([Weather.CLEAR], []))

    def test_3tight_bond(self):
        self.card_collection = CardCollection(Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND) * 3)
        self.assertEqual(27, self.card_collection.calculate_damage([Weather.CLEAR], []))

    def test_3tight_bond_with_horn(self):
        self.card_collection = CardCollection(Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND) * 3 +
                                              [Card(CombatRow.CLOSE, 0, Ability.SPECIAL_COMMANDERS_HORN)])
        self.assertEqual(54, self.card_collection.calculate_damage([Weather.CLEAR], []))
