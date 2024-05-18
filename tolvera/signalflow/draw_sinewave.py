"""
This example demonstrates how to draw a sine wave using the Tolvera library.
First, we create a sine wave oscillator and play it. We then create a Taichi buffer
to store the output of the sine wave. We also create a Taichi buffer to store the
points of the sine wave. We then define a Taichi kernel to draw the sine wave using
the Taichi buffer. Finally, we define a render function that clears the screen, draws
the sine wave, and returns the Tolvera pixel buffer. We then run the Tolvera application.

We could improve the flexibility of the drawing by allowing the user to specify a rectangle
to draw the sine wave in. We could also allow the user to specify the color of the sine wave.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    sine = SineOscillator(440)
    stereo = StereoPanner(sine, 0.0)
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
            x = i * sX
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
