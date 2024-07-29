from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import threading
import logging
import time
import math

from typing import Callable

from ..serialosc import SerialOSC

ARC_HOST = "127.0.0.1"
ARC_CLIENT_PORT = 13001

arc_client_count = 0

logger = logging.getLogger(__name__)


class Arc:
    def __init__(self,
                 ring_count: int = 4,
                 led_count: int = 64,
                 prefix: str = "monome"):
        global arc_client_count

        self.ring_count = ring_count
        self.led_count = led_count
        self.prefix = prefix
        self.handlers: list[Callable] = []

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Arc device.
        # Only one Arc is currently supported.
        #--------------------------------------------------------------------------------
        serialosc = SerialOSC()
        serialosc.await_devices()

        arc_devices = list(filter(lambda device: device.device_model == "arc", serialosc.available_devices))
        arc_device = arc_devices[0]
        server_port = arc_device.port
        client_port = ARC_CLIENT_PORT + arc_client_count
        arc_client_count = arc_client_count + 1

        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        dispatcher = Dispatcher()

        def default_handler(address, *args):
            logger.warning("Arc: No handler for message: %s %s" % (address, args))
        dispatcher.map(f"/{self.prefix}/enc/delta", self._osc_handle_ring_enc)
        dispatcher.map(f"/sys/port", self._osc_handle_sys_port)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer((ARC_HOST, client_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(ARC_HOST, server_port)

        self.client.send_message("/sys/port", [client_port])

    def ring_set(self, ring: int, led: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/set", [ring, led, level])

    def ring_all(self, ring: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/all", [ring, level])

    def ring_map(self, ring: int, levels: list[int]):
        # Cast other iterables to a Python list
        if isinstance(levels, np.ndarray):
            levels = levels.tolist()
        assert len(levels) == 64
        self.client.send_message(f"/{self.prefix}/ring/map", [ring, *levels])

    def ring_range(self, ring: int, x1: int, x2: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/range", [ring, x1, x2, level])

    def _osc_handle_sys_port(self, address: str, port: int):
        pass

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    def handler(self, handler: Callable):
        """
        Used for the @arc.handler decorator.

        Args:
            handler (Callable): The handler to add.
        """
        self.add_handler(handler)

    def _osc_handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
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
