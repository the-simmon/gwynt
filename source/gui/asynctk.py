import asyncio
import tkinter as tk


class AsyncTK(tk.Tk):

    def __init__(self):
        super().__init__()
        self.update_event = asyncio.Event()

    async def redraw(self):
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
