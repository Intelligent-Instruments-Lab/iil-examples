"""
This example demonstrates how to use the OSCMap class to map OSC messages to Python functions and vice versa.

When this example is run, a Pd patch is created in the background, and XML and JSON versions are also saved.
When the Pd patch is opened, it will send and receive messages to this iipyper server.
It is possible to output a Max patch instead by altering the command-line arguments.

Example
  $ python oscmap.py

In Tölvera, an OSCMap is instanced at tv.osc.map, and OSC is enabled via the --osc True flag.
Tölvera handles updating the OSCMap in the background, so the user does not need to call the map function manually.

> Note: OSCMap will be refactored and moved back into iipyper, eventually.
"""

from iipyper import OSC, run, repeat
from tolvera.osc import OSCMap

def main(**kwargs):

    host = kwargs.get('host', "127.0.0.1")
    client = kwargs.get('client', "127.0.0.1")
    receive_port = kwargs.get('receive_port', 5001)
    send_port = kwargs.get('send_port', 5000)
    patch_type = kwargs.get('patch_type', "Pd")
    patch_name = kwargs.get('patch_name', "iipyper-oscmap")
    pd_bela = kwargs.get('pd_bela', False) # True will also create a `_main.pd` patch for Bela
    export = kwargs.get('export', True)
    
    '''''''''''''''''''''''''''''''''''''''''''''
    OSC

    First, we create an OSC instance and a client. 
    '''''''''''''''''''''''''''''''''''''''''''''
    osc = OSC(host, receive_port, verbose=True, concurrent=True)
    client_name = "iipyper-example"
    osc.create_client(client_name, client, send_port)
    
    '''
    OSC Map

    Then we create an OSCMap instance:
    - 'export' is None by default and can be 'JSON', 'XML' or True (for both)
    '''
    osc_map = OSCMap(osc, client_name, patch_type, patch_name, pd_bela=pd_bela, export=export)

    '''''''''''''''''''''''''''''''''''''''''''''
    OSC Mapping

    This simple example OSCMap shows one send function and one receive function.
    We add functions to the OSCMap instance using `send_args`, `send_list`, `receive_args` or `receive_list` methods.
    In the `@osc_map.send|receive()` decorator we specify OSC parameters as `name=(default, min, max)`.
    The additional variables `count`, and `send_mode` describe different behaviours:
    - `count` is the number of times the function is called before sending or receiving
    - `send_mode` can be `broadcast` or `event`, describing whether the message is sent continuously, or only when called manually.
    We also use type hints in the method signature for sends and receives, and also return type hints for receives, which should always be a tuple.
    '''''''''''''''''''''''''''''''''''''''''''''

    '''
    Patcher → Python
    '''
    update_rate = 5

    @osc_map.receive_args(arg=(0,0,100), count=update_rate)
    def test_receive_args(arg: float):
        print(f"Receiving args: {arg}")

    @osc_map.receive_list(vector=(0.0,0.0,100.0), length=10, count=update_rate)
    def test_receive_list(vector: list[float]):
        print(f"Receiving list: {vector}")

    '''
    Python → Patcher
    '''
    update_rate = 7
    send_mode = 'broadcast' # | 'event'

    @osc_map.send_args(arg=(0,0,100), count=update_rate, send_mode=send_mode)
    def test_send_arg() -> list[int]:
        arg = 5
        print(f"Sending arg: {arg}")
        return [arg]
    
    @osc_map.send_list(vector=(0.,0.,100.), length=10, count=update_rate, send_mode=send_mode)
    def test_send_list() -> list[float]:
        print(f"Sending list: {[0]*10}")
        return [0]*10

    @repeat(0.125)
    def _():
        osc_map()

if __name__=='__main__':
    run(main)
