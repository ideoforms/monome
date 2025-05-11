from __future__ import annotations

from .page import GridPage
import logging
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPageKeyboard (GridPage):
    def __init__(self,
                 grid: GridUI):
        super().__init__(grid)

        self.octave: int = 2
        self.num_octaves_per_row = self.width // 8

    def _handle_grid_key(self, x: int, y: int, down: int):
        from ..event import GridUIMidiNoteEvent

        # First 6 rows are the keyboard keys
        if y < 6:
            y_octave_offset = ((5 - y) // 2) * self.num_octaves_per_row
            x_octave_index = (x // 7)
            if x_octave_index >= self.num_octaves_per_row:
                return
            octave = self.octave + y_octave_offset + x_octave_index
            notes_white = [0, 2, 4, 5, 7, 9, 11]
            notes_black = [None, 1, 3, None, 6, 8, 10]
            if y % 2 == 0:
                semitone = notes_black[x % 7]
            else:
                semitone = notes_white[x % 7]
            if semitone is None:
                return
            note = octave * 12 + semitone
            if down:
                self.grid.led_level_set(x, y, self.grid.led_intensity_high)
            else:
                self.grid.led_level_set(x, y, self.grid.led_intensity_low)
            event = GridUIMidiNoteEvent(self, x, y, down, note)
            for handler in self.handlers:
                handler(event)

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
        for y in [0, 2, 4]:
            black_keys = (np.array([0, 1, 1, 0, 1, 1, 1]) * self.grid.led_intensity_low).tolist()
            black_keys_row_intensities = black_keys * self.num_octaves_per_row
            self.grid.led_level_row(0, y, black_keys_row_intensities)
        for y in [1, 3, 5]:
            white_keys = (np.array([1, 1, 1, 1, 1, 1, 1]) * self.grid.led_intensity_low).tolist()
            white_keys_row_intensities = white_keys * self.num_octaves_per_row
            self.grid.led_level_row(0, y, white_keys_row_intensities)
        self.grid.led_level_set(0, self.grid.height - 1, self.grid.led_intensity_medium)
        self.grid.led_level_set(self.grid.width - 1, self.grid.height - 1, self.grid.led_intensity_medium)