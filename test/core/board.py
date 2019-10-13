import random
import unittest
from typing import Tuple

from source.core.board import Board
from source.core.card import Card, CombatRow, Ability, Muster
from source.core.cardcollection import CardCollection
from source.core.gameenvironment import GameEnvironment
from source.core.player import Faction, Player
from source.core.weather import Weather


def revive(environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
    if player.graveyard.get_all_cards():
        card = random.choice(player.graveyard.get_all_cards())
        row = random.choice(CombatRow.get_possible_rows(card.combat_row))
    else:
        card, row = None, None
    return card, row


class BoardTest(unittest.TestCase):

    def setUp(self):
        self.player1_deck_cards = [Card(CombatRow.CLOSE, 4, Ability.NONE), Card(CombatRow.CLOSE, 5, Ability.NONE)]
        self.player1 = Player(0, Faction.NILFGAARD, self.player1_deck_cards)
        self.player1_active_card = Card(CombatRow.RANGE, 9)
        self.player1.active_cards.add(self.player1_active_card.combat_row, self.player1_active_card)

        self.player2_muster_cards = Card(CombatRow.CLOSE, 8, Ability.MUSTER, muster=Muster.NEKKER) * 3
        self.player2_deck_cards = [Card(CombatRow.CLOSE, 3, Ability.NONE)] + self.player2_muster_cards
        self.player2 = Player(1, Faction.NOTHERN_REALMS, self.player2_deck_cards)
        self.player2.active_cards.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 0))

        dummy_player = Player(0, Faction.NILFGAARD, [])
        self.board = Board(self.player1, self.player2, revive,
                           GameEnvironment(dummy_player, dummy_player, revive))

    def test_repr_list(self):
        empty_card_collection = CardCollection(22, [])
        expected = [1] + self.player2.repr_list() + self.player1.repr_list(include_deck_and_active=True,
                                                                           exclude_card=self.player1_active_card) + \
                   empty_card_collection.repr_list() + empty_card_collection.repr_list() + Weather.CLEAR.one_hot()
        self.assertCountEqual(expected, self.board.repr_list(self.player1, excluded_card=self.player1_active_card))

    def test_weather_card(self):
        self.board.add(self.player1, CombatRow.SPECIAL, Card(CombatRow.SPECIAL, 0, Ability.FOG))
        self.assertEqual(Weather.FOG, self.board.weather)

    def test_none_ability_card(self):
        card = Card(CombatRow.CLOSE, 3, Ability.NONE)
        self.board.add(self.player1, card.combat_row, card)
        self.assertEqual([card], self.board.cards[self.player1][card.combat_row])

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
        self.assertTrue(scorched_card not in self.board.cards[self.player2][scorched_card.combat_row])

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

        self.assertEqual([cards_to_scorch1[0]], self.player1.graveyard[CombatRow.CLOSE])
        self.assertEqual([cards_to_scorch1[1]], self.player1.graveyard[CombatRow.SIEGE])
        self.assertEqual([surviving_cards1[0]], self.board.cards[self.player1][CombatRow.CLOSE])
        self.assertEqual([surviving_cards1[1]], self.board.cards[self.player1][CombatRow.RANGE])

        self.assertEqual(cards_to_scorch2, self.player2.graveyard[CombatRow.RANGE])
        self.assertEqual(surviving_cards2, self.board.cards[self.player2][CombatRow.CLOSE])

    def test_medic_card(self):
        self.player1.graveyard.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 3))
        self.board.add(self.player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 3, Ability.MEDIC))
        self.assertEqual(2, len(self.board.cards[self.player1].get_all_cards()))

    def test_spy_card(self):
        spy = Card(CombatRow.CLOSE, 5, Ability.SPY)
        self.board.add(self.player1, spy.combat_row, spy)

        self.assertCountEqual(self.player1_deck_cards, self.player1.active_cards[CombatRow.CLOSE])
        self.assertEqual([spy], self.board.cards[self.player2][spy.combat_row])

    def test_muster(self):
        muster_card = Card(CombatRow.CLOSE, 4, Ability.MUSTER, muster=Muster.NEKKER)
        self.board.add(self.player2, muster_card.combat_row, muster_card)
        self.assertCountEqual(self.player2_muster_cards + [muster_card],
                              self.board.cards[self.player2][CombatRow.CLOSE])

    def test_all_cards_to_graveyard(self):
        for card in self.player1_deck_cards:
            self.board.add(self.player1, card.combat_row, card)

        self.board.all_cards_to_graveyard(self.player1)
        self.assertCountEqual(self.player1_deck_cards, self.player1.graveyard.get_all_cards())
