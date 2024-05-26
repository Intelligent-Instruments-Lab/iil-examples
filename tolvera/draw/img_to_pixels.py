import taichi as ti
import numpy as np
from tolvera import Tolvera, run
from tolvera.pixels import Pixels

def main(**kwargs):
    tv = Tolvera(**kwargs)

    path = 'image.png'

    img_px = Pixels(tv)
    img_px.from_img(path)
    # tv.px.set(img_px) # alternative to blending

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        tv.px.blend_mix(img_px, 0.5)
        return tv.px

if __name__ == '__main__':
    run(main)
