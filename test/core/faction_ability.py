import unittest

from source.core.card import Card, LeaderCard
from source.core.comabt_row import CombatRow
from source.core.faction_abililty import monster_ability_get_card_to_survive, nilfgaard_check_draw, \
    northern_realms_check_extra_card
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction


class FactionAbilityText(unittest.TestCase):

    def test_monster(self):
        player1 = Player(0, Faction.MONSTER, [], LeaderCard())
        player2 = Player(1, Faction.NILFGAARD, [], LeaderCard())
        environment = GameEnvironment(player1, player2)

        cards = [Card(CombatRow.CLOSE, 1), Card(CombatRow.SIEGE, 9)]
        environment.board.add(player1, cards[0].combat_row, cards[0])
        environment.board.add(player1, cards[1].combat_row, cards[1])

        actual = monster_ability_get_card_to_survive(environment.board, player1)
        self.assertIn(actual, cards)

    def test_nilfgaard(self):
        player1 = Player(0, Faction.MONSTER, [], LeaderCard())
        player2 = Player(1, Faction.NILFGAARD, [], LeaderCard())
        environment = GameEnvironment(player1, player2)
        environment.board.add(player1, CombatRow.CLOSE, Card(CombatRow.CLOSE, 1))
        environment.board.add(player2, CombatRow.CLOSE, Card(CombatRow.CLOSE, 1))

        nilfgaard_check_draw(environment)
        self.assertEqual(0, player1.rounds_won)
        self.assertEqual(1, player2.rounds_won)

    def test_northern_realms(self):
        player1 = Player(0, Faction.NORTHERN_REALMS, [Card(CombatRow.CLOSE, 2)], LeaderCard())
        northern_realms_check_extra_card(player1)
        self.assertEqual(1, len(player1.hand))
