import unittest

from source.core.card import CombatRow, Ability, Card
from source.core.cardcollection import CardCollection
from source.core.player import Player, Faction


class PlayerTest(unittest.TestCase):

    def setUp(self):
        self.deck_cards = [Card(CombatRow.CLOSE, 5, Ability.SCORCH)]
        self.active_cards = [Card(CombatRow.SIEGE, 10, Ability.MEDIC, hero=True)]
        self.graveyard_cards = [Card(CombatRow.RANGE, 9, Ability.NONE, hero=True)]
        self.player = Player(0, Faction.NILFGAARD, self.deck_cards)

        for card in self.graveyard_cards:
            self.player.graveyard.add(card.combat_row, card)

        for card in self.active_cards:
            self.player.active_cards.add(card.combat_row, card)

    def test_repr_list(self):
        expected = Faction.NILFGAARD.one_hot() + CardCollection(max_cards=22, cards=self.graveyard_cards).repr_list()
        self.assertEqual(expected, self.player.repr_list())

    def test_repr_list_with_deck_and_active(self):
        expected = Faction.NILFGAARD.one_hot() + CardCollection(max_cards=22, cards=self.graveyard_cards).repr_list() \
                   + CardCollection(max_cards=22, cards=self.deck_cards).repr_list() + \
                   CardCollection(max_cards=22, cards=self.active_cards).repr_list()
        self.assertEqual(expected, self.player.repr_list(include_deck_and_active=True))
