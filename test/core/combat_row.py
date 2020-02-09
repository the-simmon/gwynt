import unittest

from source.core.card import Card
from source.core.comabt_row import CombatRow


class CombatRowTest(unittest.TestCase):

    def test_get_possible_rows(self):
        card = Card(CombatRow.AGILE, 0)
        actual = CombatRow.get_possible_rows(card)
        self.assertCountEqual(actual, [CombatRow.CLOSE, CombatRow.RANGE])

        card.combat_row = CombatRow.SPECIAL
        actual = CombatRow.get_possible_rows(card)
        self.assertCountEqual(actual, [CombatRow.CLOSE, CombatRow.RANGE, CombatRow.SIEGE])

        card.combat_row = CombatRow.CLOSE
        actual = CombatRow.get_possible_rows(card)
        self.assertCountEqual(actual, [CombatRow.CLOSE])

        card.combat_row = CombatRow.NONE
        actual = CombatRow.get_possible_rows(card)
        self.assertCountEqual(actual, [CombatRow.NONE])
