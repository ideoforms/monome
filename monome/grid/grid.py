from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import logging
import time

from typing import Callable

from ..serialosc import SerialOSC, serialosc

GRID_HOST = "127.0.0.1"
GRID_CLIENT_PORT = 13001

grid_client_count = 0

logger = logging.getLogger(__name__)


class Grid:
    def __init__(self,
                 width: int = 16,
                 height: int = 8,
                 prefix: str = "monome"):
        """_summary_

        Args:
            width (int, optional): The number of cells in the Grid's horizontal axis. Defaults to 16.
            height (int, optional): The number of cells in the Grid's vertical axis. Defaults to 8.
            prefix (str, optional): The OSC prefix. Defaults to "monome".
        """
        global serialosc
        global grid_client_count

        self.width = width
        self.height = height
        self.prefix = prefix
        self.handlers: list[Callable] = []

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Grid device.
        # Only one Grid is currently supported.
        #--------------------------------------------------------------------------------
        if serialosc is None:
            serialosc = SerialOSC()
        serialosc.await_devices()

        grid_devices = list(filter(lambda device: device.device_model == "grid", serialosc.available_devices))
        grid_device = grid_devices[0]
        server_port = grid_device.port
        client_port = GRID_CLIENT_PORT + grid_client_count
        grid_client_count = grid_client_count + 1
        
        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        dispatcher = Dispatcher()

        def default_handler(address, *args):
            logger.warning("Grid: No handler for message: %s %s" % (address, args))
        dispatcher.map(f"/{self.prefix}/led/delta", self.handle_osc_ring_enc)
        dispatcher.map(f"/sys/port", self.handle_sys_port)
        dispatcher.set_default_handler(default_handler)

        self.server = ThreadingOSCUDPServer((GRID_HOST, client_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = SimpleUDPClient(GRID_HOST, server_port)

        self.client.send_message("/sys/port", [client_port])

    def led_set(self, x: int, y: int, level: int):
        self.client.send_message(f"/{self.prefix}/led/set", [x, y, level])

    def led_all(self, level: int):
        self.client.send_message(f"/{self.prefix}/led/all", [level])

    def led_row(self, x: int, y_offset: int, level: int):
        self.client.send_message(f"/{self.prefix}/led/row", [x, y_offset, level])

    def led_col(self, x_offset: int, y: int, level: int):
        self.client.send_message(f"/{self.prefix}/led/col", [x_offset, y, level])

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    def handler(self, handler: Callable):
        """
        Used for the @grid.handler decorator.

        Args:
            handler (callable): The handler to add.
        """
        self.add_handler(handler)

    def handle_osc_led_press(self, address: str, x: int, y: int, down: bool):
        logger.debug("Button press: %d, %s" % (x, y, down))
        for handler in self.handlers:
            handler(x, y, down)


def main():
    grid = Grid()

    @grid.handler
    def grid_handler(x, y, down):
        print(x, y, down)
        grid.led_set(x, y, int(down) * 10)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
