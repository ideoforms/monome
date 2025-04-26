from __future__ import annotations

import time
import logging

from .page import GridPage
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPageButtons (GridPage):
    def __init__(self,
                 grid: GridUI):
        super().__init__(grid)

        self.key_down_handlers = [[None] * grid.width for _ in range(grid.height)]
        self.key_up_handlers = [[None] * grid.width for _ in range(grid.height)]
        self.last_button_index = 0

    # For decorator that binds to a single key:
    # @page.handler_for_key(0, 0, 1)
    def handler_for_key(self, x: int, y: int, down: int = 1):
        def wrapper(callback):
            self.add_handler_for_key(callback, x, y, down)
        return wrapper

    def add_handler_for_key(self, callback: Callable, handler_x: int, handler_y: int, handler_down: int = 1):
        if handler_down:
            self.add_key_handler(callback, x=handler_x, y=handler_y)
        else:
            self.add_key_handler(callback, callback, x=handler_x, y=handler_y)

    def add_key_handler(self,
                        key_down_handler: Callable,
                        key_up_handler: Callable = None,
                        x: int = None,
                        y: int = None):
        if x is not None:
            if y is None:
                raise ValueError("Both x and y must be specified, or both omitted")
        else:
            x = self.last_button_index % self.width
            y = self.last_button_index // self.width
        self.last_button_index += 1
        self.grid.led_level_set(x, y, 5)
        self.key_down_handlers[y][x] = key_down_handler
        self.key_up_handlers[y][x] = key_up_handler
    
    key_handler = add_key_handler
    
    def _handle_grid_key(self, x: int, y: int, down: int):
        logger.debug("Grid key: %d, %d, %s" % (x, y, down))
        if self.key_down_handlers[y][x] is not None:
            self.grid.led_level_set(x, y, self.grid.led_intensity_high if down else self.grid.led_intensity_low)

        if down == 1 and self.key_down_handlers[y][x] is not None:
            self.key_down_handlers[y][x]()
        if down == 0 and self.key_up_handlers[y][x] is not None:
            self.key_up_handlers[y][x]()

if __name__ == "__main__":
    from ..ui import GridUI

    grid = GridUI()
    page = grid.add_page("buttons")

    def key_down():
        print("down")
    def key_up():
        print("up")

    # add two initial buttons
    page.add_key_handler(key_down, key_up)
    page.add_key_handler(key_down, key_up)

    @page.handler_for_key(4, 4)
    def _():
        print("key 4, 4 pressed")
    
    while True:
        time.sleep(1)