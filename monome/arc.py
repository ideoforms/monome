from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import logging
import time

from .serialosc import SerialOSC

ARC_HOST = "127.0.0.1"
ARC_CLIENT_PORT = 13001

serialosc = None
logger = logging.getLogger(__name__)


class Arc:
    def __init__(self, prefix: str = "monome"):
        self.prefix = prefix
        self.enc_handler: callable = None

        global serialosc
        if serialosc is None:
            serialosc = SerialOSC()
        serialosc.await_devices()

        arc_devices = list(filter(
            lambda device: device.device_model == "arc", serialosc.available_devices))
        logger.warning("Arc: got devices: %s" % serialosc.available_devices)
        arc_device = arc_devices[0]
        server_port = arc_device.port
        client_port = ARC_CLIENT_PORT

        dispatcher = Dispatcher()

        def default_handler(address, *args):
            logger.warning("Arc: No handler for message: %s %s" %
                           (address, args))
        dispatcher.map(f"/{self.prefix}/enc/delta", self.handle_ring_enc)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer(
            (ARC_HOST, client_port), dispatcher)
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(ARC_HOST, server_port)

        # self.client.send_message("/sys/info", [])
        self.client.send_message("/sys/port", [client_port])

    def ring_set(self, ring: int, led: int, level: int):
        self.client.send_message(
            f"/{self.prefix}/ring/set", [ring, led, level])

    def ring_all(self, ring: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/all", [ring, level])

    def ring_map(self, ring: int, levels: list[int]):
        assert len(levels) == 64
        self.client.send_message(f"/{self.prefix}/ring/map", [ring, *levels])

    def ring_range(self, ring: int, x1: int, x2: int, level: int):
        self.client.send_message(
            f"/{self.prefix}/ring/range", [ring, x1, x2, level])

    def handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        if self.enc_handler:
            self.enc_handler(ring, delta)

    def handler(self, fn: callable):
        self.enc_handler = fn


def main():
    arc = Arc()
    arc.ring_all(0, 2)
    arc.ring_all(1, 5)

    @arc.handler
    def arc_handler(ring, delta):
        print(ring, delta)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
