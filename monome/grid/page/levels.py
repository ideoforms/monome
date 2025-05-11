from __future__ import annotations

import logging

from .page import GridPage
from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPageHorizontalLevels (GridPage):
    def __init__(self,
                 grid: GridUI,
                 num_levels: int = None,
                 handler: Callable = None):
        super().__init__(grid)

        if num_levels is None:
            num_levels = grid.height
        self.levels = [0] * num_levels
        if handler is not None:
            self.add_handler(handler)

    def _handle_grid_key(self, x: int, y: int, down: int):
        from ..event import GridUIKeyEvent

        if down:
            if y < len(self.levels):
                self.levels[y] = x
                event = GridUIKeyEvent(self, x, y, down)
                for handler in self.handlers:
                    handler(event)
                self.draw()
    
    def set_level(self, y: int, level: int):
        if level < 0 or level >= self.width:
            raise ValueError("Level must be between 0 and width-1")
        self.levels[y] = level
        self.draw()

    def set_levels(self, levels: list[int]):
        if len(levels) != len(self.levels):
            raise ValueError("Length of levels must match number of levels")
        for level in levels:
            if level < 0 or level >= self.width:
                raise ValueError("Level must be between 0 and width-1")
        self.levels = levels
        self.draw()

    def draw(self):
        for index, level in enumerate(self.levels):
            self.grid.led_level_row(0, index, [self.grid.led_intensity_high] * (level + 1) + [self.grid.led_intensity_low] * (self.width - level - 1))

if __name__ == "__main__":
    from ..ui import GridUI
    import time

    def level_handler(event):
        print(f"Level handler: page={event.page}, y={event.y}, x={event.x}")
        
    gridui = GridUI()
    page = gridui.add_page(mode="levels",
                           num_levels=4,
                           handler=level_handler)
    
    while True:
        time.sleep(1)