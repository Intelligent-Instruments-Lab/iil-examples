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
    --host: The host to send OSC messages to. Default is '127.0.0.1'.
    --receive_port: The port to receive OSC messages on. Default is 8888.
    --send_port: The port to send OSC messages to. Default is 7770.
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

    amps = kwargs.get('amps', 0)
    print(f"Testing amplifier(s): {amps}")
    amps = mrp.get_amps_fstlst(amps) if kwargs.get('fstlst', False) else mrp.get_amps(amps)
    print(f"Amplifier notes: {amps}")
    amps_index = 0

    @repeat(kwargs.get('interval', 1))
    def _():
        """
        Loop through the first and last notes
        of amplifier(s), turning them on and off.
        """
        nonlocal amps, amps_index
        
        old_note = amps[amps_index]
        mrp.note_off(old_note)

        new_note = amps[amps_index]
        mrp.note_on(new_note)
        mrp.set_note_quality(new_note, 'intensity', 1)
        
        amps_index += 1
        if amps_index >= len(amps):
            amps_index = 0

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
