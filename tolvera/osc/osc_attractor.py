from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)
    attract = {'i': 0, 'm': 10, 'r': tv.y}

    @tv.osc.map.receive_args(i=(0,0,len(attract)-1), m=(1,-30,30), r=(tv.y,0,tv.x), count=5)
    def attractor_params(i: int, m: float, r: float):
        nonlocal attract
        attract['m'], attract['r'] = m, r
        print(f"[Attractor] mass: {m} radius: {r}")
    
    @tv.osc.map.send_args(p0=(0,0,tv.pn), count=5, send_mode='broadcast')
    def attractor_nearby() -> list[int]:
        return [tv.s.flock_p[0].nearby]

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        pos = tv.p.field[attract['i']].pos
        tv.v.attract(tv.p, pos, attract['m'], attract['r'])
        tv.px.particles(tv.p, tv.s.species, 'circle')
        return tv.px

if __name__ == '__main__':
    run(main)
