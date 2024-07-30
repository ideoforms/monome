from .base import ArcRing
from ..page import ArcPage
from ...utils import round_to_integer

class ArcRingReel (ArcRing):
    def __init__(self, page: ArcPage, index: int):
        super().__init__(page, index)
        self.position = 0

    def draw(self):
        if self.arc.current_page != self.page:
            return
        
        position = round_to_integer(self.position)

        quarter_offset = self.led_count // 3
        display = [0] * self.led_count
        display[(position + 0 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        display[(position + 1 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        display[(position + 2 * quarter_offset) % self.led_count] = self.led_intensity_cursor
        self.arc.ring_map(self.index, display)

    def _handle_ring_enc(self, delta: int):
        self.position = (self.position + delta) % self.led_count
        
        for handler in self.page.handlers + self.arc.handlers:
            handler(self.index, self.position, delta)