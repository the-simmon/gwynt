import random
from typing import List

from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment, current_player: Player, card_source: CardSource) -> Player:
    game_over = environment.game_over()
    while not game_over:
        potential_cards = _get_potential_cards(current_player, card_source)
        potential_cards.append(None)  # None == pass

        random_card = random.choice(potential_cards)
        if random_card:
            row = random.choice(CombatRow.get_possible_rows(random_card))
        else:
            row = None
        game_over, current_player, card_source = environment.step(current_player, row, random_card)

    return environment.get_winner()


def _get_potential_cards(player: Player, next_card_source: CardSource) -> List[Card]:
    if next_card_source is CardSource.HAND:
        return player.active_cards.get_all_cards()
    return player.graveyard.get_all_cards()
