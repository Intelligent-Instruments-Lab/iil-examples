from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.render
    def _():
        tv.v.flock(tv.p)
        return tv.v.slime(tv.p, tv.s.species())

if __name__ == '__main__':
    run(main)
