import random
from typing import List, Tuple

from source.core.card import Card, Ability, LeaderCard
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment) -> Player:
    game_over = environment.game_over()
    while not game_over:
        potential_cards = _get_potential_cards(environment)
        if leader := environment.next_player.leader:
            potential_cards.append(leader)
        potential_cards.append(None)  # None == pass

        random_card = random.choice(potential_cards)

        if random_card:
            row = random.choice(CombatRow.get_possible_rows(random_card))
        else:
            row = None

        if random_card and random_card.ability is Ability.DECOY and environment.next_card_source is CardSource.HAND:
            row, card = _get_decoy(environment)
            if card:
                game_over = environment.step_decoy(environment.next_player, row, random_card, card)
        elif type(random_card) is LeaderCard:
            game_over = environment.step_leader(environment.next_player, random_card)
        else:
            game_over = environment.step(environment.next_player, row, random_card)

    return environment.get_winner()


def _get_potential_cards(environment: GameEnvironment) -> List[Card]:
    return environment.card_tracker.get_possible_cards(False)


def _get_decoy(environment: GameEnvironment) -> Tuple[CombatRow, Card]:
    card_collection = environment.board.cards[environment.next_player.id]
    try:
        row = random.choice(list(card_collection.keys()))
        card = random.choice(card_collection[row])
    except IndexError:
        row, card = None, None

    return row, card
