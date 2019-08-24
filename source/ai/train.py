import random
from typing import List, Tuple

from source.ai.random_forest.randomforest import RandomForest
from source.core.card import Card
from source.core.gameenvironment import GameEnvironment
from source.core.player import Faction, Player
import source.core.cards as cards


def train():
    ai = RandomForest("random_forest")
    while True:
        player1, player2 = _get_players()
        environment = GameEnvironment(player1, player2)

        finished = False
        while not finished:
            ai.step(environment, player1)
            finished = ai.step(environment, player2)


def _get_players() -> Tuple[Player, Player]:
    faction = random.choice(list(Faction))
    cards = _get_cards(faction)
    player1 = Player(0, faction, cards)

    faction = random.choice(list(Faction))
    cards = _get_cards(faction)
    player2 = Player(1, faction, cards)

    return player1, player2


def _get_cards(faction: Faction) -> List[Card]:
    result = []

    if faction is Faction.MONSTER:
        result.extend(cards.monster)
    elif faction is Faction.NILFGAARD:
        result.extend(cards.nilfgaard)
    elif faction is Faction.NOTHERN_REALMS:
        result.extend(cards.nothern_realms)
    elif faction is Faction.Scoiatael:
        result.extend(cards.scoiatael)

    result.extend(cards.neutral)

    #  random.choices not applicable, because it can return the same object multiple times
    random.shuffle(result)

    return result[:22]


if __name__ == "__main__":
    train()
