"""
Template for a 'verur'-style class that performs 
pair-wise comparison of particles (tv.p).
"""

import taichi as ti
from ..utils import CONSTS

@ti.data_oriented
class VerurTemplate:
    """
    Template for a 'verur'-style class that performs 
    pair-wise comparison of particles (tv.p).
    
    Example:
        tv = Tolvera(**kwargs)
        verur = VerurTemplate(tv, **kwargs)
        @tv.render
        def _():
            verur(tv.p) # Call the behaviour
            return tv.px
    """
    def __init__(self, tolvera, **kwargs):
        """Initialise the behaviour.

        `tmp_s` stores the species rule matrix. 
        `tmp_p` stores the rule values per particle.

        Args:
            tolvera (Tolvera): A Tolvera instance.
            **kwargs: Keyword arguments.
            prop (float, optional): Example property. Defaults to 0.5.
        """
        self.tv = tolvera
        self.kwargs = kwargs
        # Default properties
        self.prop = kwargs.get("prop", 0.5)
        self.CONSTS = CONSTS({"VAL": (ti.f32, 300.0)})
        # Species-species interaction rules
        self.tv.s.tmp_s = {
            "state": {
                "a": (ti.f32, 0.01, 1.0),
                "b": (ti.f32, 0.01, 1.0),
            }, "shape": (self.tv.sn, self.tv.sn),
            "randomise": True,
        }
        # Per-particle state
        self.tv.s.tmp_p = {
            "state": {
                "a": (ti.f32, 0.01, 1.0),
                "b": (ti.f32, 0.01, 1.0),
            }, "shape": self.tv.pn,
            "randomise": False,
        }

    def randomise(self):
        """Randomise the species state."""
        self.tv.s.tmp_s.randomise()

    @ti.kernel
    def step(self, particles: ti.template(), weight: ti.f32):
        """Step the behaviour, pair-wise compare and update particles.

        Args:
            particles (ti.template()): Tölvera particles (tv.p.field).
            weight (ti.f32): The 'weight' (scalar) of the behaviour.
        """
        # Pair-wise comparison of particles
        n = particles.shape[0]
        for i in range(n):
            # Skip inactive particles
            if particles[i].active == 0:
                continue
            p1 = particles[i]
            species = self.tv.s.tmp_s.struct()
            for j in range(n):
                # Skip inactive particles and self-comparison
                if i == j and particles[j].active == 0:
                    continue
                p2 = particles[j]
                # Retrieve species rules for the pair
                species = self.tv.s.tmp_s[p1.species, p2.species]
                """Do something here using species.a|b to affect particles[i]..."""
                # Update tv.p particle state, proportional to weight
                particles[i].vel += (species.a + species.b)/2 * p1.speed * p1.active * weight
                particles[i].pos += particles[i].vel
                # Update VerurTemplate particle state
                self.tv.s.tmp_p[i] = self.tv.s.tmp_p.struct(species.a, species.b)

    def __call__(self, particles, weight: ti.f32 = 1.0):
        """Call the behaviour.

        Args:
            particles (Particles): Particles to step.
            weight (ti.f32, optional): The weight of the behaviour. Defaults to 1.0.
        """
        self.step(particles.field, weight)
