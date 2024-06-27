"""
Authors:
  Victor Shepardson
  Jack Armitage
  Intelligent Instruments Lab 2022
"""

from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def loop():
    print('loop')

def main(host="127.0.0.1", receive_port=8888, send_port=7770):

    osc = OSC(host, receive_port, send_port)
    osc.create_client("mrp", port=send_port)

    mrp = None
    note = 48
    note_on = False
    count=0
    test='code'#'voices', 'qualities'
    qualities=['brightness', 'intensity', 'pitch', 'pitch_vibrato', 'harmonic', 'harmonics_raw']

    @osc.args(return_port=7777)
    def reset(address, kind=None):
        """
        reset the mrp
        """
        print("Resetting MRP...")
        nonlocal mrp
        mrp = MRP(osc)
    
    @repeat(1)
    def _():
        nonlocal note_on, note, count, test
        if note_on == False:
            count+=1
            if test == 'code':
                mrp.note_on(note)
                mrp.set_note_quality(note, 'brightness', 0.5+count/10)
                mrp.set_note_quality(note, 'intensity', 1.9)
                mrp.set_note_quality(note, 'brightness', 1.5, relative=True)
                mrp.set_note_quality(note, 'intensity', 1.9, relative=True)
                mrp.set_note_quality(note, 'harmonics_raw', [1.1, 0.2, 0.3])
                mrp.set_note_quality(note, 'harmonics_raw', [i/10 for i in range(0, count, 1)])
                mrp.set_note_qualities(note, {
                    'brightness': 1.5,
                    'intensity': 1.0,
                    'harmonics_raw': [1.2, 0.3, 0.4]
                })
            elif test == 'voices':
                mrp.note_on(note+count)
                print(len(mrp.voices), 'voices:', mrp.voices)
            elif test == 'qualities':
                mrp.note_on(note)
                mrp.set_note_quality(qualities[0], count/10)
            note_on = True
        else:
            if test == 'code':
                mrp.note_off(note)
            elif test == 'voices':
                if count % 2:
                    mrp.note_off(note+int(count/2))
            note_on = False

    @cleanup
    def _():
        mrp.cleanup()

    reset(None)

if __name__=='__main__':
    run(main)
