import tkinter as tk

from source.core.card import Card as CoreCard


class Card(tk.Canvas):

    def __init__(self, card: CoreCard):
        super().__init__(height=160, width=90)
        self.card = card
        self.create_rectangle(1, 1, self.cget('width'), self.cget('height'), activeoutline="red")
        self.create_text(10, 10, text=str(self.card.damage), font="Times 20")
        self.create_text(int(self.cget('width')) * 0.7, int(self.cget('height')) * 0.9, text=self.card.ability.name,
                         font="Times 10")
