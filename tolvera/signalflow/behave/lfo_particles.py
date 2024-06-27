"""
Modulate particle movement with an LFO.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)

    graph = AudioGraph()
    lfo = SineLFO(0.5, 0, 10)
    lfo.play()

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.move(tv.p, lfo.output_buffer[0][0])
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
