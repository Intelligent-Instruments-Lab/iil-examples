"""
Visualise species matrix for flock separation parameter
as a grid of rectangles, with the colour of each rectangle
representing the separation force of the corresponding
species pair.

Possible additions:
- Grids for every parameter of flock or any model (how to deal with param string names?)
- Textual and numerical labels for each grid axis and cell
- Separate Pixels objects so grids don't have to diffuse
"""

import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    tv.iml.flock_p2flock_s = {
        'type': 'fun2fun', 
        'size': (tv.s.flock_p.size, tv.s.flock_s.size), 
        'io': (tv.s.flock_p.to_vec, tv.s.flock_s.from_vec),
        'randomise': True,
        'update_rate': tv.ti.fps,
    }

    @ti.kernel
    def draw(x: ti.i32, y: ti.i32, param: ti.template()):
        w,h = 75,75
        _y = tv.y-y-h # flip y
        xgap = w//tv.sn
        ygap = h//tv.sn
        for ix in range(tv.sn):
            xoff = x+ix*xgap
            xc = tv.s.species[ix].rgba
            r = xgap//4
            tv.px.circle(xoff + xgap//2 - r/2, _y+h+r, r, xc)
            for iy in range(tv.sn):
                iyi = tv.sn - iy - 1 # flip y
                yoff = _y + iy * ygap
                yc = tv.s.species[iyi].rgba
                f_sep = tv.s.flock_s.field[ix, iyi][param]
                fc = ti.Vector([f_sep, f_sep, f_sep, 1])
                tv.px.rect(xoff, yoff, xgap-5, ygap-5, fc)
                if ix == 0:
                    tv.px.circle(xoff-r*2, yoff + ygap//2 -r/2, r, yc)
    
    @tv.render
    def _():
        if tv.ctx.i[None] % (tv.ti.fps*10) == 0:
            tv.s.species.randomise()
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species)
        draw(100,100,'separate')
        draw(200,100,'cohere')
        draw(300,100,'align')
        draw(400,100,'radius')
        return tv.px

if __name__ == '__main__':
    run(main)
