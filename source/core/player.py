import random
from typing import List

from .card import Card
from .cardcollection import CardCollection
from .one_hot_enum import OneHotEnum


class Faction(OneHotEnum):
    MONSTER = 0
    NILFGAARD = 1
    NOTHERN_REALMS = 2
    Scoiatael = 3


class Player:

    def __init__(self, id: int, faction: Faction, cards: List[Card]):
        self.id = id
        self.faction = faction
        self.deck = CardCollection(max_cards=22, cards=cards)
        self.graveyard = CardCollection(max_cards=22, cards=[])
        self.active_cards = CardCollection(max_cards=22, cards=[])
        self.rounds_won = 0

    def pick_random_from_deck(self):
        cards = self.deck.get_all_cards()
        if cards:
            card = random.choice(cards)
            self.deck.remove(card.combat_row, card)
            self.active_cards.add(card.combat_row, card)

    def __eq__(self, other):
        return other is not None and self.id is other.id

    def __hash__(self):
        return hash(self.id) + hash(self.faction) + hash(self.rounds_won)
