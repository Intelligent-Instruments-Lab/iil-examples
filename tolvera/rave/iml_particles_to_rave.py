"""Mapping particle positions to RAVE latent space via IML.

RAVE: https://github.com/acids-ircam/RAVE
Models: https://huggingface.co/Intelligent-Instruments-Lab/rave-models

Example:
    $ python iml_particles_to_rave.py --iml True --audio_device [4,5] --rave_path /path/to/rave_model.ts
"""

import numpy as np
import torch
import sounddevice as sd

from iipyper import Audio
from tolvera import Tolvera, run
from tolvera.utils import map_range

def main(**kwargs):
    print(f"Availabe audio devices:\n{sd.query_devices()}")

    tv = Tolvera(**kwargs)
    rave_path = kwargs.get('rave_path', None)
    device = kwargs.get('audio_device', None)
    assert rave_path is not None, "RAVE model path required."
    assert device is not None, f"Audio device required. Availabe devices:\n{sd.query_devices()}"

    rave = torch.jit.load(rave_path)
    
    try:
        sr = rave.sr
    except Exception:
        sr = rave.sampling_rate

    z = torch.zeros(rave.encode_params[2])

    def rave_callback(
            indata: np.ndarray, outdata: np.ndarray,
            frames: int, time, status):
        with torch.inference_mode():
            outdata[:,:] = rave.decode(z[None,:,None])[:,0].T
        
    audio = Audio(
        device=device, dtype=np.float32,
        samplerate=sr, blocksize=rave.encode_params[-1], 
        callback=rave_callback)
    
    tv.iml.particles2rave = {
        'type': 'fun2vec',
        'size': ((tv.pn,2), rave.encode_params[2]),
        'io': (tv.p.get_pos_all_2d, None),
        'randomise': True,
        # 'rand_method': 'uniform',
        # 'rand_kw': {'low': -3, 'high': 3},
        # 'config': {'interpolate': 'Ripple'},
        # 'default_kwargs': {'k': 10, 'ripple_depth': 5, 'ripple': 5}
    }

    # print(tv.iml.particles2rave.pairs)
    # exit()

    def update():
        nonlocal z
        outvec = tv.iml.o['particles2rave']
        if outvec is not None:
            print('outvec',outvec)
            z[:] = torch.from_numpy(outvec)

    audio.stream.start()
    
    @tv.render
    def _():
        update()
        tv.px.diffuse(0.99)
        tv.p()
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species, 'circle')
        return tv.px

if __name__=='__main__':
    run(main)
