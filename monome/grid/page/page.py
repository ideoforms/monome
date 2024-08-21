from __future__ import annotations

import logging

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

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
    
    handler = add_handler

    def _handle_grid_key(self, x: int, y: int, down: int):
        logger.debug("Grid key: %d, %d, %s" % (x, y, down))
        for handler in self.handlers:
            handler(x, y, down)

    def draw(self):
        self.grid.led_all(0)