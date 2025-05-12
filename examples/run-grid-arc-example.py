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
    arcui = ArcUI(normalise=True)
    arcpage = arcui.add_page("unipolar")

    gridui = GridUI()
    gridpage = gridui.add_page("levels", num_levels=arcui.ring_count)

    #--------------------------------------------------------------------------------
    # When an Arc ring is turned, display the same level on the corresponding row
    # of the Grid.
    #--------------------------------------------------------------------------------
    @arcpage.handler
    def _(event):
        level = int(event.position * (gridui.width - 1))
        gridpage.set_level(event.ring.index, level)

    #--------------------------------------------------------------------------------
    # ...and vice versa.
    #--------------------------------------------------------------------------------
    @gridpage.handler
    def _(event):
        level = float(event.x / (gridui.width - 1))
        arcpage.rings[event.y].position = level
        arcpage.draw()

    while True:
        time.sleep(1)
