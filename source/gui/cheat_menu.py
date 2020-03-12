import asyncio
import tkinter as tk
from functools import partial
from typing import Callable

from source.ai.mcts.mcts import MCTS
from source.core.card import Ability, Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import CardSource, CardDestination, GameEnvironment
from source.core.weather import Weather
from source.gui.widgets.card_editor import CardEditor
from source.gui.widgets.enum_combobox import EnumCombobox

_GUI_CALLBACK = Callable[[], None]


class CheatMenu(tk.LabelFrame):

    def __init__(self, master, environment: GameEnvironment, update_gui: _GUI_CALLBACK):
        super().__init__(master, text='Cheat menu')
        self.environment = environment
        self.board = environment.board
        self.update_gui = update_gui

        tk.Label(self, text='Source').grid(row=0, column=0)
        values = [CardSource.HAND, CardSource.GRAVEYARD, CardSource.ENEMY_GRAVEYARD, CardSource.BOARD]
        self.source_box = EnumCombobox[CardSource](self, CardSource, default=CardSource.HAND, values=values)
        self.source_box.grid(row=0, column=1)

        tk.Label(self, text='Destination').grid(row=0, column=2)
        self.destination_box = EnumCombobox[CardDestination](self, CardDestination, default=CardDestination.BOARD)
        self.destination_box.grid(row=0, column=3)

        self.card_editor = CardEditor(self)
        self.card_editor.grid(row=1, column=0, columnspan=4)

        row_frame = tk.Frame(self)
        row_frame.grid(row=2, column=0, columnspan=4)
        tk.Label(row_frame, text='Target row').grid(row=0, column=0)
        self.target_row_box = EnumCombobox[CombatRow](row_frame, CombatRow)
        self.target_row_box.grid(row=0, column=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=4)
        tk.Button(button_frame, text='Play Card', command=self._play_card).grid(row=0, column=0)
        tk.Button(button_frame, text='Play Leader', command=self._player_leader).grid(row=0, column=1)
        tk.Button(button_frame, text='Pass', command=self._pass).grid(row=0, column=2)
        tk.Button(button_frame, text='Next player = self', command=self._set_next_player_self).grid(row=0, column=3)
        tk.Button(button_frame, text='MCTS', command=self._run_mcts).grid(row=1, column=0, columnspan=2)
        tk.Button(button_frame, text='Revert', command=self._revert_card).grid(row=1, column=2, columnspan=2)
        self.best_card_label = tk.Label(button_frame, text='')
        self.best_card_label.grid(row=2, column=0, columnspan=4)

        misc_frame = tk.Frame(self)
        misc_frame.grid(row=4, column=0, columnspan=5)
        tk.Button(misc_frame, text='Clear', command=self._clear_weather).grid(row=0, column=0)
        tk.Button(misc_frame, text='Frost', command=partial(self._set_weather, Weather.FROST)).grid(row=0, column=1)
        tk.Button(misc_frame, text='Fog', command=partial(self._set_weather, Weather.FOG)).grid(row=0, column=2)
        tk.Button(misc_frame, text='Rain', command=partial(self._set_weather, Weather.RAIN)).grid(row=0, column=3)
        tk.Button(misc_frame, text='add card to enemy', command=self._add_card_to_enemy).grid(row=0, column=4)
        tk.Button(misc_frame, text='add card to player', command=self._add_card_to_player).grid(row=0, column=5)

    def _play_card(self):
        player = self.environment.player2
        if self.environment.next_card_source is CardSource.HAND:
            # remove one card to decrease the amount of cards
            player.hand.pop_first()

        self.environment.next_player = player
        self.environment.next_card_source = self.source_box.get_value()
        self.environment.next_card_destination = self.destination_box.get_value()
        target_row = self.target_row_box.get_value()
        card = self.card_editor.get_card()

        self.environment.add_card_to_source(player, card)
        if self.source_box.get_value() is CardSource.BOARD:
            self.environment.board.cards[player.id].remove(target_row, card)
            player.hand.add(card.combat_row, card)
        self.environment.step(player, target_row, card)

        self.update_gui()

    def _player_leader(self):
        player = self.environment.player2
        self.environment.step_leader(player, player.leader)
        self.update_gui()

    def _pass(self):
        player = self.environment.player2
        self.environment.step(player, None, None)
        self.update_gui()

    def _set_next_player_self(self):
        player = self.environment.player1
        self.environment.next_player = player
        self.environment.next_card_source = CardSource.HAND
        self.environment.next_card_destination = CardDestination.BOARD
        self.update_gui()

    def _run_mcts(self):
        asyncio.create_task(self._async_run_mcts())

    async def _async_run_mcts(self):
        mcts = MCTS(self.environment, self.environment.player1)
        card, row, replace_card = await asyncio.get_event_loop().run_in_executor(None, mcts.run)
        if card is None:
            text = 'Pass'
        elif card.ability is Ability.DECOY:
            text = f'Decoy: {row}, {replace_card}'
        else:
            text = f'Card: {row}, {card}'
        self.best_card_label.config(text=text)

    def _revert_card(self):
        card = self.card_editor.get_card()
        if card.ability is Ability.SPY:
            player = self.environment.player1
            # remove two card because of spy
            self.environment.player2.hand.pop_first()
        else:
            player = self.environment.player2
            # add random card to adjust card count, will be ignored anyway
            self.environment.player2.hand.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 1))

        target_row = self.target_row_box.get_value()
        self.environment.board.cards[player.id].remove(target_row, card)
        self.update_gui()

    def _clear_weather(self):
        self.environment.board.weather = [Weather.CLEAR]
        self.update_gui()

    def _set_weather(self, weather: Weather):
        if Weather.CLEAR in self.environment.board.weather:
            self.environment.board.weather.remove(Weather.CLEAR)
        self.environment.board.weather.append(weather)
        self.update_gui()

    def _add_card_to_enemy(self):
        self.environment.player2.hand.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 0))
        self.update_gui()

    def _add_card_to_player(self):
        card = self.card_editor.get_card()
        player = self.environment.player1
        player.hand.add(card.combat_row, card)
        self.update_gui()
