import signalflow as sf
from tolvera import Tolvera, run
def main(**kwargs):
    tv = Tolvera(**kwargs)
    graph = sf.AudioGraph()
    sine = sf.SineOscillator(440)
    stereo = sf.StereoPanner(sine, 0.0)
    output = sine * 0.1
    output.play()
    def update():
        pos = tv.p.field[0].pos
        f = 100+(pos[0]*(1000-100))/tv.x
        sine.frequency = f
        print(f"Frequency: {f}")
    @tv.render
    def _():
        update()
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px
if __name__ == '__main__':
    run(main)