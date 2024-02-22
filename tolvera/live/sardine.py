"""Live coding Tölvera via Sardine

Sardine: https://sardine.raphaelforment.fr

Currently this does not work with Sardine's own REPL, 
but rather works with VSCode's built-in Python REPL.

So to use this, open this file in VSCode, and then
evaluate the code below block-by-block using shift+enter.
"""

from sardine_core.run import *
from tolvera import Tolvera
import taichi as ti
tv = Tolvera()

tv.s.params = {'state':{
    'width':     (ti.i32, 0, 100),
    'evaporate': (ti.f32, 0., 0.99),
}}

@ti.kernel
def _draw():
    w = tv.s.params[0].width
    x = ti.cast(tv.x/2, ti.i32)
    y = ti.cast(tv.y/2, ti.i32)
    tv.px.rect(x,y, w, w, ti.Vector([1.,0.,0.,1.]))
draw = _draw

@swim
def gui_loop(p=0.5, i=0):
    e = tv.s.params.field[0].evaporate
    tv.px.diffuse(e)
    tv.p()
    draw()
    tv.v.move(tv.p)
    tv.px.particles(tv.p, tv.s.species())
    tv.show(tv.px)
    again(gui_loop, p=1/64, i=i+1)

silence(gui_loop)

@swim
def control_loop(p=4, i=0):
    tv.s.params.field[0].evaporate = P('0.9 0.99 0.1', i)
    tv.s.params.field[0].width = P('10 100 10 1000', i)
    again(control_loop, p=1/2, i=i+1)

silence(control_loop)
