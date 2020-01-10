import unittest

from source.core.card import Ability, Card
from source.core.comabt_row import CombatRow
from source.core.player import Player, Faction


class PlayerTest(unittest.TestCase):

    def setUp(self):
        self.deck_cards = [Card(CombatRow.CLOSE, 5, Ability.SCORCH)]
        self.hand = [Card(CombatRow.SIEGE, 10, Ability.MEDIC, hero=True)]
        self.graveyard_cards = [Card(CombatRow.RANGE, 9, Ability.NONE, hero=True)]
        self.player = Player(0, Faction.NILFGAARD, self.deck_cards)

        for card in self.graveyard_cards:
            self.player.graveyard.add(card.combat_row, card)

        for card in self.hand:
            self.player.hand.add(card.combat_row, card)
