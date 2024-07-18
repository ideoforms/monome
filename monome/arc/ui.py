import logging
import time
import math
import numpy as np

from typing import Union
from .arc import Arc

logger = logging.getLogger(__name__)


class ArcUI (Arc):
    def __init__(self,
                 modes: Union[str, list[str]] = "bipolar",
                 ring_count: int = 4,
                 led_count: int = 64):
        super().__init__(modes, ring_count, led_count)

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages = []
        self.pages.append(ArcPage(arc=self,
                                  modes=modes))
        self.current_page_index = 0
        self.draw_all()

    @property
    def current_page(self):
        return self.pages[self.current_page_index]

    def handle_osc_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        self.current_page.handle_ring_enc(ring, delta)

    def handler(self, fn: callable):
        self.current_page.handlers.append(fn)

    def get_sensitivity(self):
        return self.current_page.sensitivity
    def set_sensitivity(self, sensitivity: float):
        self.current_page.sensitivity = sensitivity
    sensitivity = property(get_sensitivity, set_sensitivity)

    def draw_all(self):
        for ring in range(self.ring_count):
            self.draw(ring)

    def draw(self, ring):
        self.current_page.draw(ring)

class ArcPage:
    def __init__(self,
                 arc: Arc,
                 modes: Union[str, list[str]] = "bipolar"):
        
        self.arc = arc
        if isinstance(modes, str):
            modes = [modes] * 4
        if len(modes) != 4:
            raise ValueError("Modes must contain either 1 or 4 value")
        for mode in modes:
            if mode not in ["unipolar", "bipolar", "relative", "angular"]:
                raise ValueError("Invalid ring mode: %s" % mode)
        self.modes = modes
        self.positions = [0] * 4
        self.sensitivity = 1.0
        self.handlers: list[callable] = []

        self.led_intensity_fill = 4
        self.led_intensity_cursor = 15

    @property
    def ring_count(self):
        return self.arc.ring_count

    @property
    def led_count(self):
        return self.arc.led_count

    def handle_ring_enc(self, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        delta = delta * self.sensitivity
        delta = int(math.ceil(delta) if delta > 0 else math.floor(delta))

        if self.modes[ring] == "bipolar":
            self.positions[ring] += delta
            for handler in self.handlers:
                handler(ring, self.positions[ring], delta)
        elif self.modes[ring] == "unipolar":
            self.positions[ring] += delta
            if self.positions[ring] < 0:
                self.positions[ring] = 0
            for handler in self.handlers:
                handler(ring, self.positions[ring], delta)
        elif self.modes[ring] == "angular":
            self.positions[ring] = (self.positions[ring] + delta) % self.led_count
            delta_radians = (np.pi * 2) * (delta / self.led_count)
            angle_radians = (np.pi * 2) * (self.positions[ring] / self.led_count)
            for handler in self.handlers:
                handler(ring, angle_radians, delta_radians)

        self.draw(ring)

    def draw(self, ring):
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

def main():
    arcui = ArcUI(modes=["bipolar", "unipolar", "angular", "angular"])
    arcui.sensitivity = 0.5

    @arcui.handler
    def arcui_handler(ring, position, delta):
        print("Handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
