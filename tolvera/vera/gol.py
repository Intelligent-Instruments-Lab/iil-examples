import taichi as ti
from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    tv.v.gol.set_speed(10)

    @ti.kernel
    def draw(s: ti.template()):
        tv.px.stamp(0, 0, s)

    @tv.render
    def _():
        return tv.v.gol()

    # # Alternatively:
    # @tv.render
    # def _():
    #     tv.px.clear()
    #     s = tv.v.gol()
    #     draw(s)
    #     return tv.px

if __name__ == '__main__':
    run(main)
