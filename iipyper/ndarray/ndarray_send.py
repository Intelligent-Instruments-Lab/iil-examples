import numpy as np
from iipyper import OSC, repeat, run, ndarray_to_json, ndarray_to_osc_args

def main(osc_host='127.0.0.1', osc_port=9999, client_port=8888):

    osc = OSC(osc_host, osc_port, verbose=True)
    osc.create_client('ndarray_receive', osc_host, client_port)
    arr = None

    @osc.args
    def reset(address, *args):
        nonlocal arr
        shape = (3,3)
        dtype = np.float32
        arr = np.random.rand(*shape).astype(dtype)
        print('reset to:', arr)

    reset('')

    @repeat(1)
    def _():
        nonlocal arr
        osc.send('/ndarray_bytes', arr)

    @repeat(1)
    def _():
        nonlocal arr
        args = ndarray_to_json(arr)
        osc.send('/ndarray_json', 'ndarray', args)

    @repeat(1)
    def _():
        nonlocal arr
        args = ndarray_to_osc_args(arr)
        osc.send('/ndarray_args', *args)

    @repeat(1)
    def _():
        nonlocal arr
        args = ndarray_to_json(arr)
        osc.send('/ndarray_kwargs', 'ndarray', args)


if __name__ == '__main__':
    run(main)
