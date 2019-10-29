import tkinter as tk

from source.core.card import Card as CoreCard, CombatRow, Ability
from source.core.cards.util import get_cards
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player, Faction
from source.gui.board import Board
from source.gui.card import Card
from source.core.board import Board as CoreBoard
from source.gui.game import Game


def main():
    master = tk.Tk()
    player1 = Player(0, Faction.NILFGAARD, get_cards(Faction.NILFGAARD))
    player2 = Player(1, Faction.NOTHERN_REALMS, get_cards(Faction.NOTHERN_REALMS))
    environment = GameEnvironment(player1, player2)
    environment.current_player = player1
    card = player1.active_cards.get_all_cards()[0]
    environment.step(player1, card.combat_row, card)

    card = player2.active_cards.get_all_cards()[0]
    environment.step(player2, card.combat_row, card)

    card = player1.active_cards.get_all_cards()[0]
    environment.step(player1, card.combat_row, card)
    game = Game(environment, player1)
    game.pack(in_=master)
    master.after(1, game.redraw)
    master.mainloop()


if __name__ == '__main__':
    main()
