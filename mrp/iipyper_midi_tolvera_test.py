from iimrp import MRP
from iipyper import OSC, MIDI, run, cleanup
import tolvera as tol

def main(midi_in='To iipyper 1', osc_host='127.0.0.1', osc_port=9999, mrp_send_port=7770):

    # TODO: CC mapping
    '''
    cc_mapping={
        0: 'brightness',
        1: 'intensity',
        2: 'pitch',
        3: 'pitch_vibrato',
        4: 'harmonic',
        5: 'harmonics_raw', # 5-21
    }
    print(f"MRP Qualities MIDI CC Mapping: \n\n{cc_mapping}\n\n")
    '''

    midi = MIDI(in_ports=midi_in)
    midi.print_ports()
    osc = OSC(osc_host, osc_port)
    osc.create_client('mrp', port=mrp_send_port)

    mrp = None
    notes_on = set()

    @osc.args(return_port=7770)
    def reset(address, kind=None):
        print("Resetting MRP...")
        nonlocal mrp, osc
        mrp = MRP(osc)

    @midi.handle(type='note_on', note=range(1,128), channel=0)
    def _(msg):
        notes_on.add(msg.note)
        print(f"notes_on: {notes_on}. new note_on: {msg}")
        mrp.note_on(msg.note, msg.velocity)

    @midi.handle(type='note_off', note=range(1,128), channel=0)
    def _(msg):
        notes_on.remove(msg.note)
        print(f"notes_on: {notes_on}. new note_off: {msg}")
        mrp.note_off(msg.note)

    @midi.handle(type='control_change', control=0)
    def _(msg):
        print(f"cc: {msg}")#, mapping: {cc_mapping[msg.control]}")
        # mrp.quality_update(notes_on, cc_mapping[msg.control], msg.value/127)

    tol.init()
    particles = tol.Particles(1920, 1080, 64, 5, 120, False)
    pixels = tol.Pixels(1920, 1080, 64, 5, 120, False)
    def _():
        pixels.clear()
        particles(pixels)

    reset(None)
    tol.utils.render(_, pixels)

    # FIXME: Cleanup does not run when using tol.utils.render
    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
