from __future__ import annotations

from .page import GridPage
import logging
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


class GridPageScaleMatrix (GridPage):
    def __init__(self,
                 grid: GridUI):
        super().__init__(grid)

        from isobar import Scale

        self.octave: int = 3
        self.scale = Scale.minorPenta

        self.matrix_width = 8
        self.matrix_height = 6
        self.matrix_total_cells = self.matrix_width * self.matrix_height
        led_sequence = [self.grid.led_intensity_low] * len(self.scale.semitones) + [0]
        matrix_num_octaves = int(np.ceil(self.matrix_total_cells / len(led_sequence)))
        matrix_sequence = (led_sequence * matrix_num_octaves)[:self.matrix_total_cells]
        self.matrix_rows = np.split(np.array(matrix_sequence), self.matrix_height)

    def _handle_grid_key(self, x: int, y: int, down: int):
        from ..event import GridUIMidiNoteEvent

        # First 6 rows are the keyboard keys
        if y < 6 and x < self.matrix_width:
            scale_length_spaced = len(self.scale.semitones) + 1
            note_index = ((5 - y) * self.matrix_width) + x
            note_octave_index = self.octave + note_index // scale_length_spaced
            note_note_index = note_index % scale_length_spaced
            if note_note_index == scale_length_spaced - 1:
                return
            midi_note = (note_octave_index * 12) + self.scale.get(note_note_index)

            if down:
                self.grid.led_level_set(x, y, self.grid.led_intensity_high)
            else:
                self.grid.led_level_set(x, y, self.grid.led_intensity_low)

            event = GridUIMidiNoteEvent(self, x, y, down, midi_note)
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
        for row in range(self.matrix_height):
            self.grid.led_level_row(0, (5 - row), self.matrix_rows[row].tolist())
        self.grid.led_level_set(0, self.grid.height - 1, self.grid.led_intensity_medium)
        self.grid.led_level_set(self.grid.width - 1, self.grid.height - 1, self.grid.led_intensity_medium)

if __name__ == "__main__":
    from ..ui import GridUI
    import time
        
    gridui = GridUI()
    page = gridui.add_page(mode="scale_matrix")

    @page.handler
    def _(event):
        print(event.note, event.down)
    
    while True:
        time.sleep(1)