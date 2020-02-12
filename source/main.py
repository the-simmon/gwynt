import asyncio
import random

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, LeaderCard
from source.core.cards.util import get_cards, get_leaders
from source.core.gameenvironment import GameEnvironment
from source.core.player import Faction, Player
from source.gui.cookie_clicker import CookieClicker
from source.gui.gui import GUI

simulate_both_players = False


class Main:

    def __init__(self):
        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        leader = random.choice(get_leaders(faction))
        self.player1 = Player(0, faction, cards[:22], leader)

        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        leader = random.choice(get_leaders(faction))
        self.player2 = Player(1, faction, cards[:22], leader)

        self.environment = GameEnvironment(self.player1, self.player2)

        self.clicker = CookieClicker(self.environment, self._run_async_mcts, self._update_gui)

        self.gui = GUI(self.environment, self.player1, self.clicker)
        self.gui.after_idle(asyncio.create_task, self._start_game())
        self.gui.mainloop()

    async def _update_gui(self):
        await self.gui.redraw()

    async def _start_game(self):
        self.environment.init()
        await self._update_gui()

        if simulate_both_players:
            await self._run_mcts_both_players(self.environment.next_player)
        else:
            while self.environment.next_player is not self.player1:
                await self._run_async_mcts(self.environment.next_player)

    async def _run_mcts_both_players(self, current_player: Player):
        game_over = False

        while not game_over:
            game_over = await self._run_async_mcts(current_player)

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
