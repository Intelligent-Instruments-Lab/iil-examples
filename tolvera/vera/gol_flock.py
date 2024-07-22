"""
Game of life interacting with flocking particles.

Example:
    python gol_flock.py --particles 64
"""

import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    gx = tv.x/2 - tv.v.gol.px.px.shape[0]/2
    gy = tv.y/2 - tv.v.gol.px.px.shape[1]/2
    gw, gh = tv.v.gol.w, tv.v.gol.h
    gn, gc = tv.v.gol.n, tv.v.gol.cell_size

    @ti.kernel
    def draw(s: ti.template()):
        tv.px.stamp_f(gx, gy, s)

    @ti.kernel
    def cells_to_flock():
        for i, j in tv.s.gol_cells.field:
            cell = tv.s.gol_cells.field[i,j]
            if cell.alive:
                tv.v._attract(tv.p, ti.Vector([i*gc + gx, j*gc + gy]), 1, 100)

    @ti.kernel
    def flock_to_cells():
        for p in tv.p.field:
            p1 = tv.p.field[p]
            x, y = p1.pos.x, p1.pos.y
            if gx <= x < gx + gw and gy <= y < gy + gh:
                i, j = int((x - gx) / gc), int((y - gy) / gc)
                tv.v.gol.fill_area(i, j, 2, 2, 1)

    @tv.render
    def _():
        cells_to_flock()
        flock_to_cells()
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        s = tv.v.gol()
        draw(s)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
