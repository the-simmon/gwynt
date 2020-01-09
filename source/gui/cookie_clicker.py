import asyncio
from typing import Callable, Tuple

from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player

_MCTS = Callable[[Player, CardSource], Tuple[bool, Player, CardSource]]
_UPDATE_GUI = Callable


def _run_asyncio_executor(update_gui: Callable, func: Callable, *args):
    async def _run_func():
        # todo: potentiel yield in func verwenden und dann ne while hier in der funktion
        await asyncio.get_event_loop().run_in_executor(None, func, *args)
        update_gui()

    asyncio.create_task(_run_func())


class CookieClicker:

    def __init__(self, environment: GameEnvironment, mcts: _MCTS, update_gui: _UPDATE_GUI):
        self.environment = environment
        self.mcts = mcts
        self.update_ui = update_gui

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
        else:
            possible_rows = []

        if self.environment.current_player is player and row in possible_rows:
            game_over, current_player, card_source = self.environment.step(player, row, card)
            self.update_ui()
            if current_player is not player:
                _run_asyncio_executor(self.update_ui, self._run_mcts, game_over, current_player, card_source)

    def pass_click(self, player: Player):
        if self.environment.current_player is player:
            game_over, current_player, card_source = self.environment.step(player, None, None)
            self.update_ui()
            if current_player is not player:
                _run_asyncio_executor(self.update_ui, self._run_mcts, game_over, current_player, card_source)

    def _run_mcts(self, game_over: bool, player: Player, card_source: CardSource):
        current_player = player
        # play enemy cards
        while current_player is player and not game_over:
            game_over, current_player, card_source = self.mcts(current_player, card_source)
