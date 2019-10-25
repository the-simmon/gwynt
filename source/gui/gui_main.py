import tkinter as tk

from source.gui.card import Card
from source.core.card import Card as CoreCard, CombatRow, Ability


def main():
    master = tk.Tk()
    card = Card(CoreCard(CombatRow.CLOSE, 5, Ability.MEDIC))
    card.pack(in_=master)

    master.mainloop()


if __name__ == '__main__':
    main()
