"""
Authors:
  Victor Shepardson
  Intelligent Instruments Lab 2024
"""

import torch
import anguilla as ag
import iipyper as ii
import numpy as np

from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from textual.widgets import Header, Footer, Static, Button, RichLog
from textual.containers import Container
from textual.reactive import reactive

def get_sr(nn):
    """get sample rate from nn~ model"""
    try: return nn.sr # newer models
    except Exception:
        try: return nn.sampling_rate # older victor-shepardson fork models
        except Exception: return None # very old models


class RAVEProcess(ii.AudioProcess):
    def init(self, rave_path):
        with torch.inference_mode():
            self.rave = torch.jit.load(rave_path)
        # here it's possible to update parameters before the audio stream starts
        self.samplerate = get_sr(self.rave)
        latent_size = self.rave.decode_params[0]
        # can set initial values of arguments to `step` here
        self.step_params['z'] = torch.zeros(latent_size)
        # return value of init gets sent to main process
        return latent_size

    def step(self, z):
        with torch.inference_mode():
            # if z is None:
                # return torch.zeros(self.rave.decode_params[1], 1)
            return self.rave.decode(z[None,:,None])[:,0].T

def main(
        rave_path,
        device=None,
        n_pts=128,
        k=8,
        buffer_frames=1,
        audio_block=256,
        render_map=True,
        profile=False
        ):
    """
    Args:
        rave_path: path to RAVE model .ts file
        device: audio device index or name
        n_pts: number of points in anguilla map
        k: number of nearest neighbors to use
        buffer_frames: trade latency for stability in audio backend
        audio_block: audio driver block size
        render_map: initial value of option render anguilla map
        profile: print performance info
    """

    # two dimensions: XY pad
    d_src = 2

    # smooth audio using a separate process
    rave_process = RAVEProcess(
        rave_path=rave_path, 
        device=device, dtype=np.float32, blocksize=audio_block,
        buffer_frames=buffer_frames,
        use_input=False
        )
    
    # get return value of rave_process.init
    d_tgt = rave_process.recv()

    class CtrlPad(Container):

        def on_mount(self) -> None:
            self.capture_mouse()
            self._colors = None
            self.render_map = render_map

        def on_mouse_move(self, event):
            w, h = self.content_size
            ctrl[0] = (event.x - 0.5) / w
            ctrl[1] = (event.y - 0.5) / h
            update_z()
            # print(self.content_size)
            # print(self.offset)
            # print(ctrl)
            # print(event)
            self.refresh()

        def on_resize(self):
            self.set_colors()

        def set_colors(self):
            w, h = self.content_size
            if w*h==0: return
            if not self.render_map: return
            # print(w,h)
            x = torch.arange(w)/w
            y = torch.arange(h)/h
            xy = torch.stack((
                x[:,None].expand(w,h),
                y[None].expand(w,h)),
                -1).reshape(-1, 2)
            
            zs = iml.map_batch(xy, k=k)
            cs = zs[:,[1,0,2]].reshape(w,h,3)
            cs = np.clip(((cs+3)/6*256).astype(int), 0, 255)
            cs = cs.transpose(1,0,2)
            # self._colors = cs

            # use of rgb() seems to be limiting performance here...
            self._colors = [[
                Style(color='black', bgcolor=f'rgb({r},{g},{b})') 
                # Style(color='black', bgcolor=f'white') 
                for r,g,b in row] for row in cs]

        def render(self):
            with ii.profile('render', print=tui.print, enable=profile):
                w, h = self.content_size

                _,_,ids,_ = iml.search(
                    ctrl, k=k, return_inputs=False, return_outputs=False)
                ids = set(ids)
                chars = [[' ' for _ in range(w)] for _ in range(h)]

                for i, (src, _) in iml.pairs.items():
                    x, y = int(src[0]*w), int(src[1]*h)
                    if y>0 and y<h and x>0 and x<w:
                        chars[y][x] = '○' if i in ids else '·'
   
                x, y = (ctrl * np.array(self.content_size)).int()
                if y>0 and y<h and x>0 and x<w:
                    chars[y][x] = 'X'

                if self.render_map:
                    if self._colors is None:
                        self.set_colors()

                    t = Text()
                    for trow, crow in zip(chars, self._colors):
                        for ch,style in zip(trow, crow):
                            t.append(ch, style=style)
                        t.append('\n')
                    return t
                else:
                    return '\n'.join(''.join(row) for row in chars)

    class IMLState(Static):
        value = reactive((None,None))
        def watch_value(self, time: float) -> None:
            src, tgt = self.value
            self.update(Panel(f'src: {src}\ntgt: {tgt}', title='state'))

    class IMLTUI(ii.TUI):
        CSS_PATH = 'tui.css'

        BINDINGS = [
            ("r", "randomize", "randomize all"),
            ("i", "inside", "randomize inside"),
            ("o", "outside", "randomize outside"),
            ("d", "delete", "delete near"),
            ("m", "toggle_map", "render anguilla map"),
            ("k", "k_inc", "increment k"),
            ("j", "k_dec", "decrement k"),
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

    # @ii.profile(print=tui.print, enable=profile)
    def update_z():
        z[:] = torch.from_numpy(iml.map(ctrl, k=k))
        rave_process(z=z)
        tui(state=(
            ' '.join(f'{x.item():+0.2f}' for x in ctrl),
            ' '.join(f'{x.item():+0.2f}' for x in z)))
        
    @tui.set_action
    def k_inc():
        nonlocal k
        k += 1
        update_z()
        tui.ctrl_pad.set_colors()
        tui.ctrl_pad.refresh()
    @tui.set_action
    def k_dec():
        nonlocal k
        if k>2:
            k -= 1
            update_z()
            tui.ctrl_pad.set_colors()
            tui.ctrl_pad.refresh()

    @tui.set_action
    def toggle_map():
        tui.ctrl_pad.render_map = not tui.ctrl_pad.render_map
        tui.ctrl_pad.refresh()


    @tui.set_action
    @ii.profile(print=tui.print, enable=profile)
    def delete():
        _, _, ids, scores = iml.search(ctrl, k=k)
        if len(ids) < len(iml.pairs):
            iml.remove_batch(ids)
            update_z()
            tui.ctrl_pad.set_colors()
            tui.ctrl_pad.refresh()

    @tui.set_action
    @ii.profile(print=tui.print, enable=profile)
    def randomize(mode=None):
        # keep the current nearest neighbors and rerandomize the rest
        # print('randomize:')
        if len(iml.pairs):
            if mode=='out':
                srcs, tgts, _, scores = iml.search(ctrl, k=k)
                max_score = max(scores)
                iml.reset()
                for s,t in zip(srcs,tgts):
                    # print(s,t)
                    iml.add(s,t)
            elif mode=='in':
                _, _, ids, scores = iml.search(ctrl, k=k)
                max_score = max(scores)
                iml.remove_batch(ids)
            else:
                iml.reset()
        else:
            max_score = 0

        total_pts = min(len(iml.pairs)+k, n_pts) if mode=='in' else n_pts
        while(len(iml.pairs) < total_pts):
            src = torch.rand(d_src)
            if mode=='in':
                # improve performance of rejection sampling
                src -= 0.5
                src *= max_score **0.5 *2 # assumes sqL2
                src += ctrl
            dist = iml.score(ctrl.numpy(), src.numpy())
            if mode=='out':
                if dist < max_score:
                    continue
                tgt = z + torch.randn(d_tgt)*1.5
            elif mode=='in':
                if dist > max_score:
                    continue
                tgt = torch.randn(d_tgt)*1.5
            else:
                tgt = torch.randn(d_tgt)*1.5
            iml.add(src, tgt)

        update_z()
        tui.ctrl_pad.set_colors()
        tui.ctrl_pad.refresh()

    @tui.set_action   
    def inside():
        randomize(mode='in')

    @tui.set_action   
    def outside():
        randomize(mode='out')

    ###
    randomize()

    # rave_process(z=z)
    ag.interpolate.print = tui.print

    tui.run()


if __name__=='__main__':
    ii.run(main)