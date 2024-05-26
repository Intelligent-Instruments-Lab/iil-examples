import taichi as ti
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tolvera import Tolvera, run
from tolvera.pixels import Pixels

def np_txt(text:str, w:int, h:int=None, color:str="#000000"):
    if h is None: h=w
    font = 'Arial.otf'
    font_size = min(w,h)//(len(text)/3)
    pil_font = ImageFont.truetype(font, size=font_size, encoding="unic")
    bbox = pil_font.getbbox(text)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    canvas = Image.new('RGB', [w, h], (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    offset = ((w - text_width) // 2, (h - text_height) // 2)
    draw.text(offset, text, font=pil_font, fill=color)

    canvas = (255 - np.asarray(canvas).astype(np.float32))
    canvas = np.rot90(canvas, axes=(1, 0))
    return canvas

def main(**kwargs):
    tv = Tolvera(**kwargs)

    w, h = tv.x, tv.y
    x, y = tv.x/2 - w/2, tv.y/2 - h/2
    phantom = np_txt("Tölvera", w, h)
    img_fld = ti.field(dtype=ti.f32, shape=phantom.shape)
    img_fld.from_numpy(phantom)
    img_px = Pixels(tv, x=w, y=h)
    img_px.from_numpy(img_fld)

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.slime(tv.p, tv.s.species())
        tv.v.slime.trail.blend_max(img_px)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
