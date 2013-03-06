#!/usr/bin/python
# Calculates spread for files in a directory

import os
import sys

from flowtools.datamaps import create_filenames, System
from flowtools.spread import Spread

try:
    base = sys.argv[1]
    floor = int(sys.argv[2])
    save = sys.argv[3]
except Exception:
    print("Usage: %s %s %s %s %s"
            % (sys.argv[0], 'base', 'floor', 'save',
                '[delta_t [[min_mass [start [end]]]]'))
    exit()

try:
    delta_t = float(sys.argv[4])
except Exception:
    delta_t = 0.

try:
    min_mass = float(sys.argv[5])
except Exception:
    min_mass = 0.

try:
    start = int(sys.argv[6])
except Exception:
    start = 1

try:
    end = int(sys.argv[7])
except Exception:
    end = None

system = System(delta_t = delta_t, min_mass = min_mass, floor = floor)

# Try file paths
num = start
while os.path.isfile('%s%05d%s' % (base, num, '.dat')):
    num += 1

# Set end frame
if end and num > end:
    num = end + 1

# Create file names and collect spread
system.datamaps = create_filenames(base, list(range(start, num)))
collect = Spread(system, delta_t = delta_t, print = True)
collect.com()

# Save to file in same folder
_file = os.path.dirname(base) + '/' + save
collect.save(_file)
