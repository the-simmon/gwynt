import unittest

from source.core.card import Card, LeaderCard
from source.core.cardcollection import CardCollection
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player, Faction


class GameEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(1, Faction.NOTHERN_REALMS, Card(CombatRow.CLOSE, 6) * 22, LeaderCard())
        self.player2 = Player(2, Faction.NILFGAARD, Card(CombatRow.RANGE, 10) * 22, LeaderCard())
        self.environment = GameEnvironment(self.player1, self.player2)
        self.environment.init()

    def test_active_card_choice(self):
        self.assertEqual(10, len(self.player1.hand.get_all_cards()))
        self.assertEqual(10, len(self.player2.hand.get_all_cards()))

    def test_step(self):
        expected = (False, self.player2, CardSource.HAND)
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertCountEqual(expected, actual)

    def test_pass(self):
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, None, None)
        self.assertCountEqual((False, self.player2, CardSource.HAND), actual)

        actual = self.environment.step(self.player2, None, None)
        self.assertEqual((False, self.player1, CardSource.HAND), actual)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.environment.current_round = 2

        self.player1.hand = CardCollection([card])
        self.player2.hand = CardCollection([card])

        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertCountEqual((False, self.player2, CardSource.HAND), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertCountEqual((True, self.player2, CardSource.HAND), actual)
