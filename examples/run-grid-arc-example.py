#--------------------------------------------------------------------------------
# Synchronise displays between a Grid and an Arc.
#--------------------------------------------------------------------------------

from monome import Grid, ArcUI
import time

if __name__ == "__main__":
    #--------------------------------------------------------------------------------
    # Initialise and clear both displays.
    #--------------------------------------------------------------------------------
    grid = Grid()
    grid.led_level_all(0)

    arcui = ArcUI()
    page = arcui.add_page("unipolar")

    #--------------------------------------------------------------------------------
    # When an Arc ring is turned, display the same level on the corresponding row
    # of the Grid.
    #--------------------------------------------------------------------------------
    @arcui.handler
    def _(ring, position, delta):
        level = position // 4
        row_map = ([8] * level) + ([0] * (grid.width - level))
        grid.led_level_row(0, ring, row_map)

    #--------------------------------------------------------------------------------
    # ...and vice versa.
    #--------------------------------------------------------------------------------
    @grid.handler
    def _(x, y, on):
        if y < page.ring_count and on:
            level = x * 4
            page.set_position(y, level)
            
            row_map = ([8] * (x + 1)) + ([0] * (grid.width - (x + 1)))
            grid.led_level_row(0, y, row_map)

    while True:
        time.sleep(1)
