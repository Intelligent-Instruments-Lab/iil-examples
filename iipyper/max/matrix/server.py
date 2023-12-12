"""
Authors:
  Victor Shepardson
  Jack Armitage
  Intelligent Instruments Lab 2023
"""

"""
This example receives the 2d matrix sent two ways by `matrix.maxpat`
"""

import numpy as np

from iipyper import OSC, run
from iipyper.types import *

def main(port=9999):
    osc = OSC(port=port)

    @osc.handle
    def matrixflat(address, w:int, h:int, data:Splat[None]):
        """
        receive a 2d array as a flat sequence of numbers, 
        starting with the array dimensions followed by all the values.
        """
        arr = np.array(data).reshape((w,h))
        print(f'from flat: {arr=}')

    @osc.handle
    def matrixjson(address, arr:NDArray):
        """
        receive an ndarray as a JSON dict with shape and data fields,
        serialized into an OSC string 
        """
        print(f'from json: {arr=}')

if __name__=='__main__':
    run(main)
