import tkinter as tk
from functools import partial
from operator import attrgetter
from typing import List, Dict

from source.core.board import Board as CoreBoard
from source.core.card import Card as CoreCard
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import CardSource, GameEnvironment
from source.core.player import Player
from source.gui.card import Card
from source.gui.cookie_clicker import CookieClicker


class Board(tk.Frame):
    WIDTH = 1920 / 2
    HEIGHT = 1080

    def __init__(self, environment: GameEnvironment, board: CoreBoard, player: Player, clicker: CookieClicker):
        super().__init__(width=Board.WIDTH, height=Board.HEIGHT)
        self.environment = environment
        self.board = board
        self.player = player
        self.clicker = clicker

    def redraw(self):
        self.clear_cards()
        frames = self._get_frames_per_player()

        enemy = self.board.get_enemy_player(self.player)
        frames[enemy].pack()

        canvas = tk.Canvas(self, width=Board.WIDTH, height=5)
        canvas.create_rectangle(0, 0, Board.WIDTH, 5, fill='black')
        canvas.pack()

        frames[self.player].pack()

    def _get_frames_per_player(self) -> Dict[Player, tk.Frame]:

        frame_dict: Dict[Player, tk.Frame] = {}

        combat_row_sorting = [CombatRow.CLOSE, CombatRow.RANGE, CombatRow.SIEGE]
        for player in [self.player, self.board.get_enemy_player(self.player)]:
            card_collection = self.board.cards[player.id]
            frame = tk.Frame(self)
            frame_dict[player] = frame

            enable_clicking = player.id is self.player.id

            cards = [card_collection.get_damage_adjusted_cards(row, self.board.weather, self.board.passive_leaders) for
                     row in combat_row_sorting]
            for card_list, row in zip(cards, combat_row_sorting):
                self._draw_row(card_list, player, row, enable_clicking).pack(in_=frame)

            if player.id is self.player.id:
                if self.environment.next_player.id is self.player.id:
                    cards = self.environment.card_tracker.get_possible_cards(False)
                else:
                    cards = self.player.hand.get_all_cards()
                self._draw_row(cards, player, None, True).pack(in_=frame)
            combat_row_sorting.reverse()

        return frame_dict

    def clear_cards(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _draw_row(self, card_list: List[CoreCard], player: Player, row: CombatRow,
                  enable_clicking: bool = False) -> tk.Frame:
        clicker = partial(self.clicker.card_click, player, row) if enable_clicking else None

        frame = tk.Frame(height=Card.HEIGHT * 1.1)
        for card in sorted(card_list, key=attrgetter('damage', 'ability')):
            card = Card(card, clicker)
            card.pack(in_=frame, side=tk.RIGHT, padx=Card.WIDTH * 0.1)
        return frame
