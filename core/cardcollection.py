from collections import defaultdict
from typing import DefaultDict, List
from .card import CombatRow, Card


class CardCollection:

    def __init__(self, max_cards: int, cards: List[Card]):
        self.max_cards = max_cards
        self.cards: DefaultDict[CombatRow, List[Card]] = defaultdict(list)

        for card in cards:
            self.cards[card.combat_row].append(card)

    def add(self, row: CombatRow, card: Card):
        self.cards[row].append(card)

    def remove(self, row: CombatRow, card: Card):
        self.cards[row].remove(card)

    def repr_list(self) -> List[int]:
        result = []
        for row, cards in self.cards.items():
            result.extend(self._one_hot_from_row(row, cards))
        return result

    def _one_hot_from_row(self, row: CombatRow, cards: List[Card]) -> List[int]:
        result = []
        counter = 0
        for i, card in enumerate(cards):
            result.extend(card.repr_list())
            counter = i

        if counter < self.max_cards:
            for _ in range(self.max_cards - counter):
                result.extend(Card.empty_card_repr(row))

        return result

    def __len__(self):
        length = 0
        for cards in self.cards.values():
            length += len(cards)
        return length


