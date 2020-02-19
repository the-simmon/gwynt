import asyncio
import random
from typing import Tuple

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard
from source.core.cards.util import get_cards, get_leaders
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction
from source.game_settings import GameSettings
from source.gui.asynctk import AsyncTK
from source.gui.card_loader import CardLoader
from source.gui.cookie_clicker import CookieClicker
from source.gui.game import Game


class Main:

    def __init__(self):
        self.master = AsyncTK()
        self.player1, self.player2 = None, None

        if GameSettings.PLAY_AGAINST_WITCHER:
            CardLoader(self.master, self.start_game).pack()
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
        self.gui = Game(self.master, self.environment, self.player1, self.clicker)
        self.gui.pack()
        self.master.after_idle(asyncio.create_task, self._start_game())

    async def _update_gui(self):
        self.gui.redraw()
        await self.master.redraw()

    async def _start_game(self):
        if not GameSettings.PLAY_AGAINST_WITCHER:
            self.environment.init()
        else:
            # the user has to select the current player
            self.environment.next_player = self.player1
        await self._update_gui()

        if GameSettings.SIMULATE_BOTH_PLAYERS:
            await self._run_mcts_both_players()
        else:
            while self.environment.next_player is not self.player1:
                await self._run_async_mcts(self.environment.next_player)

    async def _run_mcts_both_players(self):
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


def get_random_players() -> Tuple[Player, Player]:
    faction = random.choice(list(Faction))
    cards = get_cards(faction)
    leader = random.choice(get_leaders(faction))
    player1 = Player(0, faction, cards[:22], leader)

    faction = random.choice(list(Faction))
    cards = get_cards(faction)
    leader = random.choice(get_leaders(faction))
    player2 = Player(1, faction, cards[:22], leader)

    return player1, player2


if __name__ == '__main__':
    main = Main()
