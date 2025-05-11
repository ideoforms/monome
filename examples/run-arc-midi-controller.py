#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Example: Use Arc as a MIDI control device.
#  - The four rings are mapped to MIDI CCs 0-3, with four pages of rings,
#    allowing for 16 CCs in total.
#  - When a ring is turned, the corresponding CC is sent with a value
#    between 0 and 127.
#  - The page index can be set by entering a number between 0 and 3.
#--------------------------------------------------------------------------------

from monome import ArcUI
import argparse
import mido

def main(output_device=None,
         list_output_devices=False):
    
    if list_output_devices:
        print("Available MIDI output devices:")
        for name in mido.get_output_names():
            print(f" - {name}")
        return
    
    midi = mido.open_output(output_device) 
    arcui = ArcUI(sensitivity=0.5, normalise=True)

    def ring_handler(event):
        cc = event.ring.index + (event.ring.page.index * arcui.ring_count)
        value = int(event.position * 127)
        print(f"Sending CC {cc} with value {value}")
        midi.send(mido.Message('control_change', channel=0, control=cc, value=value))
    
    for _ in range(4):
        arcui.add_page(modes="unipolar", handler=ring_handler)
    
    def key_handler(event):
        if event.down:
            page_index = (arcui.current_page_index + 1) % len(arcui.pages)
            print("Changing page: %d" % page_index)
            arcui.set_current_page(page_index)
    arcui.add_key_handler(key_handler)

    while True:
        page_index = int(input("Enter page index (0-3): "))
        if page_index < 0 or page_index > 3:
            print("Invalid page index. Please enter a number between 0 and 3.")
            continue
        arcui.set_current_page(page_index)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Arc MIDI controller example.")
    parser.add_argument("--output-device", type=str, help="MIDI output device name.")
    parser.add_argument("--list-output-devices", action="store_true", help="List available MIDI output devices.")
    args = parser.parse_args()

    main(output_device=args.output_device,
         list_output_devices=args.list_output_devices)