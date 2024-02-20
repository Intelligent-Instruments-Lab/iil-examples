"""tv.cv example.

Example:
    $ python tolvera/cv/hands_attract.py --cv True --camera True --device 0 --hands True
"""

import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)    

    @ti.kernel    
    def attract():
        for p in range(tv.pn):
            x, y = tv.s.hands[0, p % 21].px
            tv.p.field[p].vel += tv.v.attract_particle(tv.p.field[p], ti.Vector([x, y]), 1000, tv.x)

    @tv.render
    def _():
        tv.px.set(tv.cv())
        tv.v.plife(tv.p)
        tv.px.diffuse(0.99)
        tv.hands(tv.cv.cc_frame)
        tv.hands.draw_hand(0)
        if tv.hands.handed[0] > -1:
            attract()
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
