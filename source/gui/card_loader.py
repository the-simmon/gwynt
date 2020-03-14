import tkinter as tk
from operator import attrgetter
from typing import List, Callable

from source.cards import deck, faction, leader
from source.core.card import Card as CoreCard
from source.core.cardcollection import CardCollection
from source.core.cards.util import get_cards
from source.core.player import Player, Faction
from source.gui.card import Card as GUICard
from source.gui.widgets.card_editor import LeaderCardEditor
from source.gui.widgets.enum_combobox import EnumCombobox

START_GAME = Callable[[Player, Player], None]


class CardLoader(tk.Frame):

    def __init__(self, master, start_game: START_GAME):
        super().__init__(master)
        self.start_game = start_game
        self.deck = list(deck)
        self.chosen_cards: List[CoreCard] = []
        self.faction = faction
        self.leader = leader

        self.card_frame = tk.Frame(self)
        self.card_frame.pack()

        enemy_selection_frame = tk.Frame(self)
        enemy_selection_frame.pack()
        tk.Label(enemy_selection_frame, text='Enemy faction').pack(side=tk.LEFT)
        self.enemy_faction_combobox = EnumCombobox[Faction](enemy_selection_frame, Faction)
        self.enemy_faction_combobox.pack(side=tk.LEFT, pady=10)

        self.leader_editor = LeaderCardEditor(self)
        self.leader_editor.pack(pady=10)

        tk.Button(self, text='Start game', command=self._start).pack()
        self.redraw()

    def redraw(self):
        self.clear_cards()
        tk.Label(self.card_frame, text="Choose your starting cards").pack()
        self._draw_row(self.deck, self._select_card)
        canvas = tk.Canvas(self.card_frame, width=self.winfo_width(), height=5)
        canvas.create_rectangle(0, 0, self.winfo_width(), 5, fill='black')
        canvas.pack()
        self._draw_row(self.chosen_cards, self._deselect_card)

    def clear_cards(self):
        for widget in self.card_frame.winfo_children():
            widget.destroy()

    def _draw_row(self, cards: List[CoreCard], clicker: Callable[[CoreCard], None]):
        frame = tk.Frame(self.card_frame)
        frame.pack()
        for card in sorted(cards, key=attrgetter('damage', 'combat_row'), reverse=True):
            card = GUICard(frame, card, clicker)
            card.pack(side=tk.RIGHT, padx=GUICard.WIDTH * 0.1)

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

        enemy_faction = self.enemy_faction_combobox.get_value()
        cards = get_cards(enemy_faction)
        leader = self.leader_editor.get_card()
        player2 = Player(1, faction, cards[:13], leader)
        player2.hand = CardCollection(cards[13:23])
        player2.faction = enemy_faction
        self.pack_forget()
        self.start_game(player1, player2)
