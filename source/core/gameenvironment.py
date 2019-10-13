from __future__ import annotations

import random
from collections import defaultdict
from typing import Tuple, List, Dict, Callable

from .board import Board
from .card import Card, CombatRow
from .player import Player


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player,
                 revive_func: Callable[[GameEnvironment, Player], Tuple[Card, CombatRow]]):
        self.player1 = player1
        self.player2 = player2
        self.revive_func = revive_func
        self.board = Board(player1, player2, revive_func, self)
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

    def step(self, player: Player, row: CombatRow = None, card: Card = None, pass_: bool = False) -> Tuple[bool, bool]:
        if not pass_:
            player.active_cards.remove(card.combat_row, card)
            self.board.add(player, row, card)
        else:
            self.passed[player] = True

        if len(player.active_cards.get_all_cards()) is 0:
            self.passed[player] = True

        if self.round_over():
            self._end_of_round()

        return self.round_over(), self.game_over()

    def round_over(self):
        return all(self.passed.values()) or self._player_won() or self.current_round is 2

    def game_over(self):
        return self._player_won() or self.current_round is 2

    def _player_won(self):
        return self.player1.rounds_won >= 2 or self.player2.rounds_won >= 2

    def repr_list(self, current_player: Player, excluded_card: Card) -> List[int]:
        current_round = [0] * 3
        current_round[self.current_round] = 1
        return self.board.repr_list(current_player, excluded_card) + current_round

    def _end_of_round(self):
        self.current_round += 1

        player1_damage = self.board.calculate_damage(self.player1)
        player2_damage = self.board.calculate_damage(self.player2)

        if player1_damage > player2_damage:
            self.player1.rounds_won += 1
        elif player1_damage < player2_damage:
            self.player2.rounds_won += 1
        else:
            self.player1.rounds_won += 1
            self.player2.rounds_won += 1

        self.board.all_cards_to_graveyard(self.player1)
        self.board.all_cards_to_graveyard(self.player2)
        self.passed = defaultdict(lambda: False)

    def __str__(self):
        result = ''
        result += str(self.player1.deck)
        result += '\n\n-----------------\n\n'
        result += str(self.board)
        result += '\n\n-----------------\n\n'
        result += str(self.player2.deck)
