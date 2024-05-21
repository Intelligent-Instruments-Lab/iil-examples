import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

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
                p1.pos.x + fp.align.x * 100., # bug
                p1.pos.y + fp.align.y * 100., # bug
                g)
            tv.px.line(
                p1.pos.x, p1.pos.y, 
                p1.pos.x + fp.cohere.x, 
                p1.pos.y + fp.cohere.y, 
                b)
            tv.px.circle(
                p1.pos.x, p1.pos.y, 
                fp.nearby,
                c)

    @tv.render
    def _():
        tv.px.clear()
        flock_av(tv.p.field)
        tv.v.flock(tv.p, 1)
        return tv.px

if __name__ == '__main__':
    run(main)
