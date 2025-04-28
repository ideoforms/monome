#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Synchronise displays between a Grid and an Arc.
#--------------------------------------------------------------------------------

from monome import GridUI, ArcUI
import time

if __name__ == "__main__":
    #--------------------------------------------------------------------------------
    # Initialise and clear both displays.
    #--------------------------------------------------------------------------------
    arcui = ArcUI()
    arcpage = arcui.add_page("unipolar")

    gridui = GridUI()
    gridpage = gridui.add_page("levels_horizontal", num_levels=arcui.ring_count)

    scale_factor = arcui.led_count // gridui.width

    #--------------------------------------------------------------------------------
    # When an Arc ring is turned, display the same level on the corresponding row
    # of the Grid.
    #--------------------------------------------------------------------------------
    @arcpage.handler
    def _(ring, position, delta):
        level = int(round(position)) // scale_factor
        gridpage.set_level(ring.index, level)

    #--------------------------------------------------------------------------------
    # ...and vice versa.
    #--------------------------------------------------------------------------------
    @gridpage.handler
    def _(page, y, x):
        level = (x + 1) * scale_factor
        arcpage.rings[y].position = level
        arcpage.draw()   

    while True:
        time.sleep(1)
