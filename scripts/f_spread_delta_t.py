#!/usr/bin/env python

# Flowtools - a suite of tools for handling and drawing flow data
# Copyright (C) 2013 Petter Johansson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
