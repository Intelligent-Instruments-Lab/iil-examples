"""
Draw a sinewave in XY mode inside a rectangle tracking a particle
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    sine = SineOscillator([440,441])
    output = sine * 1.0
    output.play()
    ti_buf = ti.ndarray(dtype=ti.f32, shape=output.output_buffer.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=output.output_buffer.shape[1])

    x = ti.field(ti.f32, shape=())
    x[None] = 100.0
    y = ti.field(ti.f32, shape=())
    y[None] = 100.0
    w,h = 100.0,100.0

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2), 
             points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1),
             x: ti.f32, y: ti.f32, w: ti.f32, h: ti.f32,
             rgba: ti.math.vec4):
        for i in range(buf.shape[1]):
            px = (1 - buf[1,i]) * w + x
            py = (1 - buf[0,i]) * h + y
            points[i] = ti.Vector([px, py])
        tv.px.lines(points, rgba)

    def update(x,y):
        pos = tv.p.field[0].pos
        x[None] = pos.x
        y[None] = pos.y
        # TODO: make this radial from centre
        px = pos.x / tv.x
        py = pos.y / tv.y
        fx = 100 + px * 20
        fy = 100 + py * 20
        sine.frequency = [fx, fy]

    @tv.render
    def _():
        update(x,y)
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        ti_buf.from_numpy(output.output_buffer)
        tv.px.particles(tv.p, tv.s.species())
        draw(ti_buf, points, x[None], y[None], w, h, tv.s.species.field[0].rgba)
        return tv.px

if __name__ == '__main__':
    run(main)
