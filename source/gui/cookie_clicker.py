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

    def card_click(self, player: Player, row: CombatRow, card: Card):
        if self.environment.current_player is player:
            game_over, current_player, card_source = self.environment.step(player, row, card)
            self.gui_is_updated.clear()
            if current_player is not player:
                threading.Thread(target=self._run_mcts, args=[game_over, current_player, card_source]).start()

    def _run_mcts(self, game_over: bool, player: Player, card_source: CardSource):
        self.gui_is_updated.wait()
        current_player = player
        # play enemy cards
        while current_player is player and not game_over:
            game_over, current_player, card_source = self.mcts(current_player, card_source)
