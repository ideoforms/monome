from ..page import ArcPage

class ArcRing:
    def __init__(self, page: ArcPage, index: int):
        self.page = page
        self.index = index
        self.arc = self.page.arc

    @property
    def ring_count(self):
        return self.arc.ring_count

    @property
    def led_count(self):
        return self.arc.led_count

    @property
    def led_intensity_fill(self):
        return self.page.led_intensity_fill

    @property
    def led_intensity_cursor(self):
        return self.page.led_intensity_cursor
