import random

from source.core.cards.monster import cards as monster_cards
from source.core.cards.neutral import cards as neutral_cards
from source.core.cards.nilfgaard import cards as niflgaard_cards
from source.core.cards.nothern_realms import cards as nothern_reamls_cards
from source.core.cards.scoiatael import cards as scoiatael_cards
from source.core.player import Faction


def get_cards(faction: Faction):
    result = neutral_cards
    if faction is Faction.MONSTER:
        result.extend(monster_cards)
    elif faction is Faction.NILFGAARD:
        result.extend(niflgaard_cards)
    elif faction is Faction.NOTHERN_REALMS:
        result.extend(nothern_reamls_cards)
    elif faction is Faction.SCOIATAEL:
        result.extend(scoiatael_cards)

    random.shuffle(result)
    return result
