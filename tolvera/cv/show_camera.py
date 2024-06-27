"""tv.cv example.

Example:
    $ python tolvera/cv/show_camera.py --cv True --camera True --device 0
"""

from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    @tv.render
    def _():
        tv.cv()
        tv.px.set(tv.cv.px)
        return tv.px

if __name__ == '__main__':
    run(main)
