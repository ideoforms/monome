from .base import ArcRing
from ..page import ArcPage
from ...utils import round_to_integer

class ArcRingReel (ArcRing):
    def __init__(self, page: ArcPage, index: int):
        super().__init__(page, index)

    def draw(self):
        if self.arc.current_page != self.page:
            return
        
        position = round_to_integer(self._position)

        quarter_offset = self.led_count // 3
        display = [0] * self.led_count
        display[(position + 0 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        display[(position + 1 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        display[(position + 2 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        self.arc.ring_map(self.index, display)

    def _handle_enc_delta(self, delta: float):
        self._position = (self._position + delta) % self.led_count
        
        self._call_handlers(self._position, delta)