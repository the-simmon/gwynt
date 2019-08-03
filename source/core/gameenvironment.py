import random
from collections import defaultdict
from typing import Tuple, DefaultDict, List

from .card import Card, CombatRow
from .board import Board
from .player import Player


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.board = Board(player1, player2)
        self.current_round = 0
        self.passed: DefaultDict[Player, bool] = defaultdict(lambda: False)

        self.chose_active_cards()

    def chose_active_cards(self):
        for player in [self.player1, self.player2]:
            chosen_cards = random.choices(player.deck.get_all_cards(), k=10)

            for card in chosen_cards:
                player.deck.remove(card)
                player.active_cards.add(card)

    def step(self, player: Player, row: CombatRow, card: Card, pass_=False) -> Tuple[int, bool]:
        if not pass_:
            self.board.add(player, row, card)
        else:
            self.passed[player] = True

        reward = 0
        if all(self.passed.values()):
            reward = self._end_of_round()

        done = False
        if self.player1.rounds_won > 2 or self.player2.rounds_won > 2:
            done = True
            reward += 100
        return reward, done

    def repr_list(self, current_player: Player, excluded_card: Card) -> List[int]:
        current_round = [0] * 3
        current_player[self.current_round] = 1
        return self.board.repr_list(current_player, excluded_card) + current_round

    def _end_of_round(self, player: Player) -> int:
        self.current_round += 1

        player1_damage = self.board.calculate_damage(self.player1)
        player2_damage = self.board.calculate_damage(self.player2)

        winner = None
        if player1_damage > player2_damage:
            self.player1.rounds_won += 1
            winner = self.player1
        elif player1_damage < player2_damage:
            self.player2.rounds_won += 1
            winner = self.player2
        else:
            self.player1.rounds_won += 1
            self.player2.rounds_won += 1

        self.board.all_cards_to_graveyard()
        self.passed = defaultdict(lambda: False)

        reward = 0
        if player is winner:
            reward = 10
        return reward
