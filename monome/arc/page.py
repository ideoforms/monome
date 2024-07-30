import logging
import math

from typing import Union, Callable
from .arc import Arc

logger = logging.getLogger(__name__)


class ArcPage:
    def __init__(self,
                 arc: Arc,
                 modes: Union[str, list[str]] = "bipolar"):

        from .ring import ArcRingBipolar, ArcRingAngular, ArcRingUnipolar

        self.arc = arc
        if isinstance(modes, str):
            modes = [modes] * self.arc.ring_count
        if len(modes) != self.arc.ring_count:
            raise ValueError(f"Modes must contain either 1 or {self.arc.ring_count} values")

        ring_class_index = {
            "bipolar": ArcRingBipolar,
            "unipolar": ArcRingUnipolar,
            "angular": ArcRingAngular
        }

        for mode in modes:
            if mode not in ring_class_index.keys():
                raise ValueError("Invalid ring mode: %s" % mode)

        self.modes = modes
        self.rings = []
        for index, mode in enumerate(self.modes):
            ring = ring_class_index[mode](self, index)
            self.rings.append(ring)

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
                if ring is None or ring == event_ring:
                    callback(ring, position, delta)
            self.add_handler(ring_handler)
        return wrapper

    def _handle_ring_enc(self, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        delta = delta * self.sensitivity
        delta = int(math.ceil(delta) if delta > 0 else math.floor(delta))

        self.rings[ring]._handle_ring_enc(delta)

        self.draw_ring(ring)

    def draw(self):
        for ring in range(self.ring_count):
            self.draw_ring(ring)

    def draw_ring(self, ring):
        self.rings[ring].draw()

    def set_position(self, ring: int, position: int):
        self.positions[ring] = position
        self.draw_ring(ring)