import tkinter as tk
from functools import partial

from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player
from source.gui.board import Board
from source.gui.card import Card
from source.gui.cookie_clicker import CookieClicker
from source.gui.cheat_menu import CheatMenu


class Game(tk.Frame):
    WIDTH = 1920 / 2
    HEIGHT = 1080

    def __init__(self, master, environment: GameEnvironment, player: Player, clicker: CookieClicker):
        super().__init__(master, width=Game.WIDTH, height=Game.HEIGHT)
        self.environment = environment
        self.player = player
        self.clicker = clicker
        self.board = Board(self, environment, environment.board, player, clicker)

        self.info_frame = tk.Frame(self)
        self.info_frame.grid(column=0, row=0, padx=5)

        self.damage_frame = tk.Frame(self)
        self.damage_frame.grid(column=1, row=0)

        self.board.grid(column=2, row=0)

        self.cheat_menu = CheatMenu(self, self.environment, self.redraw)
        self.cheat_menu.grid(column=3, row=0)

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
        weather_string = ''
        for weather in self.environment.board.weather:
            weather_string += f'{weather.name}, '

        tk.Label(self.info_frame, text=f'Weather: {weather_string}').pack(anchor=tk.N)

        enemy = self.environment.board.get_enemy_player(self.player)
        tk.Label(self.info_frame, text=f'Enemy: {enemy.rounds_won}').pack()
        tk.Label(self.info_frame, text=f'Self: {self.player.rounds_won}').pack()

        current_player = 'Self' if self.environment.next_player.id == self.player.id else 'Enemy'
        tk.Label(self.info_frame, text=f'Current player: {current_player}').pack()
        tk.Label(self.info_frame, text=f'Enemy cards: {len(enemy.hand.get_all_cards())}').pack()

        tk.Frame(self.info_frame, height=Card.HEIGHT).pack()
        core_board = self.environment.board

        damage = core_board.calculate_damage(enemy)
        tk.Label(self.info_frame, text=f'Enemy damage: {damage}').pack()

        damage = core_board.calculate_damage(self.player)
        tk.Label(self.info_frame, text=f'Own damage: {damage}').pack()

        tk.Frame(self.info_frame, height=Card.HEIGHT).pack()
        tk.Label(self.info_frame, text=f'Enemy passed: {self.environment.passed[enemy.id]}').pack()
        tk.Label(self.info_frame, text=f'Self passed: {self.environment.passed[self.player.id]}').pack()
        tk.Button(self.info_frame, text="Pass", command=partial(self.clicker.pass_click, self.player)).pack()

        tk.Frame(self.info_frame, height=Card.HEIGHT).pack()
        tk.Label(self.info_frame, text=f'Enemy: {core_board.get_enemy_player(self.player).faction.name}').pack()
        tk.Label(self.info_frame, text=f'Self: {self.player.faction.name}').pack()

        tk.Frame(self.info_frame, height=Card.HEIGHT).pack()
        tk.Label(self.info_frame, text=f'Enemy leader: {str(core_board.get_enemy_player(self.player).leader)}').pack()
        tk.Label(self.info_frame, text=f'Self leader: {str(self.player.leader)}').pack()
        button_state = tk.DISABLED if not self.player.leader or self.player.leader.is_passive() else tk.NORMAL
        tk.Button(self.info_frame, text="Leader", command=partial(self.clicker.leader_click, self.player),
                  state=button_state).pack()

        tk.Label(self.info_frame, text=f'CardSource: {str(self.environment.next_card_source.name)}').pack()
        tk.Label(self.info_frame, text=f'CardDestination: {str(self.environment.next_card_destination.name)}').pack()

    def _draw_damage_frame(self):
        combat_row_sorting = [CombatRow.SIEGE, CombatRow.RANGE, CombatRow.CLOSE]
        core_board = self.environment.board

        for player in [core_board.get_enemy_player(self.player), self.player]:
            for row in combat_row_sorting:
                damage = core_board.cards[player.id].calculate_damage_for_row(row, core_board.weather,
                                                                              core_board.passive_leaders)
                label = tk.Label(self.damage_frame, text=F'{row.name}: {damage}')
                label.pack()

                # row=row is necessary, otherwise the all lambdas would reference the current value of row
                # which would be 'SIEGE', as it is the last value of row
                label.bind('<Button-1>', lambda _, row=row: self.clicker.click_row(row))

                tk.Frame(self.damage_frame, height=Card.HEIGHT).pack()
            combat_row_sorting.reverse()
