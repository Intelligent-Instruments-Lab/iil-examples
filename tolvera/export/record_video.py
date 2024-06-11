"""
Record a video of a Tölvera program

Work in progress: not possible to record long videos yet.

Example:
    python record_video.py --f=16 --r=4 --c=0 --w=512 --h=512 --output_dir='./output' --filename='output' --automatic_build=True --build_mp4=True --build_gif=False --clean_frames=True
"""

from tolvera import Tolvera, run, VideoRecorder

def main(**kwargs):
    tv = Tolvera(**kwargs)

    vid = VideoRecorder(tv, **kwargs)

    @tv.cleanup
    def write():
        vid.write()

    @tv.render
    def _():
        vid()
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px
    

if __name__ == '__main__':
    run(main)
