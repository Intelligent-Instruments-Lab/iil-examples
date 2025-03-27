import taichi as ti
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tolvera import Tolvera, run
from tolvera.pixels import Pixels

def np_txt(text:str, w:int, h=None, x=0, y=0, size=None, color:str="#000000"):
    if h is None: h=w
    # replace font path with your own
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = size if size is not None else min(w,h)//(len(text)/2)
    pil_font = ImageFont.truetype(font, size=font_size, encoding="unic")
    bbox = pil_font.getbbox(text)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    canvas = Image.new('RGB', [w, h], (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    offset = ((w - text_width) // 2, (h - text_height) // 2.5)
    # draw.text((x,y), text, font=pil_font, fill=color)
    draw.text(offset, text, font=pil_font, fill=color)

    canvas = (255 - np.asarray(canvas).astype(np.float32))
    canvas = np.rot90(canvas, axes=(1, 0))
    return canvas

def text(tv, text:str, w:int, h:int, size=None, color:str="#000000"):
    canvas = np_txt(text, w, h, size=size, color=color)
    img_fld = ti.field(dtype=ti.f32, shape=canvas.shape)
    img_fld.from_numpy(canvas)
    img_px = Pixels(tv, x=w, y=h)
    img_px.from_numpy(img_fld)
    return img_px

@ti.data_oriented
class Ruler:
    def __init__(self,
                 tolvera,
                 ticks:int=10,
                 start:tuple=(100,0),
                 end:tuple=(100,100),
                 domain:tuple=(0,100),
                 rgba:list=[1.,1.,1.,1.]):
        self.tv = tolvera
        self.ticks = ticks
        self.tick_len = 5
        self.start = ti.math.vec2(*start)
        self.end = ti.math.vec2(*end)
        self.domain = ti.math.vec2(*domain)
        self.rgba = [1.,1.,1.,1.]
        self.axis = 1 if end[1] > end[0] else -1 # 1 for +y axis and -1 for +x axis
        self.create_tick_labels()
    
    def create_tick_labels(self):
        self.tick_labels = []
        print(f"[Ruler] Creating {self.ticks} tick labels")
        for i in range(self.ticks):
            d = self.domain
            label_str = f"{d[0] + (i+1) * (d[1] - d[0]) / self.ticks}"
            txt = text(self.tv, label_str, 100, 50, 12)
            self.tick_labels.append(txt)

    @ti.kernel
    def draw_lines(self):
        self.tv.px.line(self.start[0], self.start[1], self.end[0], self.end[1], ti.Vector(self.rgba))
        for i in ti.static(range(self.ticks)):
            l = self.tick_len
            x = self.start[0] + (self.end[0] - self.start[0]) * (i+1) / self.ticks
            y = self.start[1] + (self.end[1] - self.start[1]) * (i+1) / self.ticks
            if self.axis == 1:
                self.tv.px.line(x, y, x+l, y, ti.Vector(self.rgba))
            elif self.axis == -1:
                self.tv.px.line(x, y, x, y+l, ti.Vector(self.rgba))

    def draw_labels(self):
        for i in range(self.ticks):
            l = self.tick_len
            x = int(self.start[0] + (self.end[0] - self.start[0]) * (i+1) / self.ticks)
            y = int(self.start[1] + (self.end[1] - self.start[1]) * (i+1) / self.ticks)
            self.tv.px.stamp(x-l, y, self.tick_labels[i])

    def __call__(self):
        self.draw_lines()
        self.draw_labels()

def main(**kwargs):
    tv = Tolvera(**kwargs)
    x = Ruler(tv, start=(500,500), end=(500, 1000))
    y = Ruler(tv, start=(500,500), end=(1000, 500))

    @tv.render
    def _():
        tv.px.clear()
        x()
        y()
        return tv.px

if __name__ == '__main__':
    run(main)
