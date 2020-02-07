import asyncio
from typing import Callable, Tuple, Awaitable

from source.core.card import Card, Ability
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player

_MCTS = Callable[[Player], Awaitable[bool]]
_UPDATE_GUI = Callable[[], Awaitable]


class CookieClicker:

    def __init__(self, environment: GameEnvironment, mcts: _MCTS, update_gui: _UPDATE_GUI):
        self.environment = environment
        self.mcts = mcts
        self.update_ui = update_gui

        self._last_clicked_card: Card = None
        self._last_clicked_player: Player = None

    def card_click(self, player: Player, row: CombatRow, card: Card):
        if self._last_clicked_card and self._last_clicked_card.ability is Ability.DECOY:
            asyncio.create_task(self._decoy(card, row))
        else:
            self._last_clicked_player = player
            self._last_clicked_card = card

            # place card immediately, if only one combat row is possible
            if len(possible_rows := CombatRow.get_possible_rows(card)) == 1:
                self.click_row(possible_rows[0])

    async def _decoy(self, replace: Card, row: CombatRow):
        decoy = self._last_clicked_card
        if self.environment.next_player is self._last_clicked_player:
            game_over = self.environment.step_decoy(self._last_clicked_player, row, decoy,
                                                    replace)
            await self.update_ui()
            if self.environment.next_player is not self._last_clicked_player:
                await self._run_mcts(game_over, self.environment.next_player)

        self._last_clicked_player = None
        self._last_clicked_card = None

    def click_row(self, row: CombatRow):
        """Wrapper function because tkinter cant execute coroutine directly"""
        asyncio.create_task(self._async_click_row(row))

    async def _async_click_row(self, row: CombatRow):
        player = self._last_clicked_player
        clicked_card = self._last_clicked_card
        self._last_clicked_card = None
        self._last_clicked_player = None

        if clicked_card:
            possible_rows = CombatRow.get_possible_rows(clicked_card)
        else:
            possible_rows = []

        if self.environment.next_player is player and row in possible_rows:
            game_over = self.environment.step(player, row, clicked_card)
            await self.update_ui()
            if self.environment.next_player is not player:
                await self._run_mcts(game_over, self.environment.next_player)

    def pass_click(self, player: Player):
        """Wrapper function because tkinter cant execute coroutine directly"""
        asyncio.create_task(self._async_pass_click(player))

    async def _async_pass_click(self, player: Player):
        if self.environment.next_player is player:
            game_over = self.environment.step(player, None, None)
            await self.update_ui()
            if self.environment.next_player is not player:
                await self._run_mcts(game_over, self.environment.next_player)

    async def _run_mcts(self, game_over: bool, player: Player):
        # play enemy cards
        while self.environment.next_player is player and not game_over:
            game_over = await self.mcts(self.environment.next_player)
