import random
from typing import Tuple

from source.ai.mcts.mcts import MCTS
from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Faction, Player
from source.gui.cookie_clicker import CookieClicker
from source.gui.gui import GUI

simulate_both_players = False


class Main:

    def __init__(self):
        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        self.player1 = Player(0, faction, cards[:22])

        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        self.player2 = Player(1, faction, cards[:22])

        self.environment = GameEnvironment(self.player1, self.player2)

        self.clicker = CookieClicker(self.environment, self._run_mcts, self._update_gui)

        self.gui = GUI(self.environment, self.player1, self.clicker)
        self.gui.after(1000, self._start_game)
        self.gui.mainloop()

    def _update_gui(self):
        self.gui.redraw()

    def _start_game(self):
        if simulate_both_players:
            self._run_mcts_both_players(self.environment.current_player)
        else:
            while self.environment.current_player is not self.player1:
                self._run_mcts(self.environment.current_player, self.environment.current_card_source)

    def _run_mcts_both_players(self, current_player: Player, card_source: CardSource = CardSource.HAND):
        game_over = False

        while not game_over:
            game_over, current_player, card_source = self._run_mcts(current_player, card_source)

    def _run_mcts(self, current_player: Player, card_source: CardSource = CardSource.HAND) \
            -> Tuple[bool, Player, CardSource]:
        mcts = MCTS(self.environment, current_player, card_source)
        card, row = mcts.run()
        game_over, current_player, card_source = self.environment.step(current_player, row, card)

        return game_over, current_player, card_source


if __name__ == '__main__':
    main = Main()
