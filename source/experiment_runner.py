import logging
import multiprocessing
import random
import sys
from collections import Counter
from copy import deepcopy
from typing import Tuple, Union

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard, Card
from source.core.cardcollection import CardCollection
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player
from source.game_settings import GameSettings
from source.main import get_random_players


class ExperimentRunner:

    def __init__(self):
        self.cpu_cores = round(multiprocessing.cpu_count() / 2)
        self.log_file_name = sys.argv[1]
        logging.basicConfig(filename=f'../logs/{self.log_file_name}.txt', level=logging.INFO)
        GameSettings.PLAY_AGAINST_WITCHER = False
        GameSettings.SIMULATE_BOTH_PLAYERS = True

    def run(self, simulation_count: int):
        logging.info('------')
        with multiprocessing.Pool(self.cpu_cores) as p:
            p.map(_run_game, range(simulation_count), chunksize=10)


def _run_game(_):
    player1, player2 = get_random_players()
    environment = GameEnvironment(player1, player2)
    environment.init()
    game_over = False
    while not game_over:
        current_player = environment.next_player

        card, row, replaced_card = get_mcts_result(environment)

        if card and card.ability is Ability.DECOY and environment.next_card_source is CardSource.HAND:
            game_over = environment.step_decoy(current_player, row, card, replaced_card)
        elif type(card) is LeaderCard:
            game_over = environment.step_leader(current_player, card)
        else:
            game_over = environment.step(current_player, row, card)

    player1_cards = len(player1.hand.get_all_cards())
    player2_cards = len(player2.hand.get_all_cards())
    text = f'{player1.rounds_won},{player2.rounds_won},{player1.faction},{player2.faction},{player1_cards},{player2_cards}'
    logging.info(text)


def get_mcts_result(environment: GameEnvironment) -> Tuple[Union[Card, LeaderCard], CombatRow, Card]:
    current_player = environment.next_player
    if current_player.id == 1:
        GameEnvironment.BLOCK_OBFUSCATE = True
        card, row, replaced_card = run_determinazition(environment)
    else:
        GameEnvironment.BLOCK_OBFUSCATE = False
        mcts = MCTS(environment, current_player)
        card, row, replaced_card = mcts.run()

    return card, row, replaced_card


def run_determinazition(environment: GameEnvironment) -> Tuple[Union[Card, LeaderCard], CombatRow, Card]:
    counter = Counter()
    for _ in range(10):
        environment_copy = deepcopy(environment)
        environment_copy.player1 = add_random_cards_to_player(environment_copy.player1, environment_copy)
        mcts = MCTS(environment_copy, environment_copy.next_player, max_time=0.5)
        card, row, replaced_card = mcts.run()
        counter.update({(card, row, replaced_card): 1})
    return counter.most_common(1)[0][0]


def add_random_cards_to_player(player_to_add_cards: Player, environment: GameEnvironment) -> Player:
    player_to_add_cards = deepcopy(player_to_add_cards)
    all_cards = environment.card_tracker.get_possible_cards(True)
    total_hand = len(player_to_add_cards.hand.get_all_cards())
    random.shuffle(all_cards)

    player_to_add_cards.hand = CardCollection(all_cards[:total_hand + 1])
    player_to_add_cards.deck = CardCollection(all_cards[total_hand + 1:])

    return player_to_add_cards


ExperimentRunner().run(600)
