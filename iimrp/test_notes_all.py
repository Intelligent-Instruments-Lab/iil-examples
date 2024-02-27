from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):
    osc = OSC(kwargs.get('host', '127.0.0.1'), 
              kwargs.get('receive_port', 8888))
    osc.create_client("mrp", port=kwargs.get('send_port', 7770))
    mrp = MRP(osc, record=kwargs.get('record', False))

    note_on = False
    note = 0

    intensity = kwargs.get('intensity', 1)
    @repeat(kwargs.get('interval', 0.1))
    def _():
        nonlocal note_on, note, intensity
        current = (note % 88) + 21
        if note_on == False:
            mrp.note_on(current, 127)
            mrp.set_note_quality(current, 'intensity', intensity)
            note_on = True
        else:
            mrp.note_off(current)
            note_on = False
            note+=1
        print(current, mrp.voices)

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
