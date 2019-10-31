import tkinter as tk

from source.core.card import CombatRow
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player
from source.gui.board import Board
from source.gui.card import Card


class Game(tk.Frame):
    WIDTH = 1920 / 2
    HEIGHT = 1080

    def __init__(self, environment: GameEnvironment, player: Player):
        super().__init__(width=Game.WIDTH, height=Game.HEIGHT)
        self.environment = environment
        self.player = player
        self.board = Board(environment.board, player)

        self.info_frame = tk.Frame(self)
        self.info_frame.grid(column=0, row=0, padx=5)

        self.damage_frame = tk.Frame(self)
        self.damage_frame.grid(column=1, row=0)

        self.board.grid(in_=self, column=2, row=0)

    def redraw(self):
        self._clear_frame()
        self._draw_info_frame()
        self._draw_damage_frame()
        self.board.redraw()

    def _clear_frame(self):
        for widget in self.damage_frame.winfo_children():
            widget.destroy()

        for widget in self.info_frame.winfo_children():
            widget.destroy()

    def _draw_info_frame(self):
        tk.Label(self.info_frame, text=f'Weather: {self.environment.board.weather.name}').pack(anchor=tk.N)

        enemy = self.environment.board.get_enemy_player(self.player)
        tk.Label(self.info_frame, text=f'Enemy: {enemy.rounds_won}').pack()
        tk.Label(self.info_frame, text=f'Self: {self.player.rounds_won}').pack()

        current_player = 'Self' if self.environment.current_player.id == self.player.id else 'Enemy'
        tk.Label(self.info_frame, text=f'Current player: {current_player}').pack()

        tk.Frame(self.info_frame, height=Card.HEIGHT).pack()
        core_board = self.environment.board

        damage = core_board.calculate_damage(enemy)
        tk.Label(self.info_frame, text=f'Enemy damage: {damage}').pack()

        damage = core_board.calculate_damage(self.player)
        tk.Label(self.info_frame, text=f'Own damage: {damage}').pack()

    def _draw_damage_frame(self):
        combat_row_sorting = [CombatRow.SIEGE, CombatRow.RANGE, CombatRow.CLOSE]
        core_board = self.environment.board

        for player in [core_board.get_enemy_player(self.player), self.player]:
            for row in combat_row_sorting:
                damage = core_board.cards[player].calculate_damage_for_row(row, core_board.weather)
                text = tk.Label(self.damage_frame, text=F'{row.name}: {damage}')
                text.pack()
                tk.Frame(self.damage_frame, height=Card.HEIGHT).pack()
            combat_row_sorting.reverse()
