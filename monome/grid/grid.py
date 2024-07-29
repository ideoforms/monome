import random
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import logging
import time

from typing import Callable

from ..serialosc import SerialOSC

GRID_HOST = "127.0.0.1"
GRID_CLIENT_PORT = 14001

grid_client_count = 0

logger = logging.getLogger(__name__)


class Grid:
    def __init__(self,
                 width: int = 16,
                 height: int = 8,
                 prefix: str = "monome"):
        """
        A Monome Grid device.

        Args:
            width (int, optional): The number of cells in the Grid's horizontal axis. Defaults to 16.
            height (int, optional): The number of cells in the Grid's vertical axis. Defaults to 8.
            prefix (str, optional): The OSC prefix. Defaults to "monome".
        """
        global grid_client_count

        self.width = width
        self.height = height
        self.prefix = prefix
        self.handlers: list[Callable] = []

        #--------------------------------------------------------------------------------
        # Initialise SerialOSC connection and locate the first Grid device.
        # Only one Grid is currently supported.
        #--------------------------------------------------------------------------------
        serialosc = SerialOSC()
        serialosc.await_devices()

        grid_devices = list(filter(lambda device: device.device_model == "one", serialosc.available_devices))
        grid_device = grid_devices[0]
        server_port = grid_device.port
        client_port = GRID_CLIENT_PORT + grid_client_count
        grid_client_count = grid_client_count + 1

        #--------------------------------------------------------------------------------
        # Set up OSC bindings
        #--------------------------------------------------------------------------------
        dispatcher = Dispatcher()

        dispatcher.map(f"/{self.prefix}/grid/key", self._osc_handle_grid_key)
        dispatcher.map(f"/sys/port", self._osc_handle_sys_port)
        dispatcher.set_default_handler(self._osc_handle_unknown_message)

        self.server = ThreadingOSCUDPServer((GRID_HOST, client_port), dispatcher)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        self.client = SimpleUDPClient(GRID_HOST, server_port)
        self.client.send_message("/sys/port", [client_port])

    #--------------------------------------------------------------------------------
    # led_intensity
    #--------------------------------------------------------------------------------

    def led_intensity(self, level: int):
        """
        Set the global LED intensity.

        Args:
            level (int): The intensity, from 1 to 15.
        """
        self.client.send_message(f"/{self.prefix}/grid/led/intensity", [level])

    #--------------------------------------------------------------------------------
    # led_set/led_level_set
    #--------------------------------------------------------------------------------

    def led_set(self, x: int, y: int, on: int):
        self._validate_binary(x, y, on)
        self.client.send_message(f"/{self.prefix}/grid/led/set", [x, y, on])

    def led_level_set(self, x: int, y: int, level: int):
        self._validate_varibright(x, y, level)
        self.client.send_message(f"/{self.prefix}/grid/led/level/set", [x, y, level])

    #--------------------------------------------------------------------------------
    # led_all/led_level_all
    #--------------------------------------------------------------------------------

    def led_all(self, on: int):
        self._validate_binary(0, 0, on)
        self.client.send_message(f"/{self.prefix}/grid/led/all", [on])

    def led_level_all(self, level: int):
        self._validate_varibright(0, 0, level)
        self.client.send_message(f"/{self.prefix}/grid/led/level/all", [level])

    #--------------------------------------------------------------------------------
    # led_row/led_level_row
    #--------------------------------------------------------------------------------

    def led_row(self, x_offset: int, y: int, on: list[int]):
        for value in on:
            self._validate_binary(x_offset, y, value)
        values_packed = self._pack_binary(on)
        self.client.send_message(f"/{self.prefix}/grid/led/row", [x_offset, y, *values_packed])

    def led_level_row(self, x_offset: int, y: int, levels: list[int]):
        for level in levels:
            self._validate_varibright(x_offset, y, level)
        self.client.send_message(f"/{self.prefix}/grid/led/level/row", [x_offset, y, *levels])

    #--------------------------------------------------------------------------------
    # led_col/led_level_col
    #--------------------------------------------------------------------------------

    def led_col(self, x: int, y_offset: int, on: list[int]):
        for value in on:
            self._validate_binary(x, y_offset, value)
        values_packed = self._pack_binary(on)
        self.client.send_message(f"/{self.prefix}/grid/led/row", [x, y_offset, *values_packed])

    def led_level_col(self, x: int, y_offset: int, levels: int):
        for level in levels:
            self._validate_varibright(x, y_offset, level)
        self.client.send_message(f"/{self.prefix}/grid/led/level/col", [x, y_offset, *levels])

    #--------------------------------------------------------------------------------
    # led_map
    #--------------------------------------------------------------------------------

    def led_map(self, x: int, y_offset: int, levels: list[int]):
        self.client.send_message(f"/{self.prefix}/grid/led/map", [x, y_offset, *levels])

    #--------------------------------------------------------------------------------
    # Handlers
    #--------------------------------------------------------------------------------

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    def handler(self, handler: Callable):
        """
        Used for the @grid.handler decorator.

        Args:
            handler (callable): The handler to add.
        """
        self.add_handler(handler)

    #--------------------------------------------------------------------------------
    # Validation and packing
    #--------------------------------------------------------------------------------

    def _validate_binary(self, x: int, y: int, on: int):
        if x not in range(self.width):
            raise ValueError(f"x must be between 0 and {self.width - 1}")
        if y not in range(self.height):
            raise ValueError(f"y must be between 0 and {self.height - 1}")
        if on not in range(2):
            raise ValueError("level must be either 0 or 1. For variable brightness, use the _level_ methods.")
        
    def _validate_varibright(self, x: int, y: int, level: int):
        if x not in range(self.width):
            raise ValueError(f"x must be between 0 and {self.width - 1}")
        if y not in range(self.height):
            raise ValueError(f"y must be between 0 and {self.height - 1}")
        if level not in range(16):
            raise ValueError("level must be between 0 and 15")

    def _pack_binary(self, on: list[int]):
        if len(on) not in [8, 16]:
            raise ValueError("led_row: Invalid length of on (must be 8 or 16)")
        values_packed = []
        values_packed.append(sum(j << i for i, j in enumerate(reversed(on[:8]))))
        if len(on) == 16:
            values_packed.append(sum(j << i for i, j in enumerate(reversed(on[8:16]))))
        return values_packed

    #--------------------------------------------------------------------------------
    # OSC handlers
    #--------------------------------------------------------------------------------

    def _osc_handle_grid_key(self, address: str, x: int, y: int, down: bool):
        logger.debug("Key press: %d, %d, %d" % (x, y, down))
        for handler in self.handlers:
            handler(x, y, down)

    def _osc_handle_sys_port(self, address: str, port: int):
        pass

    def _osc_handle_unknown_message(address, *args):
        logger.warning("Grid: No handler for message: %s %s" % (address, args))


if __name__ == "__main__":
    grid = Grid()
    grid.led_level_all(0)

    @grid.handler
    def _(x, y, down):
        if x == 0:
            if y == 0:
                grid.led_level_all(int(down) * 10)
            else:
                grid.led_level_row(x, y, list(range(grid.width)) if down else [0] * grid.width)
        elif y == 0:
            grid.led_level_col(x, y, list(range(grid.height)) if down else [0] * grid.height)
        else:
            grid.led_level_set(x, y, int(down) * 10)

    while True:
        x = random.randrange(0, grid.width)
        y = random.randrange(0, grid.height)
        grid.led_level_set(x, y, random.choice([0, 5]))
        time.sleep(0.05)
