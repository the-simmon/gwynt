import random
import unittest
from typing import Tuple

from source.core.card import Card, CombatRow
from source.core.cardcollection import CardCollection
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction


def revive(environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
    if player.graveyard.get_all_cards():
        card = random.choice(player.graveyard.get_all_cards())
        row = random.choice(CombatRow.get_possible_rows(card.combat_row))
    else:
        card, row = None, None
    return card, row


class GameEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(1, Faction.NOTHERN_REALMS, Card(CombatRow.CLOSE, 6) * 22)
        self.player2 = Player(2, Faction.NILFGAARD, Card(CombatRow.RANGE, 10) * 22)
        self.environment = GameEnvironment(self.player1, self.player2, revive)

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
        expected = (False, False)
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(expected, actual)

    def test_pass(self):
        card = self.player1.active_cards[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        actual = self.environment.step(self.player1, pass_=True)
        self.assertEqual((False, False), actual)

        actual = self.environment.step(self.player2, pass_=True)
        self.assertEqual((True, False), actual)

    def test_no_cards_left(self):
        card = Card(CombatRow.CLOSE, 3)
        self.player1.active_cards = CardCollection(max_cards=22, cards=[card])
        self.player2.active_cards = CardCollection(max_cards=22, cards=[card])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual((False, False), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertEqual((True, False), actual)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.environment.current_round = 1

        self.player1.active_cards = CardCollection(max_cards=22, cards=[card])
        self.player2.active_cards = CardCollection(max_cards=22, cards=[card])

        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual((False, False), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertEqual((True, True), actual)
