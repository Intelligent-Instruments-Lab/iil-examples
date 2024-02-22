"""tolvera/vera/forces.py examples

This module contains functions for applying forces to particles.

Some are @ti.kernel and can run directly inside @tv.render
Some are @ti.func which can only be called from @ti.kernel functions, or other @ti.funcs
"""

import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @ti.kernel
    def ti_funcs():
        # Attract single particle to a position with a mass and radius
        tv.v.attract_particle(tv.p.field[0], [tv.x/2, tv.y/2], 10.0, tv.y)

        # Repel single particle from a position with a mass and radius
        # tv.v.repel_particle(tv.p.field[0], [tv.x/2, tv.y/2], 10.0, tv.y)

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        
        # Update position based on velocity
        tv.v.move(tv.p)
        
        # Attract particles to a position with a mass and radius
        # tv.v.attract(tv.p, [tv.x/2, tv.y/2], 10.0, tv.y)

        # Attract particle species to a position with a mass and radius
        # tv.v.attract_species(tv.p, [tv.x/2, tv.y/2], 10.0, tv.y, 1)

        # Repel particles from a position with a mass and radius
        # tv.v.repel(tv.p, [tv.x/2, tv.y/2], 10.0, tv.y)

        # Repel particle species from a position with a mass and radius
        # tv.v.repel_species(tv.p, [tv.x/2, tv.y/2], 10.0, tv.y, 1)

        # Gravitate particles to a position with force G and radius
        # tv.v.gravitate(tv.p, 10.0, 100.0)

        # Gravitate particle species to a position with force G and radius
        # tv.v.gravitate_species(tv.p, 10.0, 100.0, 0)

        # Add noise to the particles with a weight (scalar)
        # tv.v.noise(tv.p, 1.0)

        # ti_funcs()

        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
