from __future__ import annotations

import random
from collections import defaultdict
from typing import Tuple, List, Dict, TYPE_CHECKING

from .board import Board
from .card import Card, CombatRow
from .player import Player

if TYPE_CHECKING:
    from ..ai.abstract_ai import AbstractAI


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player, ai: AbstractAI):
        self.player1 = player1
        self.player2 = player2
        self.ai = ai
        self.board = Board(player1, player2, ai, self)
        self.current_round = 0
        self.passed: Dict[Player, bool] = {player1: False, player2: False}

        self._chose_active_cards()

    def _chose_active_cards(self):
        for player in [self.player1, self.player2]:

            #  random.choices not applicable, because it can return the same object multiple times
            deck_cards = player.deck.get_all_cards()
            random.shuffle(deck_cards)
            chosen_cards = deck_cards[:10]

            for card in chosen_cards:
                player.deck.remove(card.combat_row, card)
                player.active_cards.add(card.combat_row, card)

    def step(self, player: Player, row: CombatRow = None, card: Card = None, pass_: bool = False) -> bool:
        if not pass_:
            player.active_cards.remove(card.combat_row, card)
            self.board.add(player, row, card)
        else:
            self.passed[player] = True

        return all(self.passed.values()) or self._players_have_no_cards(
            player) or self._player_won() or self.current_round is 2

    def get_round_reward(self, player: Player) -> Tuple[int, bool]:
        game_finished = self._player_won() or self._players_have_no_cards(player) or self.current_round is 2
        reward = self._end_of_round(player)
        return reward, game_finished

    def get_game_reward(self, player: Player) -> int:
        reward = 100 if player.rounds_won == 2 else -100
        return reward

    def _players_have_no_cards(self, player):
        return len(player.active_cards.get_all_cards()) is 0

    def _player_won(self):
        return self.player1.rounds_won >= 2 or self.player2.rounds_won >= 2

    def repr_list(self, current_player: Player, excluded_card: Card) -> List[int]:
        current_round = [0] * 3
        current_round[self.current_round] = 1
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

        self.board.all_cards_to_graveyard(player)
        self.passed = defaultdict(lambda: False)

        if player is winner:
            reward = 10
        else:
            reward = -10
        return reward

    def __str__(self):
        result = ''
        result += str(self.player1.deck)
        result += '\n\n-----------------\n\n'
        result += str(self.board)
        result += '\n\n-----------------\n\n'
        result += str(self.player2.deck)
