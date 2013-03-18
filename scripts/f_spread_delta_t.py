#!/usr/bin/env python

"""
Script for changing the delta_t for spread data files.

"""

import argparse
import numpy as np

from flowtools.datamaps import Spread

parser = argparse.ArgumentParser()
parser.add_argument('spreading', nargs='+',
        help="files to modify with new time")
parser.add_argument('-dt', '--delta_t', required=True, type=float,
        help="new delta_t for files")
parser.add_argument('-t0', type=float, help="set new initial time of maps")
parser.add_argument('-o', '--output', nargs='+',
        help="list of files to output to instead of overwriting read")
args = parser.parse_args()

# Set output to output, else input
if args.output:
    # Control that corresponding files exist
    if (len(args.spreading) != len(args.output)):
        parser.error(
                "number of output files does not match number of spread files"
                )
    output = args.output
else:
    output = args.spreading

# Edit and output one at a time
for i, _file in enumerate(args.spreading):
    spread = Spread().read(_file)

    spread.delta_t = args.delta_t
    times = np.array(spread.frames) * args.delta_t
    if args.t0 != None:
        times -= times[0] - args.t0

    spread.times = list(times)
    spread.save(output[i])
