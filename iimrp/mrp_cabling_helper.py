help_message = """
When wiring up the MRP magnets to the amplifiers,
it's easy to make mistakes.

Start by wiring up the first and last magnets on each amplifier,
and then run this script to check that the magnets are working correctly.

Command-line arguments:
    --host: The host to send OSC messages to. Default is '127.0.0.1'.
    --receive_port: The port to receive OSC messages on. Default is 8888.
    --send_port: The port to send OSC messages to. Default is 7770.
    --interval: The interval in seconds between each note change. Default is 1.
    --print: Print the note names and midi note numbers and then exit.
    --help: print this message and exit.
"""

from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):

    if kwargs.get('help', False):
        print(help_message)
        exit()

    host = kwargs.get('host', '127.0.0.1')
    receive_port = kwargs.get('receive_port', 8888)
    send_port = kwargs.get('send_port', 7770)

    osc = OSC(host, receive_port, send_port)
    osc.create_client("mrp", port=send_port)

    mrp = None

    @osc.args(return_port=7777)
    def reset(address, kind=None):
        """
        reset the mrp
        """
        nonlocal mrp
        print("Resetting MRP...")
        mrp = MRP(osc)

    reset(None)

    # Generate a list of notes for the amplifiers
    npa = 18 # notes per amplifier
    amp_rows = 6
    A0 = 21
    gen_amp_notes = lambda n: [
        A0 + npa * (i//2) if i % 2 == 0 else
        A0 + npa * (i//2) + npa-1
        for i in range(n)]
    amp_notes = gen_amp_notes(amp_rows*2)
    print(f"Amplifier notes: {dict(zip(mrp.midi_notes_to_note_names(amp_notes), amp_notes))}")
    amp_notes_index = 0
    note = 0

    kwargs.get('print', False)
    if print:
        exit()
    
    @repeat(kwargs.get('interval', 1))
    def _():
        """
        Loop through the first and last notes
        of each amplifier, turning them on and off.
        """
        nonlocal note, amp_notes, amp_notes_index
        mrp.note_off(note)
        note = amp_notes[amp_notes_index]
        mrp.note_on(note)
        mrp.set_note_quality(note, 'intensity', 1)
        amp_notes_index += 1
        if amp_notes_index >= len(amp_notes):
            amp_notes_index = 0

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
