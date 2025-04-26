#!/usr/bin/env python3

#------------------------------------------------------------------------
# Monome control for SignalFlow
#------------------------------------------------------------------------
from signalflow import *
from .arc import Arc
import logging

logger = logging.getLogger(__name__)

shared_arc = None

# TODO: Throw an error when two ArcControls use the same ring
class ArcControl(Patch):
    def __init__(self,
                 ring: int,
                 range_min: float = 0.0,
                 range_max: float = 1.0,
                 initial: float = None,
                 mode: str = "absolute",
                 curve: str = "linear"):
        super().__init__()
        global shared_arc

        assert mode in ["absolute"]
        self.value = self.add_input("value")
        self.value_smoothed = Smooth(self.value, 0.999)
        self.set_output(self.value_smoothed)
        self.ring = ring
        self.range_min = range_min
        self.range_max = range_max
        self.curve = curve
        if initial is not None:
            if self.curve == "exponential":
                self._value_norm = scale_exp_lin(initial, range_min, range_max, 0, 1)
            elif self.curve == "linear":
                self._value_norm = scale_lin_lin(initial, range_min, range_max, 0, 1)
        else:
            self._value_norm = 0.5
        self.mode = mode

        if shared_arc is None:
            shared_arc = Arc()
        self.arc = shared_arc

        self.update()

        @self.arc.handler
        def handle_encoder(event_ring: int, delta: int):
            if event_ring == ring:
                # normalise to 0..1
                delta = delta / 7
                # scale down to 0.05 max
                delta = delta * 0.05
                self._value_norm += delta
                self._value_norm = clip(self._value_norm, 0, 1)

                self.update()

    def update(self):
        #--------------------------------------------------------------------------------
        # Update the Arc LED display
        #--------------------------------------------------------------------------------
        ring_ones = int(64 * self._value_norm)
        ring_zeros = 64 - ring_ones
        led_intensity = 7
        self.arc.ring_map(self.ring, ([led_intensity] * ring_ones) + ([0] * ring_zeros))

        #--------------------------------------------------------------------------------
        # Update the SignalFlow node
        #--------------------------------------------------------------------------------
        if self.curve == "exponential":
            value_scaled = scale_lin_exp(self._value_norm, 0, 1, self.range_min, self.range_max)
        elif self.curve == "linear":
            value_scaled = scale_lin_lin(self._value_norm, 0, 1, self.range_min, self.range_max)
        self.set_input("value", value_scaled)

if __name__ == "__main__":
    graph = AudioGraph()
    
    for index, frequency in enumerate([100, 201, 403, 805]):
        sine = SineOscillator(frequency + 5.5) * 0.25 * ArcControl(index)
        StereoPanner(sine).play()
        
    graph.wait()