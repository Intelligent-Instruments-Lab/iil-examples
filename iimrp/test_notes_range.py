from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):
    osc = OSC(kwargs.get('host', '127.0.0.1'), 
              kwargs.get('receive_port', 8888))
    osc.create_client("mrp", port=kwargs.get('send_port', 7770))
    mrp = MRP(osc, record=kwargs.get('record', False))

    start = kwargs.get('start', 21)
    end = kwargs.get('end', 108)
    print(f"start: {start}, end: {end}")
    note_on = False
    note = start
    
    @repeat(kwargs.get('interval', 0.1))
    def _():
        nonlocal note_on, note, start, end
        if note_on == False:
            mrp.note_on(note, 127)
            mrp.set_note_quality(note, 'intensity', 1)
            note_on = True
        else:
            mrp.note_off(note)
            note_on = False
            note+=1
        if note > end:
            note = start
        print(note, mrp.voices)

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
