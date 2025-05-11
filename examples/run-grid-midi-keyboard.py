#!/usr/bin/env python3

from monome import GridUI
import argparse
import time
import mido


def main(mode="scale_matrix"):
    gridui = GridUI()
    page = gridui.add_page(mode)
    output = mido.open_output()

    @page.handler
    def _(event):
        if event.down:
            output.send(mido.Message("note_on", note=event.note, velocity=64))
            print("Key down: %d" % event.note)
        else:
            output.send(mido.Message("note_off", note=event.note))
            print("Key up: %d" % event.note)

    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a MIDI keyboard with the monome grid.")
    parser.add_argument("--mode", type=str, default="scale_matrix", help="Can be either 'scale_matrix' or 'keyboard'.")
    args = parser.parse_args()

    if args.mode not in ["scale_matrix", "keyboard"]:
        raise ValueError("Invalid mode. Choose either 'scale_matrix' or 'keyboard'.")
    main(args.mode)
