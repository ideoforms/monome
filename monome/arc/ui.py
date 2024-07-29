import logging

from typing import Union
from .page import ArcPage
from .arc import Arc

logger = logging.getLogger(__name__)


class ArcUI (Arc):
    def __init__(self,
                 ring_count: int = 4,
                 led_count: int = 64,
                 sensitivity: float = 1.0):
        super().__init__(ring_count, led_count)

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages: list[ArcPage] = []
        self.current_page_index = -1
        self._sensitivity = sensitivity

    def add_page(self, modes: Union[str, list[str]] = "bipolar"):
        page = ArcPage(arc=self,
                       modes=modes)
        self.pages.append(page)
        page.sensitivity = self.sensitivity
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
    
    def get_sensitivity(self):
        return self._sensitivity

    def set_sensitivity(self, sensitivity: float):
        self._sensitivity = sensitivity
        for page in self.pages:
            page.sensitivity = sensitivity

    sensitivity = property(get_sensitivity, set_sensitivity)

    def draw(self):
        if len(self.pages) > 0:
            self.current_page.draw()

    def draw_ring(self, ring):
        self.current_page.draw_ring(ring)

    def _osc_handle_ring_enc(self, address: str, ring: int, delta: int):
        """
        Override the default OSC handler, and forward it to the current page.
        """
        logger.debug("Ring encoder delta: %d, %s" % (ring, delta))
        self.current_page._handle_ring_enc(ring, delta)


if __name__ == "__main__":
    arcui = ArcUI(sensitivity=0.25)
    arcui_bi = arcui.add_page("bipolar")
    arcui_uni = arcui.add_page("unipolar")
    arcui_ang = arcui.add_page("angular")

    @arcui.handler
    def _(ring, position, delta):
        print("Handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_bi.handler
    def _(ring, position, delta):
        print("Bipolar handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_uni.handler
    def _(ring, position, delta):
        print("Unipolar handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_ang.handler
    def _(ring, position, delta):
        print("Angular handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    while True:
        try:
            page_index = input("Enter page number [012]$ ")
            print(page_index)
            page_index = int(page_index.strip())
            arcui.set_current_page(page_index)
        except Exception as e:
            print("Exiting...")
            print(e)
            break
