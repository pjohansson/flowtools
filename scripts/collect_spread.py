#!/usr/bin/python
# Calculates spread for files in a directory

import argparse
import numpy as np
import os

from flowtools.datamaps import System

parser = argparse.ArgumentParser()

# Required arguments
parser.add_argument('base', help="file name base of system")
parser.add_argument('floor', help="floor of the system", type=int)
parser.add_argument('save', help="file for saving spread data to")

# Optional arguments
parser.add_argument('-dt', '--delta_t', type=float, default=0.,
        help="time difference between frames")
parser.add_argument('-m', '--min_mass', type=float, default=0.,
        help="minimum mass of droplet cells")
parser.add_argument('-s', '--start', type=int, default=1,
        help="initial frame number")
parser.add_argument('-e', '--end', type=int, default=np.inf,
        help="final frame number")
parser.add_argument('-rel', '--relative', action='store_true',
        help="save to path relative to input base directory (False)")

# Parse
args = parser.parse_args()

system = System(
        base = args.base, delta_t = args.delta_t,
        floor = args.floor, min_mass = args.min_mass
        )

# Create file names and collect spread
system.files(start = args.start, end = args.end)
spread = system.spread()

# Save to file in same folder
if args.relative:
    _file = os.path.dirname(args.base) + '/' + args.save
else:
    _file = args.save

spread.save(_file)
