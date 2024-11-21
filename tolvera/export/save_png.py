import taichi as ti
from tolvera import Tolvera, run, FrameRecorder

def main(**kwargs):
    tv = Tolvera(**kwargs)
    recorder = FrameRecorder(tv, output_dir='./screenshots')
    
    @tv.render
    def _():
        # Capture frame when space is pressed
        if tv.ti.window.is_pressed(ti.ui.SPACE):
            recorder.capture_frame()
            
        # Or capture with custom name
        if tv.ti.window.is_pressed(ti.ui.RETURN):
            recorder.capture_frame(custom_name='special_moment')

        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.v.slime(tv.p, tv.s.species())
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
