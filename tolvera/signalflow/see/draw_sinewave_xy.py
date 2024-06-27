"""
Draws a stereo sine wave as an XY Lissajous curve.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    sine = SineOscillator([440,441])
    output = sine * 1
    output.play()
    ti_buf = ti.ndarray(dtype=ti.f32, shape=output.output_buffer.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=output.output_buffer.shape[1])

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2), points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1)):
        c = ti.Vector([1.0, 1.0, 1.0, 1.0])
        sX = tv.x / buf.shape[1]
        sY = tv.y / 2
        for i in range(buf.shape[1]):
            x = (1 - buf[1,i]) * sY + tv.x/4
            y = (1 - buf[0,i]) * sY
            points[i] = ti.Vector([x, y])
        tv.px.lines(points, c)

    @tv.render
    def _():
        tv.px.clear()
        ti_buf.from_numpy(output.output_buffer)
        draw(ti_buf, points)
        return tv.px

if __name__ == '__main__':
    run(main)
