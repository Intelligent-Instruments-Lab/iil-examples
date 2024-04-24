"""tv.cv example.

Example:
    $ python tolvera/cv/slime_camera_iml.py --cv True --camera True --device 0 --iml True
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    if kwargs.get('iml', False):
        tv.iml.slime_p2slime_s = {
            'type': 'fun2fun', 
            'size': (tv.s.slime_p.size, tv.s.slime_s.size), 
            'io': (tv.s.slime_p.to_vec, tv.s.slime_s.from_vec),
            'randomise': True,
        }

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.slime(tv.p, tv.s.species())
        # tv.px.set(tv.v.slime.trail)
        # tv.px.blend_max(tv.cv.px)
        tv.v.slime.trail.blend_max(tv.cv.px)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
