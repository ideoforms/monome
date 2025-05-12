from ..page import ArcPage

class ArcRing:
    def __init__(self, page: ArcPage, index: int):
        self.page = page
        self.index = index
        self.arc = self.page.arc
        self._position = 0

    def _call_handlers(self, position: float, delta: float):
        from ..event import ArcUIRotationEvent
        for handler in self.handlers + self.page.handlers:
            if self.normalise:
                event = ArcUIRotationEvent(self, position / self.led_count, delta / self.led_count)
            else:
                event = ArcUIRotationEvent(self, position, delta)
            handler(event)

    def get_position(self):
        if self.normalise:
            return self._position / self.led_count
        else:
            return self._position
    
    def set_position(self, position: float):
        if self.normalise:
            self._position = int(position * self.led_count)
        else:
            self._position = int(position)
    
    position = property(get_position, set_position)

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

    @property
    def sensitivity(self):
        return self.page.sensitivity

    @property
    def normalise(self):
        return self.page.normalise
    
    @property
    def handlers(self):
        return self.page.handlers + self.arc.handlers