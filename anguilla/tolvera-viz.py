"""
runs with https://github.com/Intelligent-Instruments-Lab/tolvera/commit/9623740e9c879ca805a5470cc5563b26c8b7a409

requires taichi v1.7.0 for ArgPack
"""

import fire
import taichi as ti
import numpy as np
from tolvera import Tolvera
from tolvera.pixels import Pixels

def main(**kwargs):

    w, h, d = 120, 67, 4
    shape = (2, 1)

    tv = Tolvera(**kwargs)

    rect_w = tv.x // w 
    rect_h = tv.y // h 

    tv.iml.test2test = {
        'type': 'vec2vec',
        'size': shape, 
        'randomise': True,
        'rand_method': 'uniform',
        'rand_kwargs': {'low': -d/2, 'high': d/2},
        'config': {'interp': 'Ripple'},
        'default_kwargs': {'k': 10, 'ripple_depth': 5, 'ripple': 5}
    }

    def iml_create_map(iml, w, h, domain=4, **kw) -> np.ndarray:
        l = domain
        x_c = np.linspace(-l, l, w)
        y_c = np.linspace(-l, l, h)
        r = np.empty((w, h)).astype(np.float32)
        for i, x in enumerate(x_c):
            for j, y in enumerate(y_c):
                invec = [x,y]
                outvec = iml.map(invec, **iml.default_kwargs, **kw)[0]
                print(f"{i},{j}: {invec} → {outvec}")
                r[i, j] = outvec
        return r

    iml_map_tmpl = ti.types.argpack(iml_map=ti.types.ndarray())
    iml_map_np = iml_create_map(tv.iml.test2test, w, h, d)
    iml_map_ti = ti.ndarray(dtype=ti.f32, shape=(w, h))
    iml_map_ti.from_numpy(iml_map_np)
    iml_map_pack = iml_map_tmpl(iml_map=iml_map_ti)

    iml_src_tmpl = ti.types.argpack(iml_src=ti.types.ndarray())
    iml_pairs_tc = tv.iml.test2test.pairs.values()
    iml_src_tc = np.array([p[0] for p in iml_pairs_tc]).astype(np.float32)
    iml_src_ti = ti.ndarray(dtype=ti.f32, shape=(len(iml_src_tc), 2))
    iml_src_ti.from_numpy(iml_src_tc)
    iml_src_pack = iml_src_tmpl(iml_src=iml_src_ti)

    iml_map_px = Pixels(tv)

    @ti.kernel
    def iml_show_map(iml_map: iml_map_tmpl):
        for i, j in ti.ndrange(w, h):
            m = iml_map.iml_map[i, j]
            rgba = color_map(m, 0.1, 0.5, 0.9)
            iml_map_px.rect(i*rect_w, j*rect_h, rect_w, rect_h, rgba)
    
    @ti.func
    def color_map(val, r=0., g=0., b=0.):
        """Weighted colormap"""
        val = 1 - val
        r = ti.max(0, 1 - ti.abs(val - r))
        g = ti.max(0, 1 - ti.abs(val - g))
        b = ti.max(0, 1 - ti.abs(val - b))
        return ti.Vector([r, g, b, 1])

    @ti.kernel
    def iml_show_src(iml_src: iml_src_tmpl):
        shape = iml_src.iml_src.shape
        for i in range(shape[0]):
            x, y = iml_src.iml_src[i,0], iml_src.iml_src[i,1]
            x = (x + d) * w / (2*d)
            y = (y + d) * h / (2*d)
            rgba = ti.Vector([1, 1, 1, 1])
            iml_map_px.circle(x*rect_w, y*rect_h, 8, rgba)

    def iml_show(iml_map_pack, iml_src_pack, blur=50):
        iml_show_map(iml_map_pack)
        iml_map_px.blur(blur)
        iml_show_src(iml_src_pack)
        tv.px.set(iml_map_px.px)
    
    iml_show(iml_map_pack, iml_src_pack, blur=50)

    @tv.render
    def _():
        return tv.px

if __name__ == '__main__':
    fire.Fire(main)
