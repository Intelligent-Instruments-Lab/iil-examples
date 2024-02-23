"""Alternative approach to setting states from a vector.

Using `tv.s.from_vec`

Example
  $ python states_from_vec.py --iml True
"""

import fire
from tolvera import Tolvera

def main(**kwargs):
    tv = Tolvera(**kwargs)

    states = ['species', 'flock_s']
    def states_from_vec(vec:list):
        tv.s.from_vec(states, vec)

    tv.iml.particles_pos2states = {
        'type': 'fun2fun', 
        'size': ((tv.pn, 2), tv.s.get_size(states)), 
        'io': (tv.p.get_pos_all_2d, states_from_vec),
        'randomise': True,
    }

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.p()
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species, 'circle')
        return tv.px

if __name__ == '__main__':
    fire.Fire(main)
