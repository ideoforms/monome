from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import threading
import logging

from typing import Callable

from .serialosc import SerialOSC

MONOME_HOST = "127.0.0.1"
MONOME_CLIENT_PORT = 14001

monome_client_count = 0

logger = logging.getLogger(__name__)

class MonomeDevice:
    def __init__(self,
                 model_name: str = "one",
                 prefix: str = "monome"):
        """
        A generic Monome device.
        """
        global monome_client_count

        self.prefix = prefix
        self.handlers: list[Callable] = []

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Grid device.
        # Only one Grid is currently supported.
        #--------------------------------------------------------------------------------
        serialosc = SerialOSC()
        serialosc.await_devices()

        self.client_port = MONOME_CLIENT_PORT + monome_client_count
        monome_client_count = monome_client_count + 1

        available_devices = list(filter(lambda device: device.device_model == model_name, serialosc.available_devices))
        device = available_devices[0]
        server_port = device.port

        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        self.dispatcher = Dispatcher()
        self.dispatcher.map(f"/sys/port", self._osc_handle_sys_port)
        self.dispatcher.set_default_handler(self._osc_handle_unknown_message)

        self.server = ThreadingOSCUDPServer((MONOME_HOST, self.client_port), self.dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        self.client = SimpleUDPClient(MONOME_HOST, server_port)
        self.client.send_message("/sys/port", [self.client_port])

    #--------------------------------------------------------------------------------
    # Handlers
    #--------------------------------------------------------------------------------

    def add_handler(self, handler: Callable):
        """
        Add a handler to receive events from the device.

        Args:
            handler (Callable): A function that is called when an event is received.
        """
        self.handlers.append(handler)

    def handler(self, handler: Callable):
        """
        Used for the @device.handler decorator.

        Args:
            handler (callable): The handler to add.
        """
        self.add_handler(handler)

    #--------------------------------------------------------------------------------
    # OSC handlers
    #--------------------------------------------------------------------------------

    def _osc_handle_sys_port(self, address: str, port: int):
        pass

    def _osc_handle_unknown_message(self, address: str, *args):
        logger.warning(f"{self.__class__}: No handler for message: {address}, {args}")
