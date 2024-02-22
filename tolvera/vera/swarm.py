import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @ti.kernel
    def draw_swarm_particles(particles: ti.template()):
        """Draw swarm particles, colour=phase"""
        for i in range(tv.p.n):
            p = particles.field[i]
            ps = tv.s.swarm_p[i]
            if p.active == 0.0: continue
            px = ti.cast(p.pos[0], ti.i32)
            py = ti.cast(p.pos[1], ti.i32)
            rgba = color_map_1d(ps.color, .1, .3, .7) * tv.px.CONSTS.BRIGHTNESS
            tv.px.circle(px, py, 3, rgba)

    @ti.func
    def color_map_1d(val, r=0., g=0., b=0.):
        """Weighted colormap"""
        val = 1 - val
        r = ti.max(.2, 1 - ti.abs(val - r))
        g = ti.max(.2, 1 - ti.abs(val - g))
        b = ti.max(.2, 1 - ti.abs(val - b))
        return ti.Vector([r, g, b, 1])

    @tv.render
    def _():
        p = 11
        tv.px.diffuse(0.99)
        tv.v.swarm(tv.p, p)
        draw_swarm_particles(tv.p)
        return tv.px

if __name__ == '__main__':
    run(main)
