from __future__ import annotations

import time
import logging

from .page import GridPage
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ..ui import GridUI

logger = logging.getLogger(__name__)


@dataclass
class GridKey:
    x: int
    y: int
    mode: str = None
    state: int = 0
    handler: Callable = None
    group: GridControlGroup = None

@dataclass
class GridControlGroup:
    index: int
    controls: list[GridKey]

@dataclass
class GridKeyEvent:
    x: int
    y: int
    down: int

@dataclass
class GridKeyRadioEvent(GridKeyEvent):
    group: GridControlGroup
    selected_index: int



class GridPageFreeform (GridPage):
    def __init__(self,
                 grid: GridUI,
                 mode: str = "freeform"):
        super().__init__(grid, mode)

        self.keys = [[GridKey(x, y) for x in range(grid.width)] for y in range(grid.height)]
        self.control_groups = []
    
    def _handle_grid_key(self, x: int, y: int, down: int):
        logger.debug("Grid key: %d, %d, %s" % (x, y, down))
        key = self.keys[y][x]

        if key.mode is None:
            return
        elif key.mode == "toggle":
            if down:
                key.state = 1 - key.state
                self.grid.led_level_set(x, y, self.grid.led_intensity_high if key.state else self.grid.led_intensity_low)
                if key.handler:
                    event = GridKeyEvent(x, y, key.state)
                    key.handler(event)
        elif key.mode == "momentary":
            if down:
                self.grid.led_level_set(x, y, self.grid.led_intensity_high)
            else:
                self.grid.led_level_set(x, y, self.grid.led_intensity_low)
            if key.handler:
                event = GridKeyEvent(x, y, down)
                key.handler(event)
        elif key.mode == "radio":
            if down:
                group = key.group
                for other_key in group.controls:
                    if other_key.state:
                        other_key.state = 0
                        self.grid.led_level_set(other_key.x, other_key.y, self.grid.led_intensity_low)
                key.state = 1
                self.grid.led_level_set(key.x, key.y, self.grid.led_intensity_high)
                selected_index = group.controls.index(key)
                if key.handler:
                    event = GridKeyRadioEvent(x, y, down, group=group, selected_index=selected_index)
                    key.handler(event)
    
    def add_control_for_key(self, mode: str, x: int, y: int, handler: Callable, group: GridControlGroup = None):
        key = self.keys[y][x]
        if key.mode is not None:
            raise ValueError("Key already has a control assigned (%d, %d)" % (x, y))
        key.mode = mode
        key.handler = handler
        key.group = group
        if group:
            group.controls.append(key)

    # To enable @control_for_key decorator
    def control_for_key(self, mode: str, x: int, y: int):
        def wrapper(handler):
            self.add_control_for_key(mode, x, y, handler)
        return wrapper
    
    def draw(self):
        self.grid.led_level_all(0)
        for y, row in enumerate(self.keys):
            for x, key in enumerate(row):
                if key.mode != None:
                    self.grid.led_level_set(x, y, self.grid.led_intensity_low)
    
    def add_control_group(self):
        control_group = GridControlGroup(len(self.control_groups), [])
        self.control_groups.append(control_group)
        return control_group

if __name__ == "__main__":
    from ..ui import GridUI

    gridui = GridUI()
    page = gridui.add_page("freeform")

    page.add_control_for_key("toggle", 0, 0, lambda event: print("down" if event.down else "up"))
    page.add_control_for_key("momentary", 2, 0, lambda event: print("down" if event.down else "up"))
    page.add_control_for_key("momentary", 3, 0, lambda event: print("down" if event.down else "up"))
    page.add_control_for_key("momentary", 4, 0, lambda event: print("down" if event.down else "up"))

    radio_group = page.add_control_group()
    page.add_control_for_key("radio", 0, 2, lambda event: print("group: %d" % event.selected_index), group=radio_group)
    page.add_control_for_key("radio", 1, 2, lambda event: print("group: %d" % event.selected_index), group=radio_group)
    page.add_control_for_key("radio", 2, 2, lambda event: print("group: %d" % event.selected_index), group=radio_group)

    page.draw()
    
    while True:
        time.sleep(1)