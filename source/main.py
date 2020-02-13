import asyncio

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player
from source.get_random_players import get_random_players
from source.gui.asynctk import AsyncTK
from source.gui.card_loader import CardLoader
from source.gui.cookie_clicker import CookieClicker
from source.gui.game import Game

simulate_both_players = False
play_against_witcher = True


class Main:

    def __init__(self):
        self.master = AsyncTK()
        self.player1, self.player2 = None, None

        if play_against_witcher:
            CardLoader(self.start_game).pack(in_=self.master)
        else:
            player1, player2 = get_random_players()
            self.master.after_idle(self.start_game, player1, player2)

        self.environment = None
        self.clicker = None
        self.gui = None
        self.master.mainloop()

    def start_game(self, player1: Player, player2: Player):
        self.player1, self.player2 = player1, player2
        self.environment = GameEnvironment(player1, player2)
        self.clicker = CookieClicker(self.environment, self._run_async_mcts, self._update_gui)
        self.gui = Game(self.environment, self.player1, self.clicker)
        self.gui.pack(in_=self.master)
        self.master.after_idle(asyncio.create_task, self._start_game())

    async def _update_gui(self):
        self.gui.redraw()
        await self.master.redraw()

    async def _start_game(self):
        if not play_against_witcher:
            self.environment.init()
        else:
            # the user has to select the current player
            self.environment.next_player = self.player1
        await self._update_gui()

        if simulate_both_players:
            await self._run_mcts_both_players(self.environment.next_player)
        else:
            while self.environment.next_player is not self.player1:
                await self._run_async_mcts(self.environment.next_player)

    async def _run_mcts_both_players(self, current_player: Player):
        game_over = False

        while not game_over:
            game_over = await self._run_async_mcts(self.environment.next_player)

    async def _run_async_mcts(self, current_player: Player) -> bool:
        result = await asyncio.get_event_loop().run_in_executor(None, self._run_mcts, current_player)
        await self._update_gui()
        return result

    def _run_mcts(self, current_player: Player) -> bool:
        mcts = MCTS(self.environment, current_player)
        card, row, replaced_card = mcts.run()
        if card and card.ability is Ability.DECOY:
            game_over = self.environment.step_decoy(current_player, row, card, replaced_card)
        elif type(card) is LeaderCard:
            game_over = self.environment.step_leader(current_player, card)
        else:
            game_over = self.environment.step(current_player, row, card)

        return game_over


if __name__ == '__main__':
    main = Main()
