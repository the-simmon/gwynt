from typing import List

from ..card import Card


def flatten(cards: List[any]) -> List[Card]:
    result = []
    for item in cards:
        if type(item) is Card:
            result.append(item)
        else:
            result.append(flatten(item))
    return result
