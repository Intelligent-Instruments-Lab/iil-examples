"""Some vera have an additional 'weight' parameter.

This parameter will scale the behaviour to give additional control."""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p, 0.5)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
