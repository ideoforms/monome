# monomeui

A Python package for interfacing with the [monome](https://monome.org/) Grid and Arc controllers. This library uses classic synchronous I/O, providing an alternative to the [pymonome](https://github.com/artfwo/pymonome) async library.

Two levels of interface are provided:

 - `Grid` and `Arc` provide low-level APIs directly to the SerialOSC commands, to modify the visual state and capture button presses and ring rotation events
 - `GridUI` and `ArcUI` encapsulate different high-level user interface paradigms, including unipolar/bipolar value displays. These interfaces support page-based rendering which can maintain and return states for different pages.

```
# Example: Arc UI
arcui = ArcUI()
page = arcui.add_page("unipolar")

@page.handler
def handler(ring, level, delta):
  print("Ring %d set to level %d" % (ring, level))
```

## Requirements

 - A Monome [Grid](https://monome.org/docs/grid/) (tested with a 2021-edition 128, but should work with any generation) or [Arc](https://monome.org/docs/arc/) (tested with a 4-ring v2)
 - A computer running the [serialosc](https://monome.org/docs/serialosc/osc/) server (tested on macOS Ventura)
 - Python 3.9 or above

## Usage

Connect your monome device via USB. To test that the library works:

```sh
# run a test sequence on a grid, responding to button presses
python3 -m monome.grid.grid 

# run a test sequence on an arc, responding to ring rotations
python3 -m monome.arc.arc 
```

## Examples

Further examples are available in [examples](examples).