import logging

from typing import Union, Optional, Callable
from .page import ArcPage
from .arc import Arc

logger = logging.getLogger(__name__)


class ArcUI (Arc):
    def __init__(self,
                 ring_count: int = 4,
                 led_count: int = 64,
                 sensitivity: float = 1.0,
                 normalise: bool = False):
        super().__init__(ring_count, led_count)

        #--------------------------------------------------------------------------------
        # Create pages
        #--------------------------------------------------------------------------------
        self.pages: list[ArcPage] = []
        self.current_page_index = -1
        self._sensitivity = sensitivity
        self._normalise = normalise

        from .ring import ArcRingBipolar, ArcRingAngular, ArcRingUnipolar, ArcRingReel

        self.ring_classes = {}
        self.register_ring_class("bipolar", ArcRingBipolar)
        self.register_ring_class("unipolar", ArcRingUnipolar)
        self.register_ring_class("angular", ArcRingAngular)
        self.register_ring_class("reel", ArcRingReel)

    def register_ring_class(self, name: str, cls: type):
        self.ring_classes[name] = cls

    def add_page(self,
                 modes: Union[str, list[str]] = "bipolar",
                 handler: Optional[Callable] = None) -> ArcPage:
        page = ArcPage(arc=self,
                       index=len(self.pages),
                       modes=modes)
        self.pages.append(page)
        if handler:
            page.add_handler(handler)
        page.sensitivity = self.sensitivity
        page.normalise = self._normalise
        if len(self.pages) == 1:
            self.current_page_index = 0
            self.draw()
        return page

    @property
    def current_page(self) -> ArcPage:
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

    def get_normalise(self):
        return self._normalise

    def set_normalise(self, normalise: bool):
        self._normalise = normalise
        for page in self.pages:
            page.normalise = normalise

    normalise = property(get_normalise, set_normalise)

    def draw(self):
        if len(self.pages) > 0:
            self.current_page.draw()

    def draw_ring(self, ring):
        self.current_page.draw_ring(ring)

    def _osc_handle_enc_delta(self, address: str, ring: int, delta: int):
        """
        Override the default OSC handler, and forward it to the current page.
        """
        logger.debug("Ring encoder delta: %d, %s" % (ring, delta))
        self.current_page._handle_enc_delta(ring, delta)
    
    def _osc_handle_enc_key(self, address: str, key: int, down: int):
        """
        Override the default OSC handler, and forward it to the current page.
        """
        from .event import ArcKeyEvent

        logger.debug("Ring encoder key: %d, %s" % (key, down))
        self.current_page._handle_enc_key(key, down)
        event = ArcKeyEvent(key, down)
        for handler in self.key_handlers:
            handler(event)


if __name__ == "__main__":
    arcui = ArcUI(sensitivity=0.25)
    arcui_bi = arcui.add_page("bipolar")
    arcui_uni = arcui.add_page("unipolar")
    arcui_ang = arcui.add_page("angular")
    arcui_reel = arcui.add_page("reel")
    arcui_reel.sensitivity = 0.1

    @arcui.handler
    def _(event):
        print("Handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_bi.handler
    def _(event):
        print("Bipolar handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_uni.handler
    def _(event):
        print("Unipolar handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_ang.handler
    def _(event):
        print("Angular handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    import threading, time
    def runloop():
        while True:
            time.sleep(0.05)
            for ring in arcui_reel.rings:
                ring.position += 1
                ring.draw()
    thread = threading.Thread(target=runloop, daemon=True)
    thread.start()

    while True:
        try:
            page_index = input("Enter page number [0123]$ ")
            print(page_index)
            page_index = int(page_index.strip())
            arcui.set_current_page(page_index)
        except Exception as e:
            print("Exiting...")
            print(e)
            break
