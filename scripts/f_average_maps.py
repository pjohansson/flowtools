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
Script for taking the average of several data maps combined into one.

"""


import argparse
import numpy as np

from flowtools.datamaps import DataMap, System
from sys import exit

def combine_maps(datamaps, start, end):
    """
    Combine datamaps from file list in datamaps from positions start to end,
    return.

    """

    datamap = DataMap(datamaps[start])
    for i, name in enumerate(datamaps[start+1:end]):
        add = DataMap(name)
        for row, _ in enumerate(datamap.cells):
            for cell, _ in enumerate(datamap.cells[row]):
                for key in datamap.cells[row][cell].keys():
                    prev = datamap.cells[row][cell][key]
                    cur = add.cells[row][cell][key]
                    avg = ((i+1)*prev + cur)/(i+2)

                    datamap.cells[row][cell][key] = avg

    return datamap

parser = argparse.ArgumentParser(description="Average flow maps and output new.")

parser.add_argument('--filebase', '-f', required=True, type=str,
        help="file name base of system")
parser.add_argument('--number', '-n', type=int, default=1, dest="stride",
        help="number of data maps to average over")
parser.add_argument('--out', '-o', type=str, default="out_",
        help="output file name base (default: 'out')")
parser.add_argument('--start', '-s', type=int, default=1,
        help="starting data map number")
parser.add_argument('--end', '-e', type=int, default=np.inf,
        help="final data map number")

args = parser.parse_args()

system = System(base=args.filebase)
system.files(start=args.start, end=args.end)

num_out = int(len(system.datamaps) / args.stride)
print("Averaging data maps of base '%s' from %d to %d, %d maps to 1."
        % (args.filebase, args.start, args.start+len(system.datamaps)-1, args.stride))

if num_out == 0:
    print(num_out)
    print("Not enough maps (%d) for chosen averaging number (%d)."
            % (args.end - args.start + 1, args.stride))
    exit()
elif num_out == 1:
    print("Saving 1 map to base '%s'." % (args.out))
else:
    print("Saving a total of %d maps to base '%s'." % (num_out, args.out))

if len(system.datamaps) % args.stride != 0:
    print()
    print("WARNING: Number of maps (%d) not a multiple of averaging number (%d), ignoring rest."
            % (len(system.datamaps), args.stride))

for i in range(num_out):
    start = i*args.stride
    end = start + args.stride

    datamap = combine_maps(system.datamaps, start, end)
    datamap.save("%s%05d%s" % (args.out, i+1, ".dat"))
