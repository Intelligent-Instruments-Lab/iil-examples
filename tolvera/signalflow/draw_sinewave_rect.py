"""
Draw a sinewave inside a rectangle
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    sine = SineOscillator(440)
    stereo = StereoPanner(sine, 0.0)
    output = stereo * 1
    output.play()
    ti_buf = ti.ndarray(dtype=ti.f32, shape=output.output_buffer.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=output.output_buffer.shape[1])

    x,y,w,h = 100,100,200,400

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2), 
             points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1),
             x: ti.f32, y: ti.f32, w: ti.f32, h: ti.f32):
        c = ti.Vector([1.0, 1.0, 1.0, 1.0])
        sX = w / buf.shape[1]
        sY = h / 2
        for i in range(buf.shape[1]):
            px = i * sX + x
            py = (1 - buf[0,i]) * sY + y
            points[i] = ti.Vector([px, py])
        tv.px.lines(points, c)

    @tv.render
    def _():
        tv.px.clear()
        ti_buf.from_numpy(output.output_buffer)
        draw(ti_buf, points, x,y,w,h)
        return tv.px

if __name__ == '__main__':
    run(main)
