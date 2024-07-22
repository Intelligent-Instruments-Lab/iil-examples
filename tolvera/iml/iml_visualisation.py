"""Visualisation of interactive machine learning mapping.
"""

import taichi as ti
import numpy as np
from tolvera import Tolvera, run
from tolvera.pixels import Pixels
from tolvera.utils import *

def tmpl(**kw):
    return ti.types.argpack(**kw)

def pack(tmpl, **kw):
    return tmpl(**kw)

def tmpl_pack(types, data):
    t = tmpl(**types)
    p = pack(t, **data)
    return t, p

def iml_domain_invec(w, h, domain=1):
    X, Y = np.meshgrid(np.linspace(-domain, domain, w), np.linspace(-domain, domain, h), indexing='ij')
    return np.column_stack([X.flatten(), Y.flatten()])

def iml_pairs_to_np(iml):
    pairs = iml.pairs.values()
    return np.array([p[0] for p in pairs]).astype(np.float32)

def iml_domain_map(iml, d_x, d_y, domain_invec, domain_np, domain_ti, **kw) -> np.ndarray:
    outvec = iml.map_batch(domain_invec, **iml.map_kw, **kw)
    domain_np = np.array(outvec).reshape(d_x, d_y)
    return domain_np

def iml_pack_domain(iml, template, domain_invec, domain_np, domain_ti, d_x, d_y):
    domain_np = iml_domain_map(iml, d_x, d_y, domain_invec, domain_np, domain_ti)
    domain_ti.from_numpy(domain_np)
    return pack(template, domain=domain_ti)

def iml_pack_pairs(iml, template, pairs_ti):
    pairs_np = iml_pairs_to_np(iml)
    pairs_ti.from_numpy(pairs_np)
    return pack(template, pairs=pairs_ti)

def iml_resample(iml):
    size = iml.size
    iml.remove_oldest()
    iml.add(input=rand_n(size[0]), output=rand_n(size[1]))

@ti.func
def color_map(val, r=0., g=0., b=0.):
    """Weighted colormap"""
    val = 1 - val
    r = ti.max(0, 1 - ti.abs(val - r))
    g = ti.max(0, 1 - ti.abs(val - g))
    b = ti.max(0, 1 - ti.abs(val - b))
    return ti.Vector([r, g, b, 1])

def main(**kwargs):
    tv = Tolvera(**kwargs)
    size = (2, 1)
    tv.iml.test2test = {
        'size': (size, size),
        'io': (None, None),
        'randomise': True,
        # 'rand_method': 'uniform',
        # 'rand_kwargs': {'low': -d, 'high': d},
        'config': {'interpolate': 'Ripple'},
        'map_kw': {'k': 10, 'ripple_depth': 5, 'ripple': 5}
    }
    
    # Domain
    d_x, d_y, d = kwargs.get('w', 128), kwargs.get('h', 128), kwargs.get('d', 1)
    d_x_px = tv.x // d_x
    d_y_px = tv.y // d_y
    domain_invec = iml_domain_invec(d_x, d_y, d)
    domain_np = np.zeros((d_x, d_y), dtype=np.float32) # TODO: turn this into ti.ndarray?
    domain_ti = ti.ndarray(dtype=ti.f32, shape=(d_x, d_y))
    domain_tmpl = tmpl(domain=ti.types.ndarray())
    domain_pack = pack(domain_tmpl, domain=domain_ti)
    domain_px = Pixels(tv)

    # Pairs
    pairs_tmpl = tmpl(pairs=ti.types.ndarray())
    pairs_ti = ti.ndarray(dtype=ti.f32, shape=(len(tv.iml.test2test.pairs.values()), 2))
    pairs_pack = pack(pairs_tmpl, pairs=pairs_ti)

    @ti.kernel
    def show_domain(packed: domain_tmpl, domain_x: ti.i32, domain_y: ti.i32, px: ti.template(), px_x: ti.i32, px_y: ti.i32):
        x, y = domain_x, domain_y
        for i, j in ti.ndrange(x, y):
            d = packed.domain[i, j]
            rgba = color_map(d, 0.1, 0.5, 0.9)
            px.rect(i*px_x, j*px_y, px_x, px_y, rgba)

    @ti.kernel
    def show_pairs(packed: pairs_tmpl, domain_x: ti.i32, domain_y: ti.i32, domain: ti.i32, px: ti.template(), px_x: ti.i32, px_y: ti.i32):
        shape = packed.pairs.shape
        x, y, d = domain_x, domain_y, domain
        for i in range(shape[0]):
            _x, _y = packed.pairs[i,0], packed.pairs[i,1]
            _x = (_x + d) * x / (2*d)
            _y = (_y + d) * y / (2*d)
            rgba = ti.Vector([1, 1, 1, 1])
            px.circle(_x*px_x, _y*px_y, 8, rgba)

    def update(iml):
        nonlocal d_x, d_y
        nonlocal domain_invec, domain_tmpl, domain_ti, domain_np, domain_ti
        nonlocal pairs_tmpl, pairs_ti
        nonlocal domain_pack, pairs_pack
        iml_resample(iml)
        domain_pack = iml_pack_domain(iml, domain_tmpl, domain_invec, domain_np, domain_ti, d_x, d_y)
        pairs_pack = iml_pack_pairs(iml, pairs_tmpl, pairs_ti)

    update(tv.iml.test2test)
    iml_resample(tv.iml.test2test)

    def show():
        nonlocal domain_px, domain_pack, pairs_pack
        show_domain(domain_pack, d_x, d_y, domain_px, d_x_px, d_y_px)
        show_pairs(pairs_pack, d_x, d_y, d, domain_px, d_x_px, d_y_px)
        tv.px.set(domain_px.px)

    @tv.render
    def _():
        update(tv.iml.test2test)
        iml_resample(tv.iml.test2test)
        show()
        return tv.px

if __name__ == '__main__':
    run(main)
