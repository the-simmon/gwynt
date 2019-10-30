import tkinter as tk
from operator import attrgetter
from typing import List, Dict

from source.core.board import Board as CoreBoard
from source.core.card import Card as CoreCard
from source.core.card import CombatRow
from source.core.player import Player
from source.gui.card import Card


class Board(tk.Frame):
    WIDTH = 1920
    HEIGHT = 1080

    def __init__(self, board: CoreBoard, player: Player):
        super().__init__(width=Board.WIDTH, height=Board.HEIGHT)
        self.board = board
        self.player = player

    def redraw(self):
        self.clear_cards()
        frames = self._get_frames_per_player()

        enemy = self.board.get_enemy_player(self.player)
        frames[enemy].pack(in_=self)

        canvas = tk.Canvas(width=Board.WIDTH, height=5)
        canvas.create_rectangle(0, 0, Board.WIDTH, 5, fill='black')
        canvas.pack(in_=self)

        frames[self.player].pack(in_=self)

    def _get_frames_per_player(self) -> Dict[Player, tk.Frame]:

        frame_dict: Dict[Player, tk.Frame] = {}

        combat_row_sorting = [CombatRow.CLOSE, CombatRow.RANGE, CombatRow.SIEGE]
        for player in [self.player, self.board.get_enemy_player(self.player)]:
            card_collection = self.board.cards[player]
            frame = tk.Frame()
            frame_dict[player] = frame

            cards = [card_collection.get_damage_adjusted_cards(row, self.board.weather) for row in combat_row_sorting]
            for card_list in cards:
                self._draw_row(card_list, player).pack(in_=frame)

            if player.id is self.player.id:
                self._draw_row(player.active_cards.get_all_cards(), player).pack(in_=frame)
            combat_row_sorting.reverse()

        return frame_dict

    def clear_cards(self):
        for widget in self.children:
            widget.destroy()

    def _draw_row(self, card_list: List[CoreCard], player: Player) -> tk.Frame:
        frame = tk.Frame(height=Card.HEIGHT * 1.1)
        for card in sorted(card_list, key=attrgetter('damage', 'ability')):
            card = Card(card, player.id is self.player.id)  # convert core card to gui card
            card.pack(in_=frame, side=tk.RIGHT, padx=Card.WIDTH * 0.1)
        return frame
