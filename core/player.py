import random
from typing import List
from .cardcollection import CardCollection
from .card import Card
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
        self.active_cards = CardCollection(max_cards=10, cards=[])

    def pick_random_from_deck(self):
        self.active_cards.add(random.choice(self.deck.cards))

    def repr_list(self, include_deck=False) -> List[int]:
        result = self.faction.one_hot() + self.graveyard.repr_list() + self.active_cards.repr_list()
        if include_deck:
            result.extend(self.deck.repr_list())
        return result
