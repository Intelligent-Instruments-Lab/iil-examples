from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP
import random

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
    
    @repeat(0.1)
    def _():
        nonlocal note, count, counter
        mrp.set_note_quality(note, 'intensity', 1)
        mrp.set_note_quality(note, 'harmonics_raw', [counter/count, 0., 0., 0., 0., 0., 0., 0.])
        counter+=1
        if counter == count:
            mrp.note_off(note)
            note+=random.randint(-24, 24)
            mrp.note_on(note)
            counter=0
        # print(counter, count, counter/count)

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
