from __future__ import annotations

from .page import GridPage
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPageScaleMatrix (GridPage):
    def __init__(self,
                 grid: GridUI,
                 mode: str = "scale_matrix"):
        super().__init__(grid, mode)

        from isobar import Scale

        self.octave: int = 2
        self.scale = Scale.major

    def _handle_grid_key(self, x: int, y: int, down: int):
        # First 6 rows are the keyboard keys
        if y < 6:
            if down:
                self.grid.led_level_set(x, y, self.grid.led_intensity_high)
            else:
                self.grid.led_level_set(x, y, self.grid.led_intensity_low)
            note = (self.octave + (5 - y)) * 12 + self.scale.get(x)
            for handler in self.handlers:
                handler(note, down)
        # Final row is octave up/down
        elif y == self.grid.height - 1:
            if x == 0:
                # Octave down
                if down and self.octave > 0:
                    self.octave -= 1
                    self.grid.led_level_set(x, y, self.grid.led_intensity_high)
                else:
                    self.grid.led_level_set(x, y, self.grid.led_intensity_medium)
            elif x == self.width - 1:
                if down and self.octave < 5:
                    self.octave += 1
                    self.grid.led_level_set(x, y, self.grid.led_intensity_high)
                else:
                    self.grid.led_level_set(x, y, self.grid.led_intensity_medium)

    def draw(self):
        self.grid.led_all(0)
        for y in range(6):
            self.grid.led_level_row(0, y, [self.grid.led_intensity_low] * self.grid.width)
        self.grid.led_level_set(0, self.grid.height - 1, self.grid.led_intensity_medium)
        self.grid.led_level_set(self.grid.width - 1, self.grid.height - 1, self.grid.led_intensity_medium)