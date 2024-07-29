import numpy as np
import logging
import time
import math

from typing import Callable

from ..device import MonomeDevice

ARC_HOST = "127.0.0.1"
ARC_CLIENT_PORT = 13001

arc_client_count = 0

logger = logging.getLogger(__name__)


class Arc (MonomeDevice):
    def __init__(self,
                 ring_count: int = 4,
                 led_count: int = 64,
                 prefix: str = "monome"):
        super().__init__(model_name="arc",
                         prefix=prefix)

        self.ring_count = ring_count
        self.led_count = led_count

        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        self.dispatcher.map(f"/{self.prefix}/enc/delta", self._osc_handle_ring_enc)

    #--------------------------------------------------------------------------------
    # Public methods
    #--------------------------------------------------------------------------------

    def ring_set(self, ring: int, led: int, level: int) -> None:
        """
        Set an individual LED to the specified brightness level.

        Args:
            ring (int): The index of the ring. Must be less than `ring_count`.
            led (int): The index of the LED. Must be less than `led_count`.
            level (int): The level to set. Must be between 0 and 15.
        """
        self._validate(ring, led, level)
        self.client.send_message(f"/{self.prefix}/ring/set", [ring, led, level])

    def ring_range(self, ring: int, x1: int, x2: int, level: int):
        """
        Set a range of LEDs to the specified brightness level.

        Args:
            ring (int): The index of the ring. Must be less than `ring_count`.
            x1 (int): The starting index of the LED range. Must be less than `led_count`.
            x2 (int): The ending index of the LED range. Must be less than `led_count`.
            level (int): The level to set. Must be between 0 and 15.
        """
        for led in range(x1, x2):
            self._validate(ring, led, level)
        self.client.send_message(f"/{self.prefix}/ring/range", [ring, x1, x2, level])

    def ring_all(self, ring: int, level: int) -> None:
        """
        Set all of a ring's LEDs to the specified brightness level.

        Args:
            ring (int): The index of the ring. Must be less than `ring_count`.
            level (int): The level to set. Must be between 0 and 15.
        """
        self._validate(ring, None, level)
        self.client.send_message(f"/{self.prefix}/ring/all", [ring, level])

    def ring_map(self, ring: int, levels: list[int]):
        """
        Set the ring's LED values to the list of brightness values in `levels`.

        Args:
            ring (int): The index of the ring. Must be less than `ring_count`.
            levels (int): The list of levels to set. Must be the same length as `led_count`.
        """

        if len(levels) != self.led_count:
            raise ValueError("The number of levels specified must be equal to the ring's led_count (%d != %d)" % (len(levels), self.led_count))
        for level in levels:
            self._validate(ring, None, level)

        # Cast numpy array to a Python list
        if isinstance(levels, np.ndarray):
            levels = levels.tolist()

        self.client.send_message(f"/{self.prefix}/ring/map", [ring, *levels])

    #--------------------------------------------------------------------------------
    # Validation
    #--------------------------------------------------------------------------------

    def _validate(self, ring: int, led: int, level: int):
        if ring < 0 or ring >= self.ring_count:
            raise ValueError("Invalid ring index. Must be between 0 and %d" % (self.ring_count - 1))
        if led is not None and (led < 0 or led >= self.led_count):
            raise ValueError("Invalid LED index. Must be between 0 and %d" % (self.led_count - 1))
        if level < 0 or level > 15:
            raise ValueError("Invalid brightness level. Must be between 0 and 15")

    #--------------------------------------------------------------------------------
    # Handlers
    #--------------------------------------------------------------------------------

    def add_handler(self, handler: Callable):
        """
        Add a handler to receive events from the Arc.

        Args:
            handler (Callable): A function that is called when a rotation event is detected.
                                Must have the signature: method(ring: int, delta: int)
        """
        super().add_handler(handler)

    def _osc_handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Ring encoder event received: ring %d, delta %d" % (ring, delta))
        for handler in self.handlers:
            handler(ring, delta)


if __name__ == "__main__":
    arc = Arc()

    for ring in range(4):
        arc.ring_all(ring, 0)

    @arc.handler
    def arc_handler(ring, delta):
        print("Handling event: ring = %d, delta = %d" % (ring, delta))
        delta_abs = int(math.fabs(delta))
        delta_abs = max(-arc.led_count, min(arc.led_count, delta_abs))
        ones = [15] * delta_abs
        zeros = [0] * (arc.led_count - delta_abs)
        display = (ones + zeros) if delta > 0 else (zeros + ones)
        arc.ring_map(ring, display)

    while True:
        time.sleep(1)
