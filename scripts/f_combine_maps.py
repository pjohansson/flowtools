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
Script for combining old data maps of a system to a new type.

"""

import argparse
import numpy as np
import os

from flowtools.datamaps import DataMap, System

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--output', required=True,
        help="path to output combined file")
parser.add_argument('-d', '--dens', required=True,
        help="base path of density map to combine")
parser.add_argument('-f', '--flow', required=True,
        help="base path of flow map to combine")
parser.add_argument('-s', '--start', default=1, type=int,
        help="initial frame number")
parser.add_argument('-e', '--end', default=np.inf, type=int,
        help="final frame number")
parser.add_argument('-ext', '--extension', default='.dat',
        help="extension of map files")
parser.add_argument('--numdigits', default=5, type=int,
        help="number of frame digits in file names")

args = parser.parse_args()

def combine(_path):
    """Combine and return density and flow map in _path."""

    # Read maps using non-public ways :O
    dens = DataMap(fields = 'dens')
    dens.path = _path['dens']
    dens._read()
    flow = DataMap(fields = 'flow')
    flow.path = _path['flow']
    flow._read()

    # Container for output
    output = DataMap()
    output.cells = []

    # Go over all density cells, ie. entire system
    i = 0
    with flow.FlatArray(flow.cells) as flow.cells:
        for cell in dens.cells:
            combined = cell.copy()

            # If cells equal, add flow and move to next flow cell
            if (i < len(flow.cells)
                    and cell['X'] == flow.cells[i]['X']
                    and cell['Y'] == flow.cells[i]['Y']):
                combined.update(flow.cells[i])
                i += 1
            else:
                combined.update({'U': 0., 'V': 0.})

            # Append to container
            output.cells.append(combined)

    # Convert by hand to good format and save
    output.cells = np.array(output.cells)
    output._info = output.info
    output._grid()

    return output

# Create containers
dens = System(base = args.dens)
dens.files(start = args.start, end = args.end,
        numdigits = args.numdigits, ext = args.extension)

flow = System(base = args.flow)
flow.files(start = args.start, end = args.end,
        numdigits = args.numdigits, ext = args.extension)

# Combine and output one by one
for i, _list in enumerate(zip(dens.datamaps, flow.datamaps)):
    print("\rCombining maps %d ..." % (i + 1), end = ' ')
    output = combine(dict(zip(['dens', 'flow'], _list)))

    num = ('%%0%dd' % args.numdigits) % (i + args.start)
    save = '%s%s%s' % (args.output, num, args.extension)
    output.save(save)
