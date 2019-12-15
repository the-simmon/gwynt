import threading
from typing import Callable, Tuple

from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player

_MCTS = Callable[[Player, CardSource], Tuple[bool, Player, CardSource]]


class CookieClicker:

    def __init__(self, environment: GameEnvironment, gui_is_updated: threading.Event, mcts: _MCTS):
        self.environment = environment
        self.gui_is_updated = gui_is_updated
        self.mcts = mcts

        self._last_clicked_card: Card = None
        self._last_clicked_player: Player = None

    def card_click(self, player: Player, card: Card):
        self._last_clicked_player = player
        self._last_clicked_card = card

        # place card immediately, if only one combat row is possible
        if len(possible_rows := CombatRow.get_possible_rows(card)) == 1:
            self.click_row(possible_rows[0])
            self._last_clicked_card = None
            self._last_clicked_player = None

    def click_row(self, row: CombatRow):
        player = self._last_clicked_player
        card = self._last_clicked_card

        if self._last_clicked_card:
            possible_rows = CombatRow.get_possible_rows(self._last_clicked_card)

        if self.environment.current_player is player and row in possible_rows:
            game_over, current_player, card_source = self.environment.step(player, row, card)
            self.gui_is_updated.clear()
            if current_player is not player:
                threading.Thread(target=self._run_mcts, args=[game_over, current_player, card_source]).start()

    def pass_click(self, player: Player):
        if self.environment.current_player is player:
            game_over, current_player, card_source = self.environment.step(player, None, None)
            self.gui_is_updated.clear()
            if current_player is not player:
                threading.Thread(target=self._run_mcts, args=[game_over, current_player, card_source]).start()

    def _run_mcts(self, game_over: bool, player: Player, card_source: CardSource):
        # wait for gui update before 'blocking' the GIL
        self.gui_is_updated.wait()
        current_player = player
        # play enemy cards
        while current_player is player and not game_over:
            game_over, current_player, card_source = self.mcts(current_player, card_source)
