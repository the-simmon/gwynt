import tkinter as tk

from source.core.card import Card as CoreCard


class Card(tk.Canvas):
    HEIGHT = 100
    WIDTH = 56

    def __init__(self, card: CoreCard, enable_highlighting: bool):
        super().__init__(height=Card.HEIGHT, width=Card.WIDTH, background='white')
        self.card = card
        fill = 'gold' if card.hero else None
        self.create_rectangle(1, 1, Card.WIDTH, Card.HEIGHT, fill=fill)
        self.create_text(15, 15, text=str(self.card.damage), font="Times 20")
        self.create_text(Card.WIDTH * 0.7, Card.HEIGHT * 0.9, text=self.card.ability.name, font="Times 8")
        self.create_text(Card.WIDTH * 0.5, Card.HEIGHT * 0.5, text=self.card.combat_row.name, font="Times 10")

        if enable_highlighting:
            self.bind('<Enter>', self._highlight)
            self.bind('<Leave>', self._stop_highlight)

    def _highlight(self, _):
        self.config(background='red')

    def _stop_highlight(self, _):
        self.config(background='white')
