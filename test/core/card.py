import unittest

from source.core.card import Card, CombatRow, Ability


class CardTest(unittest.TestCase):

    def test_repr_list(self):
        card = Card(CombatRow.RANGE, 5, Ability.NONE, hero=True)
        expected = [5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(expected, card.repr_list())

    def test_empty_card_repr(self):
        expected = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(expected, Card.empty_card_repr())
