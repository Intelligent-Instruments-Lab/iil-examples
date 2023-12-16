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

    @osc.handle('/anguilla/*add_batch')
    def _(address, input:NDArray, output=None):
        """
        receive an ndarray as a JSON dict with shape and data fields,
        serialized into an OSC string 
        """
        print(address)
        print(f'from json: {input=}')

if __name__=='__main__':
    run(main)
