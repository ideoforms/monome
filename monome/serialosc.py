from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from dataclasses import dataclass
import threading
import datetime
import logging
import time

from .exceptions import NoDevicesFoundError

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

    def await_devices(self, timeout: float = 0.5):
        """
        Wait until a device is found.

        Args:
            timeout (float, optional): Time to wait. If None, waits indefinitely. Defaults to 0.5.

        Raises:
            NoDevicesFoundError: No devices were found before the timeout interval.
        """
        t0 = datetime.datetime.now()
        while len(self.available_devices) == 0:
            time.sleep(0.01)
            t1 = datetime.datetime.now()
            if timeout and ((t1 - t0).total_seconds() > timeout):
                raise NoDevicesFoundError("No Monome devices were found")
