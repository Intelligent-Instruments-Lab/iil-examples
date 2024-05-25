"""
Trigger a Buffer when any particle crosses the center of the screen.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()

    audio_path = kwargs.get('audio_path', 'signalflow-examples/audio/stereo-count.wav')
    audio_buf = Buffer(audio_path)
    player = BufferPlayer(audio_buf, end_time=audio_buf.duration/16)
    player.play()

    tv.s.triggers = {
        'state': {
            't': (ti.i32, 0, 1)
        }, 'shape': tv.pn
    }

    @ti.kernel
    def check_trigger():
        tv.px.line(tv.x/2, 0, tv.x/2, tv.y, ti.Vector([1, 1, 1, 1]))
        for i in range(tv.pn):
            p = tv.p.field[i]
            px = p.pos.x
            ppx = p.ppos.x
            t = 0
            if px > tv.x/2 and ppx < tv.x/2 and ppx > 0:
                t = 1
            if px < tv.x/2 and ppx > tv.x/2 and ppx < tv.x:
                t = 1
            tv.s.triggers[i].t = t
            if t == 1:
                c = tv.s.species[p.species].rgba
                tv.px.circle(px, p.pos.y, 20, c)
            tv.p.field[i].ppos = px

    def update():
        for i in range(tv.pn):
            if tv.s.triggers.field[i].t == 1:
                player.trigger()
                tv.s.triggers.field[i].t = 0
                p1 = tv.p.field[i]

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p, 1)
        tv.v.centripetal(tv.p, ti.Vector([tv.x/2,tv.y/2]), 0, 5)
        tv.px.particles(tv.p, tv.s.species())
        check_trigger()
        update()
        return tv.px

if __name__ == '__main__':
    run(main)
