from __future__ import annotations

import logging

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPage:
    def __init__(self,
                 grid: GridUI):

        self.grid = grid
        self.handlers: list[Callable] = []
    
    def __str__(self):
        return str(self.__class__.__name__)

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
        raise NotImplementedError("Subclasses must implement _handle_grid_key() method")

    def draw(self):
        raise NotImplementedError("Subclasses must implement draw() method")