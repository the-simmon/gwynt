from collections import defaultdict
from typing import DefaultDict
from .card import CombatRow, Card
from .cardcollection import CardCollection
from .player import Player


class Board:

    def __init__(self):
        self.cards: DefaultDict[Player, CardCollection] = defaultdict(CardCollection)

    def add(self, player: Player, row: CombatRow, card: Card):
        self.cards[player].add(row, card)

    def remove(self, player: Player, row: CombatRow, card: Card):
        self.cards[player].remove(row, card)
