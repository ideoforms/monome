from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import logging
import time
import math

from typing import Union

from .serialosc import SerialOSC, serialosc

ARC_HOST = "127.0.0.1"
ARC_CLIENT_PORT = 13001

arc_client_count = 0

logger = logging.getLogger(__name__)


class Arc:
    def __init__(self,
                 modes: Union[str, list[str]] = "bipolar",
                 ring_count: int = 4,
                 led_count: int = 64,
                 prefix: str = "monome"):
        global serialosc
        global arc_client_count

        self.ring_count = ring_count
        self.led_count = led_count
        self.prefix = prefix

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Arc device.
        # Only one Arc is currently supported.
        #--------------------------------------------------------------------------------
        if serialosc is None:
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
        dispatcher.map(f"/{self.prefix}/enc/delta", self.handle_ring_enc)
        dispatcher.map(f"/sys/port", self.handle_sys_port)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer((ARC_HOST, client_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(ARC_HOST, server_port)

        self.client.send_message("/sys/port", [client_port])

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages = []
        self.pages.append(ArcPage(arc=self,
                                  modes=modes))
        self.current_page_index = 0
        self.draw_all()

    def ring_set(self, ring: int, led: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/set", [ring, led, level])

    def ring_all(self, ring: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/all", [ring, level])

    def ring_map(self, ring: int, levels: list[int]):
        assert len(levels) == 64
        self.client.send_message(f"/{self.prefix}/ring/map", [ring, *levels])

    def ring_range(self, ring: int, x1: int, x2: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/range", [ring, x1, x2, level])

    def handle_sys_port(self, address: str, port: int):
        pass

    @property
    def current_page(self):
        return self.pages[self.current_page_index]

    def handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        self.current_page.handle_ring_enc(address, ring, delta)

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
            if mode not in ["unipolar", "bipolar", "relative"]:
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

    def handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        delta = delta * self.sensitivity / 7
        delta = int(math.ceil(delta) if delta > 0 else math.floor(delta))

        if self.modes[ring] == "bipolar":
            self.positions[ring] += delta
            for handler in self.handlers:
                handler(ring, self.positions[ring], delta)

        self.draw(ring)

    def draw(self, ring):
        if self.modes[ring] == "bipolar":
            position = self.positions[ring]

            ones = int(math.fabs(position))
            ones = min(ones, 64)
            zeros = 64 - ones
            if position > 0:
                buf = ([self.led_intensity_fill] * ones) + ([0] * zeros)
            else:
                buf = ([0] * zeros) + ([self.led_intensity_fill] * ones)
            buf[position % 64] = self.led_intensity_cursor
            self.arc.ring_map(ring, buf)

def main():
    arc = Arc(modes="bipolar")
    arc.sensitivity = 0.1

    @arc.handler
    def arc_handler(ring, position, delta):
        print("handled - %d" % position)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
