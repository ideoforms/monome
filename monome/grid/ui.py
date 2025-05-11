import logging

from .page import GridPage, GridPageKeyboard, GridPageScaleMatrix, GridPageFreeform, GridPageHorizontalLevels
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
        self.led_intensity_low = 3

        self.page_classes = {}
        self.register_page_class("keyboard", GridPageKeyboard)
        self.register_page_class("scale_matrix", GridPageScaleMatrix)
        self.register_page_class("freeform", GridPageFreeform)
        self.register_page_class("levels", GridPageHorizontalLevels)

    def register_page_class(self, name: str, cls: type):
        self.page_classes[name] = cls

    def add_page(self, mode: str = "freeform", **kwargs) -> GridPage:
        page = self.page_classes[mode](self, **kwargs)
        self.pages.append(page)
        if len(self.pages) == 1:
            self.current_page_index = 0
            self.clear()
            self.draw()
        return page

    @property
    def current_page(self) -> GridPage:
        return self.pages[self.current_page_index]

    def set_current_page(self, index: int):
        if not index in list(range(len(self.pages))):
            raise ValueError("Invalid page index: %d" % index)
        self.current_page_index = index
        self.clear()
        self.draw()
    
    def clear(self):
        self.led_all(0)
    
    def draw(self):
        if len(self.pages) > 0:
            self.current_page.draw()

    def _osc_handle_grid_key(self, address: str, x: int, y: int, down: int):
        """
        Override the default OSC handler, and forward it to the current page.
        """
        logger.debug("Grid key: %d, %d, %d" % (x, y, down))
        self.current_page._handle_grid_key(x, y, down)