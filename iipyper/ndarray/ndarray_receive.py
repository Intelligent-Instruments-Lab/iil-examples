import numpy as np
from iipyper import OSC, repeat, run

def main(osc_host='127.0.0.1', osc_port=8888, client_port=9999):

    osc = OSC(osc_host, osc_port, verbose=True)
    osc.create_client('ndarray_send', osc_host, client_port)

    @osc.ndarray(dformat='bytes')
    def ndarray_bytes(address, ndarray):
        print('bytes', ndarray)

    @osc.ndarray(dformat='json')
    def ndarray_json(address, ndarray):
        print('json', ndarray)

    @osc.args
    def ndarray_args(address, *args):
        print('args (bytes)', args)

    @osc.kwargs(json_keys=['ndarray'])
    def ndarray_kwargs(address, ndarray={}):
        arr = np.array(ndarray)
        print('kwargs (json)', arr)

if __name__ == '__main__':
    run(main)
