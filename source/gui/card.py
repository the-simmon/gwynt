import tkinter as tk

from source.core.card import Card as CoreCard


class Card(tk.Canvas):
    HEIGHT = 160
    WIDTH = 90

    def __init__(self, card: CoreCard):
        super().__init__(height=Card.HEIGHT, width=Card.WIDTH)
        self.card = card
        self.create_rectangle(1, 1, Card.WIDTH, Card.HEIGHT, activeoutline="red")
        self.create_text(10, 10, text=str(self.card.damage), font="Times 20")
        self.create_text(Card.WIDTH * 0.7, Card.HEIGHT * 0.9, text=self.card.ability.name, font="Times 10")
        self.create_text(Card.WIDTH * 0.5, Card.HEIGHT * 0.5, text=self.card.combat_row.name, font="Times 10")
