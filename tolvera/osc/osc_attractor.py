from tolvera import Tolvera, run
import taichi as ti

def main(**kwargs):
    tv = Tolvera(**kwargs)
    attract = {'i': 0, 'm': 10, 'r': tv.y}

    @tv.osc.map.receive_args(i=(0,0,len(attract)-1), m=(1,-30,30), r=(tv.y,0,tv.x), count=5)
    def attractor_params(i: int, m: float, r: float):
        nonlocal attract
        attract['m'], attract['r'] = m, r
        print(f"[Attractor] mass: {m} radius: {r}")

    # Create an integer Taichi object to keep track of the count - to maintain similar functionality as return [tv.s.flock_p[0].nearby]
    nearby_count =  ti.field(ti.i32, shape=1) 

    # A function to update_count within taichi scope, to avoid "Taichi functions cannot be called from python scope" error.
    @ti.kernel
    def update_nearby_count():
        nearby_count[0] = tv.s.flock_p[0].nearby
    
    @tv.osc.map.send_args(p0=(0,0,tv.pn), count=5, send_mode='broadcast')
    def attractor_nearby() -> list[int]:
        # Work around to avoid taichi-scope error
        update_nearby_count()  
        return [nearby_count[0]] 

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
