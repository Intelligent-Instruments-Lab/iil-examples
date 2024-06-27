"""
Control a species-species interaction over OSC.

Example:
    python osc_flock.py --osc True --create_patch True
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.osc.map.receive_args(
        a=(0,0,tv.sn), b=(0,0,tv.sn), 
        separate=(0.5,0,1), align=(0.5,0,1), cohere=(0.5,0,1), radius=(.1,0,1),  
        count=10)
    def flock(a: int, b: int, separate: float, align: float, cohere: float, radius: float):
        tv.s.flock_s.field[a, b].separate = separate
        tv.s.flock_s.field[a, b].align = align
        tv.s.flock_s.field[a, b].cohere = cohere
        tv.s.flock_s.field[a, b].radius = radius

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
