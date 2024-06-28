"""
Same as `draw_sinewave.py`, except particle[0]'s X-position 
updates the frequency of the sine wave.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    sine = SineOscillator(440)
    stereo = StereoPanner(sine, 0.0)
    output = sine * 0.5
    output.play()
    ti_buf = ti.ndarray(dtype=ti.f32, shape=output.output_buffer.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=output.output_buffer.shape[1])

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2), points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1)):
        c = ti.Vector([1.0, 1.0, 1.0, 1.0])
        sX = tv.x / buf.shape[1]
        sY = tv.y / 2
        for i in range(buf.shape[1]):
            x = i * sX
            y = (1 - buf[0,i]) * sY
            points[i] = ti.Vector([x, y])
        tv.px.lines(points, c)

    def update():
        sine.frequency = tv.p.field[0].pos[0]

    @tv.render
    def _():
        update()
        tv.px.clear()
        tv.v.move(tv.p, 1)
        ti_buf.from_numpy(output.output_buffer)
        draw(ti_buf, points)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
