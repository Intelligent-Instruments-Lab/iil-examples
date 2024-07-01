"""
Authors:
  Victor Shepardson
  Intelligent Instruments Lab 2024
"""

import torch
import anguilla as ag
from iipyper import TUI, audio, start_audio, OSC, run, AudioProcess
import numpy as np

from rich.panel import Panel
from textual.widgets import Header, Footer, Static, Button, RichLog, Sparkline
from textual.containers import Container
from textual.reactive import reactive

class RAVEProcess(AudioProcess):
    def init(self, rave_path):
        with torch.inference_mode():
            self.rave = torch.jit.load(rave_path)

    def step(self, z=None):
        with torch.inference_mode():
            if z is None:
                return torch.zeros(2048, 1) # TODO
            return self.rave.decode(z[None,:,None])[:,0].T

def main(
        device=None,
        rave_path=None,
        n_pts=32,
        k=5,
        buffer_frames=1,
        audio_block=256,
        # osc_host="127.0.0.1", osc_port=9999,
        ):
    # osc = OSC(osc_host, osc_port)
    
    rave = torch.jit.load(rave_path)
    d_src = 2
    d_tgt = rave.encode_params[2]
    try:
        sr = rave.sr
    except Exception:
        sr = rave.sampling_rate
    del rave

    rave_process = RAVEProcess(
        rave_path=rave_path, 
        device=device, dtype=np.float32,
        samplerate=sr, blocksize=audio_block,
        buffer_frames=buffer_frames
        )

    class CtrlPad(Container):
        def on_mount(self) -> None:
            self.capture_mouse()

        def on_mouse_move(self, event):
            w, h = self.content_size
            ctrl[0] = event.x / w
            ctrl[1] = event.y / h
            # z[:] = torch.from_numpy(iml.map(ctrl, k=5))
            z[:] = torch.from_numpy(iml.map(ctrl, k=5))
            rave_process(z=z)
            # print(event)
            self.refresh()
            tui(state=(
                ' '.join(f'{x.item():+0.2f}' for x in ctrl),
                ' '.join(f'{x.item():+0.2f}' for x in z)))

        def render(self):
            _,_,ids,_ = iml.search(ctrl, k=k)

            w,h = self.content_size
            chars = [[' ' for _ in range(w)] for _ in range(h)]

            for i, (src, _) in iml.pairs.items():
                src = np.array(src) * np.array(self.content_size)
                x, y = src.astype(int)
                if y>0 and y<h and x>0 and x<w:
                    chars[y][x] = '0' if i in ids else '*'

            x, y = (ctrl * np.array(self.content_size)).int()
            if y>0 and y<h and x>0 and x<w:
                chars[y][x] = 'X'

            return '\n'.join(''.join(row) for row in chars)

    class IMLState(Static):
        value = reactive((None,None))
        def watch_value(self, time: float) -> None:
            src, tgt = self.value
            self.update(Panel(f'src: {src}\ntgt: {tgt}', title='state'))

    class IMLTUI(TUI):
        CSS_PATH = 'tui.css'

        BINDINGS = [
            ("r", "randomize", "randomize around current mapping"),
            # ("z", "zero", "reset to zero vector"),
            # ("s", "store", "store a source / target"),
        ]

        def __init__(self):
            super().__init__()
            self.ctrl_pad = CtrlPad()

        def compose(self):
            """Create child widgets for the app."""
            yield Header()
            yield self.std_log
            yield self.ctrl_pad
            yield IMLState(id='state')
            yield Footer()

    tui = IMLTUI()

    print = ag.print = tui.print

    ctrl = torch.zeros(d_src)
    z = torch.zeros(d_tgt)  

    iml = ag.IML()

    # TODO: button to fix current neighbors
    # or record a gesture and fix those neighbors
    # draw locations of current sources

    @tui.set_action
    def randomize():
        # keep the current nearest neighbors and rerandomize the rest
        # print('randomize:')
        if len(iml.pairs):
            # iml.reset(keep_near=ctrl, k=k)
            srcs, tgts, _, scores = iml.search(ctrl, k=k)
            max_score = max(scores)
            iml.reset()
            for s,t in zip(srcs,tgts):
                # print(s,t)
                iml.add(s,t)
        else:
            max_score = 0

        # print(f'{tui.ctrl_pad.content_size=}')
        # print(f'{tui.ctrl_pad.content_offset=}')
        while(len(iml.pairs) < n_pts):
            src = torch.rand(d_src)#/(ctrl.abs()/2+1)
            dist = iml.distance(ctrl.numpy(), src.numpy())
            if dist < max_score:
                continue
            tgt = z + torch.randn(d_tgt)*2#/(z.abs()/2+1)
            iml.add(src, tgt)

        tui.ctrl_pad.refresh()

    # @tui.set_action
    # def zero():
    #     z.zero_()
    #     randomize()

    ###
    randomize()

    # rave_process(z=z)

    tui.run()


if __name__=='__main__':
    run(main)