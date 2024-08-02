"""
Granulator example using SignalFlow and Tolvera.
Written by Daniel Jones @ideoforms.

Example:
    python granulator.py --y 400 --particles 12 --species 3 --audio_path /path/to/audio.wav
"""

import taichi as ti
import random
from tolvera import Tolvera, run
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)

    #--------------------------------------------------------------------------------
    # Increase the particle rate range
    #--------------------------------------------------------------------------------
    tv.species_consts.MIN_SPEED = 1
    tv.species_consts.MAX_SPEED = 4

    #--------------------------------------------------------------------------------
    # Create the global processing graph
    #--------------------------------------------------------------------------------
    graph = AudioGraph()
    players = []

    #--------------------------------------------------------------------------------
    # Load the buffer to granulate
    #--------------------------------------------------------------------------------
    audio_path = kwargs.get('audio_path', None)
    audio_buf = Buffer(audio_path)

    #--------------------------------------------------------------------------------
    # Create a SignalFlow Granulator node for each particle, with random pan
    # and transposition
    #--------------------------------------------------------------------------------
    for n in range(tv.pn):
        rate = random.choice([1, 1.5, 2, 4])
        player = Granulator(audio_buf,
                            duration=RandomBrownian(0.1, 0.5, 0.001),
                            rate=rate,
                            pan=random_uniform(-1, 1),
                            clock=RandomImpulse(10))
        player_attenuated = player * 0.25
        player_attenuated.play()
        players.append(player)

    #--------------------------------------------------------------------------------
    # Create taichi buffers to pass data to the renderer
    #--------------------------------------------------------------------------------
    ti_buf = ti.ndarray(dtype=ti.f32, shape=audio_buf.data.shape)
    ti_buf.from_numpy(audio_buf.data)
    points = ti.ndarray(dtype=ti.math.vec2, shape=audio_buf.data.shape[1])

    @ti.kernel
    def draw(buf: ti.types.ndarray(dtype=ti.f32, ndim=2),
             points: ti.types.ndarray(dtype=ti.math.vec2, ndim=1),
             cursor_x: ti.types.f32):
        #--------------------------------------------------------------------------------
        # Draw waveform
        #--------------------------------------------------------------------------------
        c = ti.Vector([1.0, 1.0, 1.0, 1.0])
        sX = tv.x / buf.shape[1]
        sY = tv.y / 2
        for i in range(buf.shape[1]):
            x = i * sX
            y = (1 - buf[0,i]) * sY
            points[i] = ti.Vector([x, y])
        tv.px.lines(points, c)
        
        #--------------------------------------------------------------------------------
        # Draw cursor
        #--------------------------------------------------------------------------------
        tv.px.line(cursor_x, 0, cursor_x, tv.y, c)

        #--------------------------------------------------------------------------------
        # Attract particles to the cursor position, and draw the particles
        #--------------------------------------------------------------------------------
        for i in range(tv.pn):
            tv.p.field[i].vel += tv.v.attract_particle(tv.p.field[i],
                                                       ti.Vector([cursor_x,
                                                                  tv.p.field[i].pos.y + (ti.random() * 20 - 10)]),
                                                       500, tv.x)
            colour = tv.s.species[tv.p.field[i].species].rgba
            tv.px.circle(tv.p.field[i].pos.x, tv.p.field[i].pos.y, 5, colour)


    @tv.render
    def _():
        tv.px.clear()

        #--------------------------------------------------------------------------------
        # Update flock
        #--------------------------------------------------------------------------------
        tv.v.flock(tv.p)
        tv.v.noise(tv.p, 1.0)
        tv.px.diffuse(0.9) 
        
        #--------------------------------------------------------------------------------
        # Extract the cursor X position to pass to the taichi kernel
        #--------------------------------------------------------------------------------
        cursor_x_norm, cursor_y_norm = tv.ti.window.get_cursor_pos()
        cursor_x_screen = cursor_x_norm * tv.x

        #--------------------------------------------------------------------------------
        # Trigger draw
        #--------------------------------------------------------------------------------
        draw(ti_buf, points, cursor_x_screen)

        #--------------------------------------------------------------------------------
        # Iterate over each agent in the swarm, and set the read head to the time
        # corresponding to the grain's X coordinate.
        #--------------------------------------------------------------------------------
        for n in range(tv.pn):
            buffer_pos_seconds = audio_buf.duration * (tv.p.field[n].pos.x / tv.x)
            players[n].pos = buffer_pos_seconds

        return tv.px

if __name__ == '__main__':
    run(main)
