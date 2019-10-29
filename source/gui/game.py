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

        self.info_frame = tk.Frame()
        self.info_frame.grid(in_=self, column=0, row=0, padx=5)

        self.damage_frame = tk.Frame()
        self.damage_frame.grid(in_=self, column=1, row=0)

        self.board.grid(in_=self, column=2, row=0)

    def redraw(self):
        self._clear_frame()
        self._draw_info_frame()
        self._draw_damage_frame()
        self.board.redraw()

    def _clear_frame(self):
        for widget in self.damage_frame.children:
            widget.destroy()

        for widget in self.info_frame.children:
            widget.destroy()

    def _draw_info_frame(self):
        tk.Label(text=f'Weather: {self.environment.board.weather.name}').pack(in_=self.info_frame, anchor=tk.N)
        tk.Frame(height=Card.HEIGHT).pack(in_=self.info_frame)

        enemy = self.environment.board.get_enemy_player(self.player)
        tk.Label(text=f'Enemy: {enemy.rounds_won}').pack(in_=self.info_frame)
        tk.Frame(height=Card.HEIGHT * 3).pack(in_=self.info_frame)
        tk.Label(text=f'Self: {self.player.rounds_won}').pack(in_=self.info_frame)

    def _draw_damage_frame(self):
        combat_row_sorting = [CombatRow.SIEGE, CombatRow.RANGE, CombatRow.CLOSE]
        core_board = self.environment.board

        for player in [core_board.get_enemy_player(self.player), self.player]:
            for row in combat_row_sorting:
                damage = core_board.cards[player].calculate_damage_for_row(row, core_board.weather)
                text = tk.Label(text=F'{row.name}: {damage}')
                text.pack(in_=self.damage_frame)
                tk.Frame(height=Card.HEIGHT).pack(in_=self.damage_frame)
            combat_row_sorting.reverse()
