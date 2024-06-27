"""
Draws a stereo buffer as an XY Lissajous curve.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()
    wavetable_size = 1024

    square = np.zeros(wavetable_size)
    for n in range(1, 300, 2):
        square += np.sin(np.arange(wavetable_size) * n * np.pi * 2.0 / wavetable_size) / n
    square_buf = Buffer([square])

    saw = np.zeros(wavetable_size)
    for n in range(1, 300):
        saw += np.sin(np.arange(wavetable_size) * n * np.pi * 2.0 / wavetable_size) / n
    saw_buf = Buffer([saw])

    buffer2D = Buffer2D([square_buf, saw_buf])
    frequency = SineLFO(0.1, 60, 61)
    crossfade = SineLFO(0.5)
    wavetable = Wavetable2D(buffer2D, frequency, crossfade) * 0.1
    stereo = StereoPanner(wavetable)

    stereo.play()
    graph.wait()

    sq_ti = ti.ndarray(dtype=ti.f32, shape=square_buf.data.shape)
    saw_ti = ti.ndarray(dtype=ti.f32, shape=saw_buf.data.shape)

    @ti.kernel
    def draw(saw: ti.types.ndarray(dtype=ti.f32, ndim=1), sq: ti.types.ndarray(dtype=ti.f32, ndim=1)):
        sX = tv.x / saw.shape[1]
        sY = tv.y / 2
        for i in ti.ndrange(saw.shape[1], sq.shape[1]):
            x = (1 - buf[1,i]) * sY + tv.x/4
            y = (1 - buf[0,i]) * sY
            tv.px.px.rgba[]

    @tv.render
    def _():
        tv.px.clear()
        ti_buf.from_numpy(player.output_buffer)
        draw(ti_buf, points)
        return tv.px

if __name__ == '__main__':
    run(main)
