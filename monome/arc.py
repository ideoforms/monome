from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import threading
import logging
import time

SERIALOSC_HOST = "127.0.0.1"
SERIALOSC_SERVER_PORT = 12002
SERIALOSC_CLIENT_PORT = 12003
ARC_CLIENT_PORT = 13001

serialosc = None
logger = logging.getLogger(__name__)


@dataclass
class DeviceSpec:
    device_id: str
    device_type: str
    port: int

    def __post_init__(self):
        self.device_manufacturor, self.device_model, self.device_version = self.device_type.split(" ")


class Arc:
    def __init__(self, prefix: str = "monome"):
        self.prefix = prefix
        self.enc_handler: callable = None

        global serialosc
        if serialosc is None:
            serialosc = SerialOSC()
        serialosc.await_devices()

        arc_devices = list(filter(lambda device: device.device_model == "arc", serialosc.available_devices))
        logger.warning("Arc: got devices: %s" % serialosc.available_devices)
        arc_device = arc_devices[0]
        server_port = arc_device.port
        client_port = ARC_CLIENT_PORT

        dispatcher = Dispatcher()
        def default_handler(address, *args):
            logger.warning("Arc: No handler for message: %s %s" % (address, args))
        dispatcher.map(f"/{self.prefix}/enc/delta", self.handle_ring_enc)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer((SERIALOSC_HOST, client_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(SERIALOSC_HOST, server_port)

        # self.client.send_message("/sys/info", [])
        self.client.send_message("/sys/port", [client_port])
        
    def ring_set(self, ring: int, led: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/set", [ring, led, level])

    def ring_all(self, ring: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/all", [ring, level])

    def ring_map(self, ring: int, levels: list[int]):
        assert len(levels) == 64
        self.client.send_message(f"/{self.prefix}/ring/map", [ring, *levels])

    def ring_range(self, ring: int, x1: int, x2: int, level: int):
        self.client.send_message(f"/{self.prefix}/ring/range", [ring, x1, x2, level])
    
    def handle_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        if self.enc_handler:
            self.enc_handler(ring, delta)

    def handler(self, fn: callable):
        self.enc_handler = fn


class SerialOSC:
    def __init__(self):
        dispatcher = Dispatcher()
        def default_handler(address, *args):
            logger.warning("SerialOSC: No handler for message: %s %s" % (address, args))
        dispatcher.map("/serialosc/device", self.handle_device_listed)
        dispatcher.map("/serialosc/add", self.handle_device_added)
        dispatcher.map("/serialosc/remove", self.handle_device_removed)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer((SERIALOSC_HOST, SERIALOSC_CLIENT_PORT), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(SERIALOSC_HOST, SERIALOSC_SERVER_PORT)
        self.client.send_message("/serialosc/list", [SERIALOSC_HOST, SERIALOSC_CLIENT_PORT])
        self.available_devices: list[DeviceSpec] = []
        
    def _serialosc_register(self):
        self.client.send_message("/serialosc/notify", [SERIALOSC_HOST, SERIALOSC_CLIENT_PORT])

    def handle_device_listed(self, address, device_id, device_model, port):
        logger.warning("Found serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.append(device)
        self._serialosc_register()

    def handle_device_added(self, address, device_id, device_model, port):
        logger.warning("Added serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.remove(device)
        self._serialosc_register()

    def handle_device_removed(self, address, device_id, device_model, port):
        logger.warning("Removed serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.remove(device)
        self._serialosc_register()

    def await_devices(self):
        while len(self.available_devices) == 0:
            time.sleep(0.01)

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