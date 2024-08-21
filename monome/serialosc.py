from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from singleton_decorator import singleton
from dataclasses import dataclass
import threading
import datetime
import logging
import time

from .exceptions import NoDevicesFoundError

SERIALOSC_HOST = "127.0.0.1"
SERIALOSC_SERVER_PORT = 12002

logger = logging.getLogger(__name__)


@dataclass
class DeviceSpec:
    device_id: str
    device_type: str
    port: int

    def __post_init__(self):
        parts = self.device_type.split(" ")
        self.device_manufacturer = parts[0]
        self.device_model = parts[1]
        self.device_version = parts[2] if len(parts) >= 3 else None

#--------------------------------------------------------------------------------
# SerialOSC is a singleton class, with one instance shared across all clients.
#--------------------------------------------------------------------------------

@singleton
class SerialOSC:
    def __init__(self):
        dispatcher = Dispatcher()

        dispatcher.map("/serialosc/device", self._osc_handle_device_listed)
        dispatcher.map("/serialosc/add", self._osc_handle_device_added)
        dispatcher.map("/serialosc/remove", self._osc_handle_device_removed)
        dispatcher.set_default_handler(self._osc_handle_unknown_message)

        #--------------------------------------------------------------------------------
        # Listen on a random UDP port
        #--------------------------------------------------------------------------------
        self.server = ThreadingOSCUDPServer((SERIALOSC_HOST, 0), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.server_port = self.server.socket.getsockname()[1]

        self.client = SimpleUDPClient(SERIALOSC_HOST, SERIALOSC_SERVER_PORT)
        self.client.send_message("/serialosc/list", [SERIALOSC_HOST, self.server_port])
        self.available_devices: list[DeviceSpec] = []

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

    def _serialosc_register(self):
        self.client.send_message("/serialosc/notify", [SERIALOSC_HOST, self.server_port])

    def _osc_handle_unknown_message(self, address, *args):
        logger.warning("SerialOSC: No handler for message: %s %s" % (address, args))

    def _osc_handle_device_listed(self, address, device_id, device_model, port):
        logger.info("Discovered serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.append(device)
        self._serialosc_register()

    def _osc_handle_device_added(self, address, device_id, device_model, port):
        logger.info("Added serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.remove(device)
        self._serialosc_register()

    def _osc_handle_device_removed(self, address, device_id, device_model, port):
        logger.info("Removed serial OSC device: %s (model %s, port %d)" % (device_id, device_model, port))
        device = DeviceSpec(device_id, device_model, port)
        self.available_devices.remove(device)
        self._serialosc_register()
