import random
from typing import Tuple

from source.ai.mcts.mcts import MCTS
from source.core.card import CombatRow, Card
from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction

player0_cards = get_cards(Faction.NOTHERN_REALMS)
random.shuffle(player0_cards)
player0 = Player(0, Faction.NOTHERN_REALMS, player0_cards[:22])

player1_cards = get_cards(Faction.NILFGAARD)
random.shuffle(player1_cards)
player1 = Player(1, Faction.NILFGAARD, player1_cards[:22])


def revive(environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
    card = random.choice(player.graveyard.get_all_cards())
    return card, random.choice(CombatRow.get_possible_rows(card.combat_row))


environment = GameEnvironment(player0, player1, revive)

current_player = player0
while environment.current_round < 2:
    mcts = MCTS(environment, current_player)
    card, row = mcts.run()
    environment.step(current_player, row, card)

    current_player = environment.board.get_enemy_player(current_player)
