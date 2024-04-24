from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    tv.iml.flock_p2flock_s = {
        'type': 'osc2fun', 
        'size': (4, tv.s.flock_s.size), 
        'io': ('tolvera/flock/iml', tv.s.flock_s.from_vec),
        'randomise': True,
    }

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
