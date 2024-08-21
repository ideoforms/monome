import time
import logging

from .page import GridPage, GridPageKeyboard, GridPageScaleMatrix, GridPageButtons
from .grid import Grid

logger = logging.getLogger(__name__)

class GridUI (Grid):
    def __init__(self):
        super().__init__()

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages: list[GridPage] = []
        self.current_page_index = -1

        self.led_intensity_high = 15
        self.led_intensity_medium = 10
        self.led_intensity_low = 5

        self.page_classes = {}
        self.register_page_class("buttons", GridPageButtons)
        self.register_page_class("keyboard", GridPageKeyboard)
        self.register_page_class("scale_matrix", GridPageScaleMatrix)

    def register_page_class(self, name: str, cls: type):
        self.page_classes[name] = cls

    def add_page(self, mode: str = "buttons"):
        page = self.page_classes[mode](self)
        self.pages.append(page)
        if len(self.pages) == 1:
            self.current_page_index = 0
            self.draw()
        return page

    @property
    def current_page(self):
        return self.pages[self.current_page_index]

    def set_current_page(self, index: int):
        if not index in list(range(len(self.pages))):
            raise ValueError("Invalid page index: %d" % index)
        self.current_page_index = index
        self.draw()
    
    def draw(self):
        if len(self.pages) > 0:
            self.current_page.draw()

    def _osc_handle_grid_key(self, address: str, x: int, y: int, down: int):
        """
        Override the default OSC handler, and forward it to the current page.
        """
        logger.debug("Grid key: %d, %d, %d" % (x, y, down))
        self.current_page._handle_grid_key(x, y, down)


if __name__ == "__main__":
    while True:
        time.sleep(1)