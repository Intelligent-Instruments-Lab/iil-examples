"""
Authors:
  Victor Shepardson
  Jack Armitage
  Intelligent Instruments Lab 2022
"""

from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):

    host = kwargs.get('host', '127.0.0.1')
    receive_port = kwargs.get('receive_port', 8888)
    send_port = kwargs.get('send_port', 7770)
    note = kwargs.get('note', 60)

    osc = OSC(host, receive_port, send_port)
    osc.create_client("mrp", port=send_port)

    mrp = None
    note_on = False

    @osc.args(return_port=7777)
    def reset(address, kind=None):
        """
        reset the mrp
        """
        print("Resetting MRP...")
        nonlocal mrp
        mrp = MRP(osc)

    reset(None)
    
    @repeat(1)
    def _():
        nonlocal note_on, note
        if note_on == False:
            mrp.note_on(note)
            mrp.set_note_quality(note, 'intensity', 1)
            note_on = True
        else:
            mrp.note_off(note)
            note_on = False

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
