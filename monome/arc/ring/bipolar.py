from .base import ArcRing
from ..page import ArcPage
from ...utils import round_to_integer
import math

class ArcRingBipolar (ArcRing):
    def __init__(self, page: ArcPage, index: int):
        super().__init__(page, index)
        self.position = 0

    def draw(self):
        position = round_to_integer(self.position)
        
        ones = int(math.fabs(position))
        ones = min(ones, self.led_count)
        zeros = self.led_count - ones
        if position > 0:
            buf = ([self.led_intensity_fill] * ones) + ([0] * zeros)
        else:
            buf = ([0] * zeros) + ([self.led_intensity_fill] * ones)
        buf[position % self.led_count] = self.led_intensity_cursor
        self.arc.ring_map(self.index, buf)

    def _handle_ring_enc(self, delta: int):
        self.position += delta

        for handler in self.page.handlers + self.arc.handlers:
            handler(self.index, self.position, delta)