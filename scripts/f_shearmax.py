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
Script for drawing the velocity profile of a flowmap along the y axis.

"""

import argparse
import numpy as np
import os
import pylab as plt
import sys

from flowtools.datamaps import System, DataMap
from flowtools.draw import plot_line
from flowtools.utils import get_colours, get_labels, get_linestyles
from scipy import optimize

parser = argparse.ArgumentParser(
        description="Calculate the maximum shear rate of a datamap.")

# Input base arguments
input_args = parser.add_argument_group('input')
input_args.add_argument('datamap', nargs='?',
        help="datamap base to calculate shear for")
input_args.add_argument('--floor', type=int, default=0, metavar='N',
        help="calculate shear from this floor")
input_args.add_argument('--number', '-n', type=int, default=1, dest='num_shear', metavar='N',
        help="calculate shear over this many cells in y")
input_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
input_args.add_argument('--begin', '-b', type=int, default=1, metavar='FRAME',
        help="start combining from this data map frame number")
input_args.add_argument('--end', '-e', type=int, default=np.inf, metavar='FRAME',
        help="combine up to this data map frame number (default: infinity)")
input_args.add_argument('--delta_t', '-dt', type=float, default=1, metavar='DT',
        help="difference in time between frames (default: 1)")
input_args.add_argument('--noshow', dest="show", action="store_false",
        help="do not draw plot of shear per map")
input_args.add_argument('--print', action="store_true", help="print profile to stdout")
input_args.add_argument('--all', action="store_true",
        help="draw or print all shear values along an axis, not just max")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('-c', '--colour', action='append', default=[], help="line colour")
draw_args.add_argument('-l', '--label', action='append', default=[],
        help="line label, add once per line")
draw_args.add_argument('--linestyle', action='append', default=[],
        choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="line style (default: solid)")
draw_args.add_argument('--ymin', type=float, default=-np.inf,
        metavar='Y', help="minimum y (nm)")
draw_args.add_argument('--ymax', type=float, default=np.inf,
        metavar='Y', help="maximum y (nm)")
draw_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
draw_args.add_argument('--dpi', type=int, default=150, help="output graph dpi")

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Time (ps)')
label_args.add_argument('--ylabel', default='Maximum shear (1/ps)')
label_args.add_argument('--title', default='Maximum found shear of system per time')

# Parse and control for action
args = parser.parse_args()

# Plot options
colours = get_colours(args.colour, 2)
linestyles = get_linestyles(args.linestyle, 2)
labels, draw_legend = get_labels(args.label, 2)

# Define system and add data maps
system = System()
system.files(base=args.datamap, start=args.begin, end=args.end)

# Collect shear data in list
frames = []
max_shear = []

floor = args.floor
ceil = floor + args.num_shear
if ceil <= floor:
    parser.error('number of cell rows to calculate shear over (--number) must be positive')

rows = [floor, ceil]

for i, _file in enumerate(system.datamaps):
    print("Reading %s (%d of %d) ... " % (_file, i+1, len(system.datamaps)), end='')
    sys.stdout.flush()
    datamap = DataMap(_file, min_mass=args.min_mass)
    print("Done!")

    dy = datamap.info['cells']['size']['Y']
    shear = []
    xarray = []

    for col in range(datamap.info['cells']['num_cells']['X']):
        U = [0., 0.]
        try:
            for j, row in enumerate(rows):
                if not datamap.cells[row][col]['droplet']:
                    raise Exception
                U[j] = datamap.cells[row][col]['U']

            shear.append(abs(U[1] - U[0])/dy)
            xarray.append(datamap.cells[0][col]['X'])
        except Exception:
            next

    if shear != []:
        frames.append((i+args.begin)*args.delta_t)
        max_shear.append(max(shear))

    if args.all:
        if args.print:
            for x, val in zip(xarray, shear):
                print("%g %g" % (x, val))

        if args.show:
            plt.plot(xarray, shear, color=colours[0], linestyle=linestyles[0], label=labels[0])
            plt.show()
            plt.clf()
            plt.xlabel(args.xlabel)
            plt.ylabel(args.ylabel)
            plt.title(args.title)

# Get some plot options
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title)
plt.plot(frames, max_shear, color=colours[0], linestyle=linestyles[0], label=labels[0])

# Print profile if wanted
if args.print and not args.all:
    print()
    for t, shear in zip(frames, max_shear):
        print("%g %g" % (t, shear))

# Save if desired
if args.save:
    plt.savefig(args.save, dpi=args.dpi)

# Show figure if wanted
if args.show and not args.all:
    plt.show()
