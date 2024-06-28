from collections import namedtuple

import numpy as np

from iipyper import run, MIDI, repeat, audio, thread
import anguilla as ag
import signalflow as sf

# this needs to be outside of scope of main...
graph = sf.AudioGraph()

def main(
        input_size=None, output_size=5, verbose=2,
        block_size=512, device=('Macbook Pro Mic', 'Macbook Pro Speakers'),
        sample_rate=48000, channels=1,
        ):
    
    if input_size is None:
        input_size = block_size//4

    graph.config.print()
    graph.poll(2)

    class Synth(sf.Patch):
        def __init__(self, f1=880, f2=55, idx=1):
            super().__init__()
            f1 = sf.Smooth(self.add_input("f1", f1))
            f2 = sf.Smooth(self.add_input("f2", f2))
            idx = sf.Smooth(self.add_input("idx", idx))
            mod = sf.SineOscillator(f2)
            sine = sf.SineOscillator(f1 * (1+idx)*mod)
            env = 0.2#sf.ASREnvelope(0.001, duration, 0.001)
            output = sf.StereoPanner(sine * env, 0)
            self.set_output(output)
    synth = Synth()
    synth.play()

    midi = MIDI(verbose=verbose)

    iml = ag.IML()
    b = 128
    iml.add_batch(np.random.randn(b, input_size), np.random.randn(b, output_size))

    state = {
        'mark_input':False,
        'mark_output':False,
        }

    @midi.handle(port='Grid', type='cc', control=40)
    def mark_input(msg):
        if msg.value > 0:
            # print('marking input...')
            state['input'] = []
            state['mark_input'] = True
        else:
            # print('done marking input')
            state['mark_input'] = False

    @midi.handle(port='Grid', type='cc', control=41)
    def mark_output(msg):
        if msg.value > 0:
            # print('marking output...')
            state['output'] = []
            state['mark_output'] = True
        else:
            # print('done marking output')
            state['mark_output'] = False

    def is_empty(k):
        return k in state and len(state[k])==0
    
    def is_full(k):
        return k in state and len(state[k])>0

    # @thread
    def process_input(inp):
        out = iml.map(inp)
        print(out)
        synth.set_input('f1', 2**out[0]*440)
        synth.set_input('f2', 2**out[1]*55)
        synth.set_input('idx', 2**out[0])
        # ensure that at least one frame is captured
        # not in state -> not recording
        # empty list -> recording
        # non-empty list and mark_* is True -> recording
        # non-empty list and mark_* is False -> not recording
        if state['mark_input'] or is_empty('input'):
            state['input'].append(inp)
        if state['mark_output'] or is_empty('output'):
            state['output'].append(out)

        # when recording is done:
        if (
            not state['mark_input'] and is_full('input')
            and not state['mark_output'] and is_full('output')
        ):
            inp = state.pop('input')
            out = state.pop('output')
            inp = np.stack(inp)
            out = np.stack(out)
            # add 
            print(f'add data {inp.shape}->{out.shape}')
            # TODO -- handle whole recordings
            # for now -- take the first element
            iml.add(inp[0], out[0])
            print(f'{len(iml.pairs)=}')
    
    # audio input
    # TODO: send to a queue,
    # make a @repeat to unqueue
    # or should there be an iipyper decorator to switch threads via queue...?
    window = np.cos(np.linspace(0, 2*np.pi, block_size))*-0.5+0.5
    mean = None
    var = None
    @audio(channels=channels, device=device, 
        blocksize=block_size, samplerate=sample_rate)
    def audio_process(indata:np.ndarray, outdata:np.ndarray):
        # print(indata.shape, outdata.shape)
        indata[:] = indata * window[:,None]
        spectrum = np.log(1e-7 + np.abs(np.fft.rfft(indata, axis=0)))
        # cepstrum = np.abs(np.fft.rfft(spectrum[:-1], axis=0))
        cepstrum = spectrum[:spectrum.shape[0]//2]
        nonlocal mean, var
        if mean is None: mean = cepstrum
        if var is None: var = np.ones_like(cepstrum)
        mean[:] = mean * 0.99 + cepstrum * 0.01
        var[:] = var * 0.99 + (cepstrum-mean)**2 * 0.01

        # out = np.mean((cepstrum - mean), -1)
        out = np.mean((cepstrum - mean)/(1e-7 + np.sqrt(var)), -1)
        # print(spectrum.dtype)
        # print(cepstrum.shape)
        # print(out[:5])
        # outdata[:] = np.random.randn(*outdata.shape)*1e-3
        # outdata[:] = 0
        process_input(out[:input_size])

    # simulate input
    # @repeat(0.01, lock=True)
    # def _():
        # print('enter repeat')
        # sensor(np.random.randn(input_size))
        # print('exit repeat')



if __name__=='__main__':
    run(main)