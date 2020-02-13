import random
from typing import Tuple

from source.core.cards.util import get_cards, get_leaders
from source.core.player import Player, Faction


def get_random_players() -> Tuple[Player, Player]:
    faction = random.choice(list(Faction))
    cards = get_cards(faction)
    leader = random.choice(get_leaders(faction))
    player1 = Player(0, faction, cards[:22], leader)

    faction = random.choice(list(Faction))
    cards = get_cards(faction)
    leader = random.choice(get_leaders(faction))
    player2 = Player(1, faction, cards[:22], leader)

    return player1, player2