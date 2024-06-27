import taichi as ti
import numpy as np
from tolvera import Tolvera, run
from tolvera.osc.update import Updater
from tolvera.utils import map_range
from signalflow import *

class Sine(Patch):
    def __init__(self, freq=880, gain=1.0, pan=0.0):
        super().__init__()
        freq = self.add_input("freq", freq)
        gain = self.add_input("gain", gain)
        pan = self.add_input("pan", pan)
        sine = SineOscillator(freq)
        panner = StereoPanner(sine, pan)
        output = panner * gain
        self.set_output(output)
        self.set_auto_free(True)
    def __setattr__(self, name, value):
        self.set_input(name, value)

def main(**kwargs):
    tv = Tolvera(**kwargs)

    config = AudioGraphConfig()
    config.output_buffer_size = kwargs.get('output_buffer_size', 8192)
    graph = AudioGraph(config)
    
    num_sines = tv.pn
    freq, pan, gain = (100, 10000), (-1, 1), (0, 1/num_sines)
    freqs = [np.random.uniform(*freq) for _ in range(num_sines)]
    pans = [np.random.uniform(*pan) for _ in range(num_sines)]
    gains = [np.random.uniform(*gain) for _ in range(num_sines)]
    sines = [Sine(freq, gain, pan) for freq, gain, pan in zip(freqs, gains, pans)]

    tv.iml.flock_p2flock_s = {
        'type': 'fun2fun', 
        'size': (tv.s.flock_p.size, tv.s.flock_s.size), 
        'io': (tv.s.flock_p.to_vec, tv.s.flock_s.from_vec),
        'randomise': True,
    }

    tv.s.oscs_p = {
        'state': {
            'freq': (ti.f32, 100., 10000.),
            'pan':  (ti.f32, -1., 1.),
            'gain': (ti.f32, 0., 1.),
        },
        'shape': tv.pn,
        'randomise': False
    }

    @ti.kernel
    def flock_av(particles: ti.template()):
        n = particles.shape[0]
        for i in range(n):
            if particles[i].active == 0:
                continue
            p1 = particles[i]
            fp = tv.s.flock_p[i]
            c = tv.s.species[p1.species].rgba
            r = ti.Vector([1.,0.,0.,1.])
            g = ti.Vector([0.,1.,0.,1.])
            b = ti.Vector([0.,0.,1.,1.])
            tv.px.line(
                p1.pos.x, p1.pos.y, 
                p1.pos.x + fp.separate.x, 
                p1.pos.y + fp.separate.y, 
                r)
            tv.px.line(
                p1.pos.x, p1.pos.y, 
                p1.pos.x + fp.align.x * 100., 
                p1.pos.y + fp.align.y * 100., 
                c)
            tv.px.line(
                p1.pos.x, p1.pos.y, 
                p1.pos.x + fp.cohere.x, 
                p1.pos.y + fp.cohere.y, 
                b)
            tv.px.circle(
                p1.pos.x, p1.pos.y, 
                fp.nearby,
                c)
            # tv.px.line(
            #     p1.pos.x, p1.pos.y, 
            #     p1.pos.x + p1.vel.x, 
            #     p1.pos.y + p1.vel.y, 
            #     c)
            # sp = tv.s.flock_s.struct()
            # for j in range(n):
            #     if i == j and particles[j].active == 0:
            #         continue
            #     p2 = particles[j]
            #     sp = tv.s.flock_s[p1.species, p2.species]
            # fs = tv.s.flock_s.field[i % tv.sn]
            # tv.s.oscs_p.field[i].freq = 
            # tv.s.oscs_p.field[i].pan = 
            # tv.s.oscs_p.field[i].gain = 

    def _update():
        nonlocal freq, pan, gain, freqs, pans, gains
        p_np = tv.p.field.to_numpy()
        pos = p_np['pos']
        mag = np.sqrt(np.sum(p_np['vel']**2, axis=1))
        pans  = map_range(pos.T[0], 0, tv.x, *pan)
        freqs = map_range(pos.T[0], 0, tv.x, *freq)
        gains = map_range(mag, 0, 1, *gain)
        for i, s in enumerate(sines):
            s.pan = pans[i]
            s.freq = freqs[i]
            s.gain = gains[i]
    _update()
    updater = Updater(_update, 1)

    def play():
        [s.play() for s in sines]
    
    def stop():
        [s.stop() for s in sines]
    
    # play()

    @tv.cleanup
    def _():
        stop()

    @tv.render
    def _():
        # updater()
        tv.px.clear()
        # tv.px.diffuse(0.99)
        # tv.v.attract(tv.p, [tv.x/2, tv.y/2], 1, tv.x)
        flock_av(tv.p.field)
        tv.v.flock(tv.p, 0.1)
        # tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
