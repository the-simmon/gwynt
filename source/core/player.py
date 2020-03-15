import enum
import random
from typing import List

from source.core.card import Card, LeaderCard
from source.core.cardcollection import CardCollection


class Faction(enum.Enum):
    MONSTER = 0
    NILFGAARD = 1
    NORTHERN_REALMS = 2
    SCOIATAEL = 3


class Player:

    def __init__(self, id: int, faction: Faction, cards: List[Card], leader: LeaderCard):
        self.id: int = id
        self.faction = faction
        self.deck = CardCollection(cards)
        self.graveyard = CardCollection([])
        self.hand = CardCollection([])
        self.leader = leader
        self.rounds_won = 0

    def pick_random_from_deck(self):
        cards = self.deck.get_all_cards()
        if cards:
            card = random.choice(cards)
            self.deck.remove(card.combat_row, card)
            self.hand.add(card.combat_row, card)
