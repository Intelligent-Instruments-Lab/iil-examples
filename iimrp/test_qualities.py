"""
Authors:
  Victor Shepardson
  Jack Armitage
  Intelligent Instruments Lab 2022
"""

import numpy as np
import random
from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(host="127.0.0.1", receive_port=8888, send_port=7770):

    osc = OSC(host, receive_port, send_port)
    osc.create_client("mrp", port=send_port)

    mrp = None
    note_on = False
    note = 48
    count = 100 # frames
    counter = 0

    @osc.args(return_port=7777)
    def reset(address, kind=None):
        """
        reset the mrp
        """
        print("Resetting MRP...")
        nonlocal mrp, note
        mrp = MRP(osc)
        mrp.all_notes_off()
        mrp.note_on(note)

    reset(None)
    
    def create_array(N, l):
        return np.linspace(-N/2, N/2, l)

    @repeat(0.1)
    def _():
        nonlocal note, count, counter
        pitch_arr = create_array(24, count)
        mrp.set_note_quality(note, 'intensity', 1.0)#counter/count)
        # mrp.set_note_quality(note, 'brightness', counter/count)
        # mrp.set_note_quality(note, 'harmonic', counter/count)
        mrp.set_note_quality(note, 'pitch', pitch_arr[counter])
        counter+=1
        if counter == count:
            print(f"turning note {note} off.")
            mrp.note_off(note)
            note = random.randint(21, 108)
            print(note, type(note))
            counter=0
        print(f"{counter}/{count}, note: {note}, pitch: {pitch_arr[counter]}")

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
