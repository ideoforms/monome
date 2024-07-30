from .base import ArcRing
from ..page import ArcPage
import numpy as np

class ArcRingAngular (ArcRing):
    def __init__(self, page: ArcPage, index: int):
        super().__init__(page, index)
        self.position = 0

    def draw(self):
        position = self.position
        display = [0] * self.led_count
        display[position] = self.led_intensity_cursor
        self.arc.ring_map(self.index, display)

    def _handle_ring_enc(self, delta: int):
        self.position = (self.position + delta) % self.led_count
        delta_radians = (np.pi * 2) * (delta / self.led_count)
        angle_radians = (np.pi * 2) * (self.position / self.led_count)
        
        for handler in self.page.handlers + self.arc.handlers:
            handler(self.index, angle_radians, delta_radians)