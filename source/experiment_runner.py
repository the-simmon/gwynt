import logging
import multiprocessing
import sys

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard
from source.core.gameenvironment import GameEnvironment
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
        max_time = 5 if current_player.id == 0 else 8
        mcts = MCTS(environment, current_player, max_time)

        card, row, replaced_card = mcts.run()
        if card and card.ability is Ability.DECOY:
            game_over = environment.step_decoy(current_player, row, card, replaced_card)
        elif type(card) is LeaderCard:
            game_over = environment.step_leader(current_player, card)
        else:
            game_over = environment.step(current_player, row, card)

    player1_cards = len(player1.hand.get_all_cards())
    player2_cards = len(player2.hand.get_all_cards())
    text = f'{player1.rounds_won},{player2.rounds_won},{player1.faction},{player2.faction},{player1_cards},{player2_cards}'
    logging.info(text)


ExperimentRunner().run(200)
