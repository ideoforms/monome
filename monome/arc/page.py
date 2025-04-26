from __future__ import annotations

import logging

from typing import Union, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import ArcUI
    from .ring import ArcRing


logger = logging.getLogger(__name__)


class ArcPage:
    def __init__(self,
                 arc: ArcUI,
                 index: int = 0,
                 modes: Union[str, list[str]] = "bipolar"):

        self.arc = arc
        self.index = index
        if isinstance(modes, str):
            modes = [modes] * self.arc.ring_count
        if len(modes) != self.arc.ring_count:
            raise ValueError(f"Modes must contain either 1 or {self.arc.ring_count} values")

        for mode in modes:
            if mode not in self.arc.ring_classes.keys():
                raise ValueError("Invalid ring mode: %s" % mode)

        self.modes = modes
        self.rings: list[ArcRing] = []
        for index, mode in enumerate(self.modes):
            ring = self.arc.ring_classes[mode](self, index)
            self.rings.append(ring)

        self.sensitivity = 1.0
        self.normalise = False
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
    
    def remove_handler(self, callback: Callable):
        if callback in self.handlers:
            self.handlers.remove(callback)
        else:
            raise ValueError("Handler not found in page handlers")

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
        logger.debug("Ring encoder delta: %d, %s" % (ring, delta))
        delta = delta * self.sensitivity

        self.rings[ring]._handle_ring_enc(delta)

        self.draw_ring(ring)

    def draw(self):
        for ring in range(self.ring_count):
            self.draw_ring(ring)

    def draw_ring(self, ring):
        self.rings[ring].draw()
