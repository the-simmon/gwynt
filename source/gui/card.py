import tkinter as tk
from typing import Callable, Optional

from source.core.card import Card as CoreCard


class Card(tk.Canvas):
    HEIGHT = 100
    WIDTH = 56

    def __init__(self, master, card: CoreCard, clicker: Optional[Callable[[CoreCard], None]]):
        super().__init__(master, height=Card.HEIGHT, width=Card.WIDTH, background='white')
        self.card = card
        self.clicker = clicker

        self.fill = 'gold' if card.hero else 'white'
        self.config(background=self.fill)
        self.create_rectangle(1, 1, Card.WIDTH, Card.HEIGHT)
        self.create_text(15, 15, text=str(self.card.damage), font="Times 20")
        self.create_text(Card.WIDTH * 0.7, Card.HEIGHT * 0.9, text=self.card.ability.name, font="Times 8")
        self.create_text(Card.WIDTH * 0.5, Card.HEIGHT * 0.5, text=self.card.combat_row.name, font="Times 10")
        self.create_text(Card.WIDTH * 0.5, Card.HEIGHT * 0.7, text=self.card.muster.name, font="Times 4")

        if clicker:
            self.bind('<Enter>', self._highlight)
            self.bind('<Leave>', self._stop_highlight)
            self.bind('<Button-1>', self._click)

    def _highlight(self, _):
        self.config(background='red')

    def _stop_highlight(self, _):
        self.config(background=self.fill)

    def _click(self, _):
        self.clicker(self.card)
