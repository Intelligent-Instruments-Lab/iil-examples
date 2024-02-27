help_message = """
When wiring up the MRP magnets to the amplifiers,
it's easy to make mistakes.

Start by wiring up the first and last magnets on each amplifier,
and then run this script to check that the magnets are working correctly.

Command-line arguments:
    --help: print this message and exit.
    --amps: Amplifier index(es), as int or list. Default is 0.
    --fstlst: Test the first and last magnets of each amplifier only. Default is False.
    --interval: The interval in seconds between each note change. Default is 1.
    --print: Print the notes of the amplifier(s) and exit.
    --host: The host to send OSC messages to. Default is '127.0.0.1'.
    --receive_port: The port to receive OSC messages on. Default is 8888.
    --send_port: The port to send OSC messages to. Default is 7770.
"""

from iipyper import OSC, run, repeat, cleanup
from iimrp import MRP

def main(**kwargs):
    osc = OSC(kwargs.get('host', '127.0.0.1'), 
              kwargs.get('receive_port', 8888))
    osc.create_client("mrp", port=kwargs.get('send_port', 7770))
    mrp = MRP(osc, record=kwargs.get('record', False))

    if kwargs.get('help', False):
        print(help_message)
        exit()

    amps = kwargs.get('amps', 0)
    print(f"Testing amplifier(s): {amps}")
    amps = mrp.get_amps_fstlst(amps) if kwargs.get('fstlst', False) else mrp.get_amps(amps)
    print(f"Amplifier notes: {amps}")
    if kwargs.get('print', False):
        exit()
    amps_index = 0

    intensity = kwargs.get('intensity', 1)
    @repeat(kwargs.get('interval', 1))
    def _():
        """
        Loop through the amplifier(s) notes
        """
        nonlocal amps, amps_index, intensity
        
        old_note = amps[amps_index - 1 if amps_index > 0 else len(amps) - 1]
        mrp.note_off(old_note)

        new_note = amps[amps_index]
        mrp.note_on(new_note)
        mrp.set_note_quality(new_note, 'intensity', intensity)
        
        amps_index += 1
        if amps_index >= len(amps):
            amps_index = 0

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
