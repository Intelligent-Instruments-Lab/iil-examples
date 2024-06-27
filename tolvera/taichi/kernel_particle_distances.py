"""Taichi kernel example for drawing particle distances.
"""

import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @ti.kernel
    def draw_particle_dists(p: ti.template(), s: ti.template(), f: ti.template(), fd: ti.template(), fs: ti.template(), max_radius: ti.f32):
        for i, j in ti.ndrange(tv.p.n,tv.p.n):
            if i==j: continue
            p1 = p[i]
            p2 = p[j]
            if p1.species != p2.species: continue
            sp = s[p1.species]
            alpha = ((p1.vel + p2.vel)/2).norm()
            p1x = ti.cast(p1.pos[0], ti.i32)
            p1y = ti.cast(p1.pos[1], ti.i32)
            p2x = ti.cast(p2.pos[0], ti.i32)
            p2y = ti.cast(p2.pos[1], ti.i32)
            tv.px.circle(p1x, p1y, 2 * alpha, sp.rgba)
            d = fd[i,j].dist 
            r = fs[p1.species,p2.species].radius
            if d > r * max_radius: continue
            # hack, should draw two lines when wrapping occurs
            if ti.abs(p1x - p2x) > tv.x-fs[i,j].radius: continue
            if ti.abs(p1y - p2y) > tv.y-fs[i,j].radius: continue
            tv.px.line(p1x, p1y, p2x, p2y, sp.rgba)

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.p()
        tv.v.flock(tv.p)
        draw_particle_dists(tv.p.field, tv.s.species(), tv.s.flock_p(), tv.s.flock_dist(), tv.s.flock_s(), tv.v.flock.CONSTS.MAX_RADIUS)
        return tv.px

if __name__ == '__main__':
    run(main)
