from typing import List

from source.core.card import Card


def flatten(cards: List[any]) -> List[Card]:
    result = []
    for item in cards:
        if type(item) is Card:
            result.append(item)
        else:
            result.extend(flatten(item))
    return result
