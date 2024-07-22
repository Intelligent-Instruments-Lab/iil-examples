"""Interactive machine learning example

Using the flock model, we map its particle states to its species rules,
creating a feedback loop between them.

The IML 'type' is 'vec2vec' because we are mapping a vector to another vector.

Example
  $ python iml_flock_particles_to_species.py --iml True
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    tv.iml.flock_p2flock_s = {
        'size': (tv.s.flock_p.size, tv.s.flock_s.size), 
        'io': (list, list),
        'randomise': True,
        'config': {'interpolate': 'Ripple'},
        'map_kw': {'k': 10, 'ripple_depth': 5, 'ripple': 5}
    }

    def update():
        invec = tv.s.flock_p.to_vec()
        tv.iml.i = {'flock_p2flock_s': invec}
        flock_s_outvec = tv.iml.o['flock_p2flock_s']
        if flock_s_outvec is not None:
            tv.s.flock_s.from_vec(flock_s_outvec)
    
    @tv.render
    def _():
        update()
        tv.px.diffuse(0.99)
        tv.p()
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species, 'circle')
        return tv.px

if __name__ == '__main__':
    run(main)
