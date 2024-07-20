import logging

from typing import Union, Callable
from .arc import Arc
from .page import ArcPage

logger = logging.getLogger(__name__)


class ArcUI (Arc):
    def __init__(self,
                 ring_count: int = 4,
                 led_count: int = 64):
        super().__init__(ring_count, led_count)

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages = []
        self.current_page_index = -1
        self.handlers: list[callable] = []

    def add_page(self, modes: Union[str, list[str]] = "bipolar"):
        page = ArcPage(arc=self,
                       modes=modes)
        self.pages.append(page)
        if len(self.pages) == 1:
            self.current_page_index = 0
            self.draw_all()
        return page
    
    @property
    def current_page(self):
        return self.pages[self.current_page_index]
    
    def set_current_page(self, index: int):
        if not index in list(range(len(self.pages))):
            raise ValueError("Invalid page index: %d" % index)
        self.current_page_index = index
        self.draw_all()

    def handle_osc_ring_enc(self, address: str, ring: int, delta: int):
        logger.debug("Enc delta: %d, %s" % (ring, delta))
        
        self.current_page.handle_ring_enc(ring, delta)

    def add_handler(self, callback: Callable):
        self.handlers.append(callback)

    # Synonym to enable @arcui.handler decorator
    handler = add_handler

    def get_sensitivity(self):
        return self.current_page.sensitivity
    def set_sensitivity(self, sensitivity: float):
        self.current_page.sensitivity = sensitivity
    sensitivity = property(get_sensitivity, set_sensitivity)

    def draw_all(self):
        if len(self.pages) > 0:
            for ring in range(self.ring_count):
                self.draw(ring)

    def draw(self, ring):
        self.current_page.draw(ring)


def main():
    arcui = ArcUI()
    arcui_bi = arcui.add_page("bipolar")
    arcui_uni = arcui.add_page("unipolar")
    arcui_ang = arcui.add_page("angular")
    arcui.sensitivity = 0.25

    @arcui.handler
    def _(ring, position, delta):
        print("Handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_bi.handler
    def _(ring, position, delta):
        print("Bi handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_uni.handler
    def _(ring, position, delta):
        print("Uni handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))

    @arcui_ang.handler
    def _(ring, position, delta):
        print("Ang handler: ring = %d, position = %f, delta = %f" % (ring, position, delta))


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


if __name__ == "__main__":
    main()
