import numpy as np
import logging
import math

from typing import Union, Callable
from .arc import Arc

logger = logging.getLogger(__name__)


class ArcPage:
    def __init__(self,
                 arc: Arc,
                 modes: Union[str, list[str]] = "bipolar"):

        self.arc = arc
        if isinstance(modes, str):
            modes = [modes] * self.arc.ring_count
        if len(modes) != self.arc.ring_count:
            raise ValueError(f"Modes must contain either 1 or {self.arc.ring_count} values")
        for mode in modes:
            if mode not in ["unipolar", "bipolar", "relative", "angular"]:
                raise ValueError("Invalid ring mode: %s" % mode)
        self.modes = modes
        self.positions = [0] * self.arc.ring_count
        self.sensitivity = 1.0
        self.handlers: list[Callable] = []

        self.led_intensity_fill = 4
        self.led_intensity_cursor = 15

    @property
    def ring_count(self):
        return self.arc.ring_count

    @property
    def led_count(self):
        return self.arc.led_count

    def add_handler(self, callback: Callable):
        self.handlers.append(callback)

    # Synonym to enable @arcpage.handler decorator
    handler = add_handler
    
    def handler_for_ring(self, ring: int = None):
        def wrapper(callback):
            def ring_handler(event_ring, position, delta):
                print("handler", event_ring, position, delta)
                if ring is None or ring == event_ring:
                    callback(ring, position, delta)
            self.add_handler(ring_handler)
        return wrapper

    def _handle_ring_enc(self, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        delta = delta * self.sensitivity
        delta = int(math.ceil(delta) if delta > 0 else math.floor(delta))

        if self.modes[ring] == "bipolar":
            self.positions[ring] += delta
            for handler in self.handlers + self.arc.handlers:
                handler(ring, self.positions[ring], delta)
        elif self.modes[ring] == "unipolar":
            self.positions[ring] += delta
            if self.positions[ring] < 0:
                self.positions[ring] = 0
            if self.positions[ring] > self.led_count:
                self.positions[ring] = self.led_count
            for handler in self.handlers + self.arc.handlers:
                handler(ring, self.positions[ring], delta)
        elif self.modes[ring] == "angular":
            self.positions[ring] = (self.positions[ring] + delta) % self.led_count
            delta_radians = (np.pi * 2) * (delta / self.led_count)
            angle_radians = (np.pi * 2) * (self.positions[ring] / self.led_count)
            for handler in self.handlers + self.arc.handlers:
                handler(ring, angle_radians, delta_radians)

        self.draw_ring(ring)

    def draw(self):
        for ring in range(self.ring_count):
            self.draw_ring(ring)

    def draw_ring(self, ring):
        if self.modes[ring] == "bipolar":
            position = self.positions[ring]

            ones = int(math.fabs(position))
            ones = min(ones, self.led_count)
            zeros = self.led_count - ones
            if position > 0:
                buf = ([self.led_intensity_fill] * ones) + ([0] * zeros)
            else:
                buf = ([0] * zeros) + ([self.led_intensity_fill] * ones)
            buf[position % self.led_count] = self.led_intensity_cursor
            self.arc.ring_map(ring, buf)
        elif self.modes[ring] == "unipolar":
            position = self.positions[ring]

            ones = int(math.fabs(position))
            ones = min(ones, self.led_count)
            zeros = self.led_count - ones
            if position > 0:
                buf = ([self.led_intensity_fill] * ones) + ([0] * zeros)
            else:
                buf = ([0] * zeros) + ([self.led_intensity_fill] * ones)
            buf[position % self.led_count] = self.led_intensity_cursor
            buf = np.roll(buf, self.led_count // 2)
            self.arc.ring_map(ring, buf)
        elif self.modes[ring] == "angular":
            position = self.positions[ring]
            display = [0] * self.led_count
            display[position] = self.led_intensity_cursor
            self.arc.ring_map(ring, display)

    def set_position(self, ring: int, position: int):
        self.positions[ring] = position
        self.draw_ring(ring)