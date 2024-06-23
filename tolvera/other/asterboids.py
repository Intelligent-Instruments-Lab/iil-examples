"""Asteroids but with boids.

Left stick: move.
Right stick: rotate.
X: shoot.
"""

import taichi as ti
from tolvera import Tolvera, run
from tolvera.dualsense import DualSense
from tolvera.utils import map_range

@ti.dataclass
class Bullet:
    pos: ti.math.vec2
    vel: ti.math.vec2
    active: ti.i32

def main(**kwargs):
    tv = Tolvera(**kwargs)

    pos = ti.math.vec2(tv.x//2, tv.y//2)
    vel = ti.math.vec2(0,0)
    ang = ti.field(ti.f32, ())

    bullets = Bullet.field(shape=100)

    ds = DualSense()
    ds.start()

    @ds.handle('left_stick')
    def _(ls):
        nonlocal vel
        vel += ti.Vector([map_range(ls.x, 0, 255, -1, 1), map_range(ls.y, 255, 0, -1, 1)])

    @ds.handle('right_stick')
    def _(rs):
        nonlocal ang
        xy = ti.Vector([map_range(rs.x, 0, 255, -1, 1), map_range(rs.y, 255, 0, -1, 1)])
        if xy.norm() > 0.5:
            ang[None] = ti.atan2(xy.y, xy.x)

    @ti.kernel
    def shoot(bullets: ti.template(), pos: ti.math.vec2, ang: ti.f32):
        break_ = 0
        for i in range(bullets.shape[0]):
            if bullets[i].active == 0 and break_ == 0:
                bullets[i].pos = pos
                bullets[i].vel = ti.Vector([ti.cos(ang), ti.sin(ang)]) * 5
                bullets[i].active = 1
                break_ = 1

    @ti.kernel
    def update_bullets():
        for i in range(bullets.shape[0]):
            if bullets[i].active == 1:
                bullets[i].pos += bullets[i].vel
                if bullets[i].pos.x < 0 or bullets[i].pos.x > tv.x or bullets[i].pos.y < 0 or bullets[i].pos.y > tv.y:
                    bullets[i].active = 0
                tv.px.circle(bullets[i].pos.x, bullets[i].pos.y, 4., ti.Vector([1.,1.,1.,1.]))

    @ds.handle('btn_l1')
    def _(pressed):
        tv.p.randomise()
        tv.s.flock_s.randomise()
        tv.s.species.randomise()

    @ds.handle('btn_r1')
    def _(pressed):
        if pressed:
            shoot(bullets, pos, ang[None])

    @tv.cleanup
    def _():
        ds.stop()

    @ti.kernel
    def update(pos: ti.math.vec2, ang: ti.f32):
        size = 15.
        offset = size/4.
        v1 = ti.Vector([pos.x + size * ti.cos(ang), pos.y + size * ti.sin(ang)])
        v2 = ti.Vector([pos.x + size * ti.cos(ang + offset), pos.y + size * ti.sin(ang + offset)])
        v3 = ti.Vector([pos.x + size * ti.cos(ang - offset), pos.y + size * ti.sin(ang - offset)])
        tv.px.triangle(v1, v2, v3, ti.Vector([1.,1.,1.,1.]))

    @ti.kernel
    def move(pos: ti.math.vec2, vel: ti.math.vec2) -> ti.math.vec2:
        return pos + vel * 0.5
    
    @ti.kernel
    def decay(vel: ti.math.vec2) -> ti.math.vec2:
        return vel * 0.99

    @ti.kernel
    def wrap(pos: ti.math.vec2) -> ti.math.vec2:
        p = ti.Vector([0.,0.])
        p = pos
        if p.x < 0: p.x = tv.x
        if p.x > tv.x: p.x = 0
        if p.y < 0: p.y = tv.y
        if p.y > tv.y: p.y = 0
        return p

    @ti.kernel
    def collisions(pos: ti.math.vec2):
        # bullets collide with particles
        for i in range(bullets.shape[0]):
            if bullets[i].active == 1:
                for j in range(tv.pn):
                    if (bullets[i].pos - tv.p.field[j].pos).norm() < 10:
                        bullets[i].active = 0
                        tv.p.field.vel[j] = ti.Vector([0.,0.])
                        tv.p.field[j].active = 0.
        # # bullets collide with each other
        # for i in range(bullets.shape[0]):
        #     if bullets[i].active == 1:
        #         for j in range(bullets.shape[0]):
        #             if bullets[j].active == 1:
        #                 if i != j and (bullets[i].pos - bullets[j].pos).norm() < 10:
        #                     bullets[i].active = 0
        #                     bullets[j].active = 0
        # bullets collide with player
        # for i in range(bullets.shape[0]):
        #     if bullets[i].active == 1:
        #         if (bullets[i].pos - pos).norm() < 10:
        #             bullets[i].active = 0
        # # player collides with particles
        # for i in range(tv.pn):
        #     if (pos - tv.p.field[i]).norm() < 10:
        #         tv.p.field.vel[i] = ti.Vector([0.,0.])

    @tv.render
    def _():
        nonlocal bullets, pos, vel, ang
        tv.px.clear()
        pos = move(pos, vel)
        vel = decay(vel)
        pos = wrap(pos)
        update(pos, ang[None])
        update_bullets()
        collisions(pos)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)

