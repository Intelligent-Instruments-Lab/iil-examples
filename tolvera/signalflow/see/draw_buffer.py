"""
Same as `draw_sinewave.py` but loads an audio file and draws its waveform.
"""

import taichi as ti
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = AudioGraph()

    audio_path = kwargs.get('audio_path', 'signalflow-examples/audio/stereo-count.wav')
    audio_buf = Buffer(audio_path)
    player = BufferPlayer(audio_buf, loop=True)
    graph.play(player)

    ti_buf = ti.ndarray(dtype=ti.f32, shape=audio_buf.data.shape)
    points = ti.ndarray(dtype=ti.math.vec2, shape=audio_buf.data.shape[1])

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

    # We only need to call this once
    ti_buf.from_numpy(audio_buf.data)
    draw(ti_buf, points)

    @tv.render
    def _():
        return tv.px

if __name__ == '__main__':
    run(main)
