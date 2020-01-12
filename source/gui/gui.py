import asyncio
import tkinter as tk

from source.core.gameenvironment import GameEnvironment
from source.core.player import Player
from source.gui.cookie_clicker import CookieClicker
from source.gui.game import Game


class GUI(tk.Tk):

    def __init__(self, environment: GameEnvironment, player: Player, clicker: CookieClicker):
        super().__init__()
        self.game = Game(environment, player, clicker)
        self.game.pack(in_=self)
        self.update_event = asyncio.Event()

    async def redraw(self):
        self.game.redraw()
        self.update_event.set()
        await self.update_event.wait()

    def mainloop(self):
        asyncio.get_event_loop().run_until_complete(self._mainloop())

    async def _mainloop(self):
        try:
            while True:
                self.update()
                self.update_event.clear()
                await asyncio.sleep(.05)
        except tk.TclError as e:
            if "application has been destroyed" not in e.args[0]:
                raise e
