from .base import ArcRing
from ..page import ArcPage
from ...utils import round_to_integer
import math

class ArcRingBipolar (ArcRing):
    def draw(self):
        position = round_to_integer(self._position)
        
        ones = int(math.fabs(position))
        ones = min(ones, self.led_count)
        zeros = self.led_count - ones
        if position > 0:
            buf = ([self.led_intensity_fill] * ones) + ([0] * zeros)
        else:
            buf = ([0] * zeros) + ([self.led_intensity_fill] * ones)
        buf[position % self.led_count] = self.led_intensity_cursor
        self.arc.ring_map(self.index, buf)

    def _handle_enc_delta(self, delta: float):
        self._position += delta

        self._call_handlers(self._position, delta)