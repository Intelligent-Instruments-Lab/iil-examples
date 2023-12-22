import numpy as np
import torch
import sounddevice as sd

from iipyper import Audio, run, Updater
from anguilla import IML
from tolvera import Tolvera

def main(**kwargs):
    assert rave_path is not None, "RAVE model path required."
    assert device is not None, f"Audio device required. Availalbe devices:\n{sd.query_devices()}"
    
    tv = Tolvera(**kwargs)
    rave_path = kwargs.get('rave_path', None)
    device = kwargs.get('device', None)

    rave = torch.jit.load(rave_path)
    
    try:
        sr = rave.sr
    except Exception:
        sr = rave.sampling_rate

    def rave_callback(
            indata: np.ndarray, outdata: np.ndarray,
            frames: int, time, status):
        with torch.inference_mode():
            outdata[:,:] = rave.decode(z[None,:,None])[:,0].T
        
    audio = Audio(
        device=device, dtype=np.float32,
        samplerate=sr, blocksize=rave.encode_params[-1], 
        callback=rave_callback)
    
    # Setup IML
    n = tv.pn
    d_src = (n,2)
    d_tgt = rave.encode_params[2]
    z = torch.zeros(d_tgt)
    ctrl = torch.zeros(d_src)
    z = torch.zeros(d_tgt)
    iml = IML(d_src, emb='ProjectAndSort')
    def iml_add():
        while(len(iml.pairs) < 32):
            src = torch.rand(d_src)
            tgt = z + torch.randn(d_tgt)*2
            iml.add(src, tgt)
    iml_add()
    
    def iml_map():
        ctrl = tv.p.get_pos_all_2d()
        z[:] = torch.from_numpy(iml.map(ctrl, k=5))
    iml_update = Updater(iml_map, 24)

    audio.stream.start()
    
    @tv.render
    def _():
        iml_update()
        tv.px.diffuse(0.99)
        tv.p()
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species, 'circle')
        return tv.px

if __name__=='__main__':
    run(main)
