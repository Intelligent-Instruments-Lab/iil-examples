import numpy as np
import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @ti.kernel    
    def attract():
        for p in range(tv.pn):
            x, y = tv.s.pose[p % 33].px
            tv.p.field[p].vel += tv.v.attract_particle(tv.p.field[p], ti.Vector([x, y]), 1000, tv.x)

    @tv.render
    def _():
        tv.cv()
        tv.cv.px.flip_y()
        tv.v.flock(tv.p)
        tv.px.diffuse(0.99)
        tv.pose(np.flip(tv.cv.cc_frame, axis=1))
        tv.pose.draw()
        if tv.pose.detected[None] == 1:
            attract()
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
