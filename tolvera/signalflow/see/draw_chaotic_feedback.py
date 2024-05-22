"""
Draws the stereo signal from SignalFlow `chaotic-feedback-example.py` example.
The left half of the screen shows the left channel and the right half shows the right channel.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    
    f0 = RandomExponential(40, 2000, clock=RandomImpulse(1))
    buf = Buffer(1, graph.sample_rate)
    feedback = FeedbackBufferReader(buf)
    op0 = SineOscillator(f0 + f0 * feedback * 14)
    level = Smooth(RandomUniform(0, 1, clock=RandomImpulse([0.5, 0.5])))
    level = ScaleLinExp(level, 0, 1, 0.0001, 1.0)
    op0 = op0 * level
    graph.add_node(FeedbackBufferWriter(buf, op0, 0.5))
    op1 = SineOscillator(f0 + f0 * op0 * 14)
    graph.play(op1)

    ti_buf = ti.ndarray(dtype=ti.f32, shape=op1.output_buffer.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=op1.output_buffer.shape[1])

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2), points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1)):
        c = ti.Vector([1.0, 1.0, 1.0, 1.0])
        sX = tv.x / 2 / buf.shape[1]
        sY = tv.y / 2
        for i in range(buf.shape[1]):
            x = i * sX
            y = (1 - buf[0,i]) * sY
            points[i] = ti.Vector([x, y])
        tv.px.lines(points, c)
        for i in range(buf.shape[1]):
            x = i * sX + tv.x / 2
            y = (1 - buf[1,i]) * sY
            points[i] = ti.Vector([x, y])
        tv.px.lines(points, c)

    @tv.render
    def _():
        tv.px.clear()
        ti_buf.from_numpy(op1.output_buffer)
        draw(ti_buf, points)
        return tv.px

if __name__ == '__main__':
    run(main)
