import tkinter as tk
from operator import attrgetter
from typing import List, Callable

from source.cards import deck, faction, leader
from source.core.card import Card as CoreCard
from source.core.cardcollection import CardCollection
from source.core.player import Player
from source.gui.card import Card as GUICard
from source.get_random_players import get_random_players

START_GAME = Callable[[Player, Player], None]


class CardLoader(tk.Frame):

    def __init__(self, start_game: START_GAME):
        super().__init__()
        self.start_game = start_game
        self.deck = list(deck)
        self.chosen_cards: List[CoreCard] = []
        self.faction = faction
        self.leader = leader
        self.redraw()

    def redraw(self):
        self.clear_cards()
        tk.Label(self, text="Choose your starting cards").pack()
        self._draw_row(self.deck, self._select_card)
        canvas = tk.Canvas(self, width=self.winfo_width(), height=5)
        canvas.create_rectangle(0, 0, self.winfo_width(), 5, fill='black')
        canvas.pack()
        self._draw_row(self.chosen_cards, self._deselect_card)
        tk.Button(self, text='Start game', command=self._start).pack()

    def _draw_row(self, cards: List[CoreCard], clicker: Callable[[CoreCard], None]):
        frame = tk.Frame(self)
        frame.pack()
        for card in sorted(cards, key=attrgetter('damage', 'ability')):
            card = GUICard(card, clicker)
            card.pack(in_=frame, side=tk.RIGHT, padx=GUICard.WIDTH * 0.1)

    def clear_cards(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _select_card(self, card: CoreCard):
        self.deck.remove(card)
        self.chosen_cards.append(card)
        self.redraw()

    def _deselect_card(self, card: CoreCard):
        self.chosen_cards.remove(card)
        self.deck.append(card)
        self.redraw()

    def _start(self):
        player1 = Player(0, self.faction, [], self.leader)
        player1.hand = CardCollection(self.chosen_cards)
        player1.deck = CardCollection(self.deck)

        _, player2 = get_random_players()
        self.destroy()
        self.start_game(player1, player2)
