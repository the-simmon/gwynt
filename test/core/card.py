import unittest

from source.core.card import CombatRow


class CardText(unittest.TestCase):

    def test_get_possible_rows(self):
        actual = CombatRow.get_possible_rows(CombatRow.AGILE)
        self.assertCountEqual(actual, [CombatRow.CLOSE, CombatRow.RANGE])

        actual = CombatRow.get_possible_rows(CombatRow.SPECIAL)
        self.assertCountEqual(actual, [CombatRow.CLOSE, CombatRow.RANGE, CombatRow.SIEGE])

        actual = CombatRow.get_possible_rows(CombatRow.CLOSE)
        self.assertCountEqual(actual, [CombatRow.CLOSE])
