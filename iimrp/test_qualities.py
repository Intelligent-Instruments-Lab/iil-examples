import numpy as np
import random
from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):
    osc = OSC(kwargs.get('host', '127.0.0.1'), 
              kwargs.get('receive_port', 8888))
    osc.create_client("mrp", port=kwargs.get('send_port', 7770))
    mrp = MRP(osc, record=kwargs.get('record', False))

    mrp = None
    note_on = False
    note = 48
    count = 100 # frames
    counter = 0

    mrp.note_on(note)
    
    def create_array(N, l):
        return np.linspace(-N/2, N/2, l)

    @repeat(0.1)
    def _():
        nonlocal note, count, counter
        pitch_arr = create_array(24, count)
        mrp.set_note_quality(note, 'intensity', 1.0)#counter/count)
        mrp.set_note_quality(note, 'brightness', counter/count)
        mrp.set_note_quality(note, 'harmonic', counter/count)
        mrp.set_note_quality(note, 'pitch', pitch_arr[counter])
        counter+=1
        if counter == count:
            print(f"turning note {note} off.")
            mrp.note_off(note)
            note = random.randint(21, 108)
            mrp.note_on(note)
            counter=0
        print(f"{counter}/{count}, note: {note}, pitch: {pitch_arr[counter]}")
        print(f"note {note} qualities: {mrp.get_note_qualities(note)}")

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
