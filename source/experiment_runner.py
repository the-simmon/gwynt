import multiprocessing

import sys
import logging

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard
from source.core.gameenvironment import GameEnvironment
from source.game_settings import GameSettings
from source.main import get_random_players


class ExperimentRunner:

    def __init__(self):
        self.cpu_cores = multiprocessing.cpu_count()
        self.log_file_name = sys.argv[1]
        logging.basicConfig(filename=f'../logs/{self.log_file_name}.txt', level=logging.INFO)
        GameSettings.PLAY_AGAINST_WITCHER = False
        GameSettings.SIMULATE_BOTH_PLAYERS = True

    def run(self, simulation_count: int):
        with multiprocessing.Pool(self.cpu_cores) as p:
            p.map(_run_game, range(simulation_count), chunksize=10)


def _run_game(_):
    player1, player2 = get_random_players()
    environment = GameEnvironment(player1, player2)
    environment.init()
    game_over = False
    while not game_over:
        current_player = environment.next_player
        mcts = MCTS(environment, current_player, max_time=1)

        card, row, replaced_card = mcts.run()
        if card and card.ability is Ability.DECOY:
            game_over = environment.step_decoy(current_player, row, card, replaced_card)
        elif type(card) is LeaderCard:
            game_over = environment.step_leader(current_player, card)
        else:
            game_over = environment.step(current_player, row, card)

    winner = environment.get_winner()
    winner_id = winner.id if winner else 0
    round = environment.current_round - 1
    logging.info(f'{winner_id}, {player1.rounds_won}, {player2.rounds_won}, {round}')


ExperimentRunner().run(200)
