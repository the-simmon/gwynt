import tkinter as tk
from typing import List, Dict

from source.core.board import Board as CoreBoard
from source.core.card import CombatRow
from source.core.player import Player
from source.gui.card import Card
from source.core.card import Card as CoreCard


class Board(tk.Frame):

    def __init__(self, board: CoreBoard, player: Player):
        super().__init__(width=1920, height=1080 / 2)
        self.board = board
        self.player = player
        self.card_list: List[Card] = []

    def redraw(self):
        self.clear_cards()
        frames = self._get_frames_per_player()

        enemy = self.board.get_enemy_player(self.player)
        if frames[enemy]:
            frames[enemy].pack(in_=self)

        if frames[self.player]:
            frames[self.player].pack(in_=self)

    def _get_frames_per_player(self) -> Dict[Player, tk.Frame]:

        frame_dict: Dict[Player, tk.Frame] = {}

        combat_row_sorting = [CombatRow.CLOSE, CombatRow.RANGE, CombatRow.SIEGE]
        for player, card_collection in self.board.cards:
            frame = tk.Frame()
            frame_dict[player] = frame
            for card_list in [card_collection[row] for row in combat_row_sorting]:
                self._draw_row(card_list, frame)

            self._draw_row(player.active_cards.get_all_cards(), frame)

        return frame_dict

    def clear_cards(self):
        for card in self.card_list:
            card.destroy()

    def _draw_row(self, card_list: List[CoreCard], master: tk.Widget):
        frame = tk.Frame()
        frame.pack(in_=master)
        for card in card_list:
            card = Card(card)  # convert core card to gui card
            card.pack(in_=frame, side=tk.RIGHT, padx=Card.WIDTH * 0.1, pady=Card.HEIGHT * 0.1)
