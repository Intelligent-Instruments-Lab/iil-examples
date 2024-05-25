from sardine_core.run import *
import taichi as ti
from tolvera import Tolvera, run

tv = Tolvera(iml=True)

tv.iml.flock_p2flock_s = {
    'type': 'fun2fun', 
    'size': (tv.s.flock_p.size, tv.s.flock_s.size), 
    'io': (tv.s.flock_p.to_vec, tv.s.flock_s.from_vec),
    'randomise': True,
    'update_rate': tv.ti.fps,
}

@ti.kernel
def draw():
    x,y,w,h = 100,100,100,100
    y = tv.y-y-h # flip y
    xgap = w//tv.sn
    ygap = h//tv.sn
    for ix in range(tv.sn):
        xoff = x+ix*xgap
        xc = tv.s.species[ix].rgba
        r = xgap//4
        tv.px.circle(xoff + xgap//2 - r/2, y+h+r, r, xc)
        for iy in range(tv.sn):
            iyi = tv.sn-iy-1 # flip y
            yoff = y+iy*ygap
            yc = tv.s.species[iyi].rgba
            f_sep = tv.s.flock_s.field[ix, iyi].separate
            fc = ti.Vector([f_sep,f_sep,f_sep,1])
            tv.px.rect(xoff, yoff, xgap-5, ygap-5, fc)
            if ix == 0:
                tv.px.circle(xoff-r*2, yoff + ygap//2 -r/2, r, yc)
_draw = draw

# p = list(tv.s.flock_s.dict)[0]
# f_sep = tv.s.flock_s.field[ix, iyi][p]

print(tv.s.flock_s.dict)

tv.s.flock_s.field[0,0]

@swim
def gui_loop(p=0.5, i=0):
    if i % tv.ti.fps*4 == 0:
        tv.s.species.randomise()
    tv.iml()
    tv.px.diffuse(0.99)
    tv.p()
    tv.v.flock(tv.p)
    tv.px.particles(tv.p, tv.s.species())
    draw()
    tv.show(tv.px)
    again(gui_loop, p=1/64, i=i+1)

silence(gui_loop)

# if __name__ == '__main__':
#     run(main)
