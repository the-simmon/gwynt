import unittest

from source.core.board import Board
from source.core.card import Card, CombatRow, Ability
from source.core.player import Faction, Player
from source.core.weather import Weather


class BoardTest(unittest.TestCase):

    def setUp(self):
        self.player1_deck_cards = [Card(CombatRow.CLOSE, 4, Ability.NONE), Card(CombatRow.CLOSE, 5, Ability.NONE)]
        self.player1 = Player(0, Faction.NILFGAARD, self.player1_deck_cards)
        self.player2 = Player(1, Faction.NOTHERN_REALMS, [])
        self.board = Board(self.player1, self.player2)

    def test_weather_card(self):
        self.board.add(self.player1, CombatRow.SPECIAL, Card(CombatRow.SPECIAL, 0, Ability.FOG))
        self.assertEqual(Weather.FOG, self.board.weather)

    def test_none_ability_card(self):
        card = Card(CombatRow.CLOSE, 3, Ability.NONE)
        self.board.add(self.player1, card.combat_row, card)
        self.assertEqual([card], self.board.cards[self.player1].cards[card.combat_row])

    def test_remove_card(self):
        card = Card(CombatRow.CLOSE, 3, Ability.NONE)
        self.board.add(self.player1, card.combat_row, card)
        self.board.remove(self.player1, CombatRow.CLOSE, card)
        self.assertEqual([card], self.player1.graveyard.cards[CombatRow.CLOSE])

    def test_row_scorch(self):
        scorched_card = Card(CombatRow.CLOSE, 11, Ability.NONE)
        self.board.add(self.player2, scorched_card.combat_row, scorched_card)
        self.board.add(self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 2, Ability.SCORCH))
        self.assertEqual([scorched_card], self.player2.graveyard.cards[CombatRow.CLOSE])
        self.assertTrue(scorched_card not in self.board.cards[self.player2].cards[scorched_card.combat_row])

    def test_special_scorch(self):
        cards_to_scorch1 = [Card(CombatRow.CLOSE, 6, Ability.NONE), Card(CombatRow.SIEGE, 6, Ability.MORALE_BOOST)]
        surviving_cards1 = [Card(CombatRow.CLOSE, 3, Ability.NONE), Card(CombatRow.RANGE, 15, Ability.NONE, hero=True)]

        for card in cards_to_scorch1 + surviving_cards1:
            self.board.add(self.player1, card.combat_row, card)

        cards_to_scorch2 = [Card(CombatRow.RANGE, 6, Ability.NONE)]
        surviving_cards2 = [Card(CombatRow.CLOSE, 2, Ability.NONE)]

        for card in cards_to_scorch2 + surviving_cards2:
            self.board.add(self.player2, card.combat_row, card)

        self.board.add(self.player2, CombatRow.SPECIAL, Card(CombatRow.SPECIAL, 0, Ability.SCORCH))

        self.assertEqual([cards_to_scorch1[0]], self.player1.graveyard.cards[CombatRow.CLOSE])
        self.assertEqual([cards_to_scorch1[1]], self.player1.graveyard.cards[CombatRow.SIEGE])
        self.assertEqual([surviving_cards1[0]], self.board.cards[self.player1].cards[CombatRow.CLOSE])
        self.assertEqual([surviving_cards1[1]], self.board.cards[self.player1].cards[CombatRow.RANGE])

        self.assertEqual(cards_to_scorch2, self.player2.graveyard.cards[CombatRow.RANGE])
        self.assertEqual(surviving_cards2, self.board.cards[self.player2].cards[CombatRow.CLOSE])

    def test_medic_card(self):
        args = self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 3, Ability.MEDIC)
        self.assertRaises(NotImplementedError, self.board.add, *args)

    def test_spy_card(self):
        spy = Card(CombatRow.CLOSE, 5, Ability.SPY)
        self.board.add(self.player1, spy.combat_row, spy)

        self.assertCountEqual(self.player1_deck_cards, self.player1.active_cards.cards[CombatRow.CLOSE])
        self.assertEqual([spy], self.board.cards[self.player2].cards[spy.combat_row])
