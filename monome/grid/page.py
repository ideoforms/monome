from __future__ import annotations

import logging

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import GridUI

logger = logging.getLogger(__name__)


class GridPage:
    def __init__(self,
                 grid: GridUI,
                 mode: str = "buttons"):

        self.grid = grid

        self.mode = mode
        self.handlers: list[Callable] = []

    @property
    def width(self):
        return self.grid.width

    @property
    def height(self):
        return self.grid.height

    def add_handler(self, callback: Callable):
        self.handlers.append(callback)

    def handler_for_key(self, handler_x: int, handler_y: int, handler_down: int = None):
        self.grid.led_level_set(handler_x, handler_y, 5)
        def wrapper(callback):
            def grid_handler(x: int, y: int, down: int):
                if x == handler_x and y == handler_y and (handler_down is None or handler_down == down):
                    callback(x, y, down)
                    self.grid.led_level_set(x, y, down * 5 + 5)
            self.add_handler(grid_handler)
        return wrapper

    def _handle_grid_key(self, x: int, y: int, down: int):
        logger.debug("Grid key: %d, %d, %s" % (x, y, down))
        for handler in self.handlers:
            handler(x, y, down)

    def draw(self):
        self.grid.led_all(0)