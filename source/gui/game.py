import tkinter as tk

from source.core.card import CombatRow
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player
from source.gui.board import Board
from source.gui.card import Card


class Game(tk.Frame):
    WIDTH = 1920
    HEIGHT = 1080

    def __init__(self, environment: GameEnvironment, player: Player):
        super().__init__(width=Game.WIDTH, height=Game.HEIGHT)
        self.environment = environment
        self.player = player
        self.board = Board(environment.board, player)
        self.frame = tk.Frame()
        self.frame.grid(in_=self)
        self.board.grid(in_=self, column=1, row=0)

    def redraw(self):
        self._clear_frame()
        self.board.redraw()

        combat_row_sorting = [CombatRow.SIEGE, CombatRow.RANGE, CombatRow.CLOSE]
        core_board = self.environment.board

        for player in [core_board.get_enemy_player(self.player), self.player]:
            for row in combat_row_sorting:
                damage = core_board.cards[player].calculate_damage_for_row(row, core_board.weather)
                text = tk.Label(text=str(damage))
                text.pack(in_=self.frame)
                tk.Frame(height=Card.HEIGHT * 1.1).pack(in_=self.frame)
            combat_row_sorting.reverse()

    def _clear_frame(self):
        for widget in self.frame.children:
            widget.destroy()
