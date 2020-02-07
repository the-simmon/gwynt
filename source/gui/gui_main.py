import tkinter as tk

from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction
from source.gui.game import Game

master = tk.Tk()
player1 = Player(0, Faction.NILFGAARD, get_cards(Faction.NILFGAARD))
player2 = Player(1, Faction.NOTHERN_REALMS, get_cards(Faction.NOTHERN_REALMS))
environment = GameEnvironment(player1, player2)
environment.next_player = player1
card = player1.hand.get_all_cards()[0]
environment.step(player1, card.combat_row, card)

card = player2.hand.get_all_cards()[0]
environment.step(player2, card.combat_row, card)

card = player1.hand.get_all_cards()[0]
environment.step(player1, card.combat_row, card)
game = Game(environment, player1)
game.pack(in_=master)
master.after(1, game.redraw)


def add_card():
    card = player1.hand.get_all_cards()[0]
    environment.step(player1, card.combat_row, card)
    game.redraw()


master.after(1000, add_card)
master.mainloop()
