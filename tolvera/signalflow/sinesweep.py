from tolvera import Tolvera, run
from tolvera.osc.update import Updater
from signalflow import *

def main(**kwargs):
    tv = Tolvera(**kwargs)

    graph = AudioGraph()

    freq = 440
    sine = SineOscillator(freq)
    stereo = StereoPanner(sine, 0.0)
    output = sine * 0.1
    output.play()

    def _update():
        nonlocal freq
        sine.frequency = freq
        freq += 1
        if freq > 10000:
            freq = 440

    updater = Updater(_update, 1)

    @tv.render
    def _():
        updater()
        return tv.px

if __name__ == '__main__':
    run(main)
