"""tv.cv example.

Example:
    $ python tolvera/cv/slime_camera.py --cv True --camera True --device 0
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.render
    def _():
        tv.v.slime(tv.p, tv.s.species())
        tv.px.set(tv.v.slime.trail)
        tv.px.blend_max(tv.cv.px)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
