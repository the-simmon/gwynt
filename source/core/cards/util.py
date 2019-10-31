import random

from source.core.player import Faction
from .monster import cards as monster_cards
from .neutral import cards as neutral_cards
from .nilfgaard import cards as niflgaard_cards
from .nothern_realms import cards as nothern_reamls_cards
from .scoiatael import cards as scoiatael_cards


def get_cards(faction: Faction):
    result = neutral_cards
    if faction is Faction.MONSTER:
        result.extend(monster_cards)
    elif faction is Faction.NILFGAARD:
        result.extend(niflgaard_cards)
    elif faction is Faction.NOTHERN_REALMS:
        result.extend(nothern_reamls_cards)
    elif faction is Faction.Scoiatael:
        result.extend(scoiatael_cards)

    random.shuffle(result)
    return result
