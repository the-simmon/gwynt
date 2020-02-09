import random
from typing import List

from source.core.card import Card, LeaderCard
from source.core.cards.monster import cards as monster_cards
from source.core.cards.monster import leaders as monster_leaders
from source.core.cards.neutral import cards as neutral_cards
from source.core.cards.nilfgaard import cards as nilfgaard_cards
from source.core.cards.nilfgaard import leaders as nilfgaard_leaders
from source.core.cards.nothern_realms import cards as nothern_realms_cards
from source.core.cards.nothern_realms import leaders as nothern_realms_leaders
from source.core.cards.scoiatael import cards as scoiatael_cards
from source.core.cards.scoiatael import leaders as scoiatael_leaders
from source.core.player import Faction


def get_cards(faction: Faction) -> List[Card]:
    result = list(neutral_cards)
    if faction is Faction.MONSTER:
        result.extend(monster_cards)
    elif faction is Faction.NILFGAARD:
        result.extend(nilfgaard_cards)
    elif faction is Faction.NOTHERN_REALMS:
        result.extend(nothern_realms_cards)
    elif faction is Faction.SCOIATAEL:
        result.extend(scoiatael_cards)

    random.shuffle(result)
    return result


def get_leaders(faction: Faction) -> List[LeaderCard]:
    result = []
    if faction is Faction.MONSTER:
        result = monster_leaders
    elif faction is Faction.NILFGAARD:
        result = nilfgaard_leaders
    elif faction is Faction.NOTHERN_REALMS:
        result = nothern_realms_leaders
    elif faction is Faction.SCOIATAEL:
        result = scoiatael_leaders
    return result
