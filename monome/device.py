from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import threading
import logging

from typing import Callable

from .serialosc import SerialOSC
from .exceptions import NoDevicesFoundError

MONOME_HOST = "127.0.0.1"

logger = logging.getLogger(__name__)

class MonomeDevice:
    def __init__(self,
                 model_name: str = "one",
                 prefix: str = "monome"):
        """
        A generic Monome device.
        """
        self.prefix = prefix
        self.handlers: list[Callable] = []

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Grid device.
        # Only one Grid is currently supported.
        #--------------------------------------------------------------------------------
        serialosc = SerialOSC()
        serialosc.await_devices()

        available_devices = list(filter(lambda device: device.device_model == model_name, serialosc.available_devices))
        try:
            device = available_devices[0]
        except IndexError:
            raise NoDevicesFoundError("No matching monome devices found")

        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        self.dispatcher = Dispatcher()
        self.dispatcher.map(f"/sys/port", self._osc_handle_sys_port)
        self.dispatcher.set_default_handler(self._osc_handle_unknown_message)

        #--------------------------------------------------------------------------------
        # Listen on a random UDP port
        #--------------------------------------------------------------------------------
        self.server = ThreadingOSCUDPServer((MONOME_HOST, 0), self.dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.server_port = self.server.socket.getsockname()[1]

        self.client = SimpleUDPClient(MONOME_HOST, device.port)
        self.client.send_message("/sys/port", [self.server_port])

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
    
    def remove_handler(self, handler: Callable):
        """
        Remove an event handler.

        Args:
            handler (Callable): A function that is called when an event is received.
        """
        if handler not in self.handlers:
            raise ValueError("Handler not found")
        self.handlers.remove(handler)

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
