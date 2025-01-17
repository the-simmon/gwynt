import unittest

from source.core.board import Board
from source.core.card import Card, Ability, Muster, LeaderCard
from source.core.comabt_row import CombatRow
from source.core.player import Faction, Player
from source.core.weather import Weather
from source.game_settings import GameSettings


class BoardTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        GameSettings.PLAY_AGAINST_WITCHER = False

    def setUp(self):
        self.player1_deck_cards = [Card(CombatRow.CLOSE, 4, Ability.NONE), Card(CombatRow.CLOSE, 5, Ability.NONE)]
        self.player1 = Player(0, Faction.NILFGAARD, self.player1_deck_cards, LeaderCard())
        self.player1_active_card = Card(CombatRow.RANGE, 9)
        self.player1.hand.add(self.player1_active_card.combat_row, self.player1_active_card)

        self.player2_muster_cards = Card(CombatRow.CLOSE, 8, Ability.MUSTER, muster=Muster.NEKKER) * 3
        self.player2_deck_cards = [Card(CombatRow.CLOSE, 3, Ability.NONE)] + self.player2_muster_cards
        self.player2 = Player(1, Faction.NORTHERN_REALMS, self.player2_deck_cards, LeaderCard())
        self.player2.hand.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 0))

        self.board = Board(self.player1, self.player2, [])

    def test_weather_card(self):
        self.board.add(self.player1, CombatRow.SPECIAL, Card(CombatRow.SPECIAL, 0, Ability.FOG))
        self.assertEqual([Weather.FOG], self.board.weather)

        self.board.add(self.player1, CombatRow.SPECIAL, Card(CombatRow.SPECIAL, 0, Ability.RAIN))
        self.assertEqual([Weather.FOG, Weather.RAIN], self.board.weather)

        self.board.add(self.player1, self.player1_active_card.combat_row, self.player1_active_card)
        actual = self.board.calculate_damage(self.player1)
        self.assertEqual(1, actual)

    def test_none_ability_card(self):
        card = Card(CombatRow.CLOSE, 3, Ability.NONE)
        self.board.add(self.player1, card.combat_row, card)
        self.assertEqual([card], self.board.cards[self.player1.id][card.combat_row])

    def test_remove_card(self):
        card = Card(CombatRow.CLOSE, 3, Ability.NONE)
        self.board.add(self.player1, card.combat_row, card)
        self.board.remove(self.player1, CombatRow.CLOSE, card)
        self.assertEqual([card], self.player1.graveyard[CombatRow.CLOSE])

    def test_row_scorch(self):
        scorched_card = Card(CombatRow.CLOSE, 11, Ability.NONE)
        self.board.add(self.player2, scorched_card.combat_row, scorched_card)
        self.board.add(self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 2, Ability.SCORCH))
        self.assertEqual([scorched_card], self.player2.graveyard[CombatRow.CLOSE])
        self.assertTrue(scorched_card not in self.board.cards[self.player2.id][scorched_card.combat_row])

    def test_row_scorch_multiple(self):
        scorched_card = Card(CombatRow.CLOSE, 11, Ability.NONE)
        self.board.add(self.player2, scorched_card.combat_row, scorched_card)
        self.board.add(self.player2, scorched_card.combat_row, scorched_card)
        self.board.add(self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 2, Ability.SCORCH))
        self.assertCountEqual([scorched_card, scorched_card], self.player2.graveyard[CombatRow.CLOSE])
        self.assertTrue(scorched_card not in self.board.cards[self.player2.id][scorched_card.combat_row])

    def test_special_scorch(self):
        cards_to_scorch1 = [Card(CombatRow.CLOSE, 6, Ability.NONE), Card(CombatRow.SIEGE, 6, Ability.MORALE_BOOST)]
        surviving_cards1 = [Card(CombatRow.CLOSE, 3, Ability.NONE), Card(CombatRow.RANGE, 15, Ability.NONE, hero=True)]

        for card in cards_to_scorch1 + surviving_cards1:
            self.board.add(self.player1, card.combat_row, card)

        cards_to_scorch2 = [Card(CombatRow.RANGE, 6, Ability.NONE)]
        surviving_cards2 = [Card(CombatRow.CLOSE, 2, Ability.NONE)]

        for card in cards_to_scorch2 + surviving_cards2:
            self.board.add(self.player2, card.combat_row, card)

        self.board.add(self.player2, CombatRow.NONE, Card(CombatRow.NONE, 0, Ability.SCORCH))

        self.assertEqual([cards_to_scorch1[0]], self.player1.graveyard[CombatRow.CLOSE])
        self.assertEqual([cards_to_scorch1[1]], self.player1.graveyard[CombatRow.SIEGE])
        self.assertEqual([surviving_cards1[0]], self.board.cards[self.player1.id][CombatRow.CLOSE])
        self.assertEqual([surviving_cards1[1]], self.board.cards[self.player1.id][CombatRow.RANGE])

        self.assertEqual(cards_to_scorch2, self.player2.graveyard[CombatRow.RANGE])
        self.assertEqual(surviving_cards2, self.board.cards[self.player2.id][CombatRow.CLOSE])

    def test_spy_card(self):
        spy = Card(CombatRow.CLOSE, 5, Ability.SPY)
        self.board.add(self.player1, spy.combat_row, spy)

        self.assertCountEqual(self.player1_deck_cards, self.player1.hand[CombatRow.CLOSE])
        self.assertEqual([spy], self.board.cards[self.player2.id][spy.combat_row])

    def test_muster(self):
        muster_card = Card(CombatRow.CLOSE, 4, Ability.MUSTER, muster=Muster.NEKKER)
        self.board.add(self.player2, muster_card.combat_row, muster_card)
        self.assertCountEqual(self.player2_muster_cards + [muster_card],
                              self.board.cards[self.player2.id][CombatRow.CLOSE])

    def test_all_cards_to_graveyard(self):
        for card in self.player1_deck_cards:
            self.board.add(self.player1, card.combat_row, card)
        self.board.add(self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 9, hero=True))

        self.board.all_cards_to_graveyard(self.player1)
        self.assertCountEqual(self.player1_deck_cards, self.player1.graveyard.get_all_cards())

    def test_get_enemy(self):
        actual = self.board.get_enemy_player(self.player1)
        self.assertEqual(self.player2, actual)

    def test_agile_to_best_row_leader(self):
        self.board.cards[self.player1.id].add(CombatRow.CLOSE, Card(CombatRow.AGILE, 9))
        self.board.cards[self.player1.id].add(CombatRow.CLOSE, Card(CombatRow.AGILE, 5, hero=True))
        self.board.cards[self.player1.id].add(CombatRow.RANGE, Card(CombatRow.AGILE, 9))
        self.board.cards[self.player1.id].add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 3))
        self.board.weather = [Weather.FROST]

        self.assertEqual(16, self.board.calculate_damage(self.player1))
        self.board.agile_to_best_row_leader(self.player1)
        self.assertEqual(24, self.board.calculate_damage(self.player1))
        expected_close = [Card(CombatRow.AGILE, 5, hero=True), Card(CombatRow.CLOSE, 3)]
        expected_range = Card(CombatRow.AGILE, 9) * 2
        self.assertCountEqual(expected_close, self.board.cards[self.player1.id][CombatRow.CLOSE])
        self.assertCountEqual(expected_range, self.board.cards[self.player1.id][CombatRow.RANGE])
