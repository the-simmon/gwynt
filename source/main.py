import random
import tkinter as tk

from source.ai.mcts.mcts import MCTS
from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Faction, Player
from source.gui.game import Game


class Main:

    def __init__(self):
        self.master = tk.Tk()
        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        self.player1 = Player(0, faction, cards[:22])

        faction = random.choice(list(Faction))
        cards = get_cards(faction)
        self.player2 = Player(1, faction, cards[:22])

        self.environment = GameEnvironment(self.player1, self.player2)
        self.gui = Game(self.environment, self.player1)

        self.gui.pack(in_=self.master)
        self.master.after(1, self.gui.redraw)
        self.master.after(100, self._run_mcts, self.environment.current_player)
        self.master.mainloop()

    def _run_mcts(self, player: Player, card_source: CardSource = CardSource.HAND):
        mcts = MCTS(self.environment, player, card_source)
        card, row = mcts.run()
        game_over, current_player, card_source = self.environment.step(player, row, card)

        self.gui.redraw()
        if not game_over:
            self.master.after(0, self._run_mcts, current_player, card_source)


if __name__ == '__main__':
    main = Main()
