import unittest

from source.ai.random_forest.randomforest import RandomForest
from source.core.card import Card, CombatRow
from source.core.cardcollection import CardCollection
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction


class GameEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(1, Faction.NOTHERN_REALMS, Card(CombatRow.CLOSE, 6) * 22)
        self.player2 = Player(2, Faction.NILFGAARD, Card(CombatRow.RANGE, 10) * 22)
        self.environment = GameEnvironment(self.player1, self.player2, RandomForest())

    def test_repr_list(self):
        expected = self.environment.board.repr_list(self.player1, self.player1.active_cards[CombatRow.CLOSE][0]) + [1,
                                                                                                                    0,
                                                                                                                    0]
        self.assertEqual(expected,
                         self.environment.repr_list(self.player1, self.player1.active_cards[CombatRow.CLOSE][0]))

    def test_active_card_choice(self):
        self.assertEqual(10, len(self.player1.active_cards.get_all_cards()))
        self.assertEqual(10, len(self.player2.active_cards.get_all_cards()))

    def test_step(self):
        expected = False
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(expected, actual)

    def test_pass(self):
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        actual = self.environment.step(self.player1, pass_=True)
        self.assertEqual(False, actual)

        actual = self.environment.step(self.player2, pass_=True)
        self.assertEqual(True, actual)

        actual = self.environment.get_round_reward(self.player1)
        self.assertCountEqual([10, False], actual)

        actual = self.environment.get_round_reward(self.player2)
        self.assertCountEqual([-10, False], actual)

    def test_no_cards_left(self):
        card = Card(CombatRow.CLOSE, 3)
        self.player1.active_cards = CardCollection(max_cards=22, cards=[card])
        self.player2.active_cards = CardCollection(max_cards=22, cards=[])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(True, actual)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.player1.active_cards = CardCollection(max_cards=22, cards=[card])
        self.player2.active_cards = CardCollection(max_cards=22, cards=[])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(True, actual)

        actual = self.environment.get_round_reward(self.player1)
        self.assertCountEqual([10, True], actual)

        actual = self.environment.get_round_reward(self.player2)
        self.assertCountEqual([-10, True], actual)

        self.environment.current_round = 3
        self.player1.rounds_won = 2

        actual = self.environment.get_game_reward(self.player1)
        self.assertEqual(100, actual)

        actual = self.environment.get_game_reward(self.player2)
        self.assertEqual(-100, actual)
