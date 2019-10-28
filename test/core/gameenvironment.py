import random
import unittest
from typing import Tuple

from source.core.card import Card, CombatRow
from source.core.cardcollection import CardCollection
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction


class GameEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(1, Faction.NOTHERN_REALMS, Card(CombatRow.CLOSE, 6) * 22)
        self.player2 = Player(2, Faction.NILFGAARD, Card(CombatRow.RANGE, 10) * 22)
        self.environment = GameEnvironment(self.player1, self.player2)

    def test_active_card_choice(self):
        self.assertEqual(10, len(self.player1.active_cards.get_all_cards()))
        self.assertEqual(10, len(self.player2.active_cards.get_all_cards()))

    def test_step(self):
        expected = (False, False)
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(expected, actual)

    def test_pass(self):
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        actual = self.environment.pass_(self.player1)
        self.assertEqual((False, False), actual)

        actual = self.environment.pass_(self.player2)
        self.assertEqual((True, False), actual)

    def test_no_cards_left(self):
        card = Card(CombatRow.CLOSE, 3)
        self.player1.active_cards = CardCollection([card])
        self.player2.active_cards = CardCollection([card])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual((False, False), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertEqual((True, False), actual)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.environment.current_round = 1

        self.player1.active_cards = CardCollection([card])
        self.player2.active_cards = CardCollection([card])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual((False, False), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertEqual((True, True), actual)
