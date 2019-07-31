import random
from typing import List

from source.core.card import CombatRow
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
        self.active_cards = CardCollection(max_cards=22, cards=[])

    def pick_random_from_deck(self):
        cards = []
        for row in CombatRow:
            cards.extend(self.deck[row])

        card = random.choice(cards)
        self.deck.remove(card.combat_row, card)
        self.active_cards.add(card.combat_row, card)

    def repr_list(self, include_deck_and_active=False, exclude_card: Card = None) -> List[int]:
        result = self.faction.one_hot() + self.graveyard.repr_list()
        if include_deck_and_active:
            result.extend(self.deck.repr_list())
            result.extend(self.active_cards.repr_list(exclude_card))
        return result
