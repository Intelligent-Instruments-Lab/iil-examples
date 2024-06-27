import taichi as ti
from tolvera import Tolvera, run
from tolvera.dualsense import DualSense
from tolvera.utils import map_range

def main(**kwargs):
    tv = Tolvera(**kwargs)

    ds = DualSense(**kwargs)
    ds.start()

    left_joystick = [0,0]

    @ds.handle('left_stick')
    def _(left_stick):
        nonlocal left_joystick
        left_joystick = [left_stick.x, left_stick.y]

    @tv.cleanup
    def _():
        ds.stop()

    @tv.render
    def _():
        nonlocal left_joystick
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        x = map_range(left_joystick[0], 0, 255, 0, tv.x)
        y = map_range(left_joystick[1], 255, 0, 0, tv.y)
        tv.v.attract(tv.p, ti.Vector([x, y]), 10, tv.x)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
