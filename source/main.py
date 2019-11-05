import random
import threading
import time
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
        self._gui_is_updated = threading.Event()
        threading.Thread(target=self._run_mcts, args=[self.environment.current_player]).start()
        self.master.after_idle(self._update_gui)
        self.master.mainloop()

    def _update_gui(self):
        if not self._gui_is_updated.is_set():
            self.gui.redraw()
            self.master.update()
            self.master.after_idle(self._gui_is_updated.set)
        self.master.after(1000, self._update_gui)

    def _run_mcts(self, current_player: Player, card_source: CardSource = CardSource.HAND):
        game_over = False

        while not game_over:
            self._gui_is_updated.clear()
            self._gui_is_updated.wait()

            mcts = MCTS(self.environment, current_player, card_source)
            card, row = mcts.run()
            game_over, current_player, card_source = self.environment.step(current_player, row, card)


if __name__ == '__main__':
    main = Main()
