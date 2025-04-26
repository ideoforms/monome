from .base import ArcRing
from ..page import ArcPage
from ...utils import round_to_integer
import numpy as np

class ArcRingAngular (ArcRing):
    def __init__(self, page: ArcPage, index: int):
        super().__init__(page, index)
        self.position = 0

    @property
    def normalise(self):
        return False

    def draw(self):
        position = round_to_integer(self.position)
        
        display = [0] * self.led_count
        display[position] = self.led_intensity_cursor
        self.arc.ring_map(self.index, display)

    def _handle_ring_enc(self, delta: float):
        self.position = (self.position + delta) % self.led_count
        delta_radians = (np.pi * 2) * (delta / self.led_count)
        angle_radians = (np.pi * 2) * (self.position / self.led_count)
        
        self._call_handlers(angle_radians, delta_radians)