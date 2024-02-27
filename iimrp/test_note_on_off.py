from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):
    osc = OSC(kwargs.get('host', '127.0.0.1'), 
              kwargs.get('receive_port', 8888))
    osc.create_client("mrp", port=kwargs.get('send_port', 7770))
    mrp = MRP(osc, record=kwargs.get('record', False))

    note = kwargs.get('note', 60)
    note_on = False
    
    @repeat(1)
    def _():
        nonlocal note_on, note
        if note_on == False:
            mrp.note_on(note)
            mrp.note_on(note+3)
            mrp.set_note_quality(note, 'intensity', 1)
            mrp.set_note_quality(note+3, 'intensity', 1)
            note_on = True
        else:
            mrp.note_off(note)
            mrp.note_off(note+3)
            note_on = False

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
