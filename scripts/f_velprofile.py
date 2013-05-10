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

from flowtools.datamaps import System, DataMap
from flowtools.draw import plot_line
from flowtools.utils import get_colours, get_labels, get_linestyles
from scipy import optimize

parser = argparse.ArgumentParser(
        description="Draw graphs of the flow in data maps.")

# Input base arguments
input_args = parser.add_argument_group('input')
input_args.add_argument('datamap', help="data map to plot profile for")
input_args.add_argument('--noshow', dest="show", action="store_false",
        help="do not draw plot of profile")
input_args.add_argument('--print', action="store_true", help="print profile to stdout")
input_args.add_argument('--nofit', action="store_false", dest="fit",
        help="do not make a linear fit for the velocity profile")

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
draw_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
draw_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
draw_args.add_argument('--dpi', type=int, default=150, help="output graph dpi")

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Mass flow along x (nm/ps)')
label_args.add_argument('--ylabel', default='Height (nm)')
label_args.add_argument('--title', default='')

# Parse and control for action
args = parser.parse_args()

profile = []
height = []

# Go through all rows and add upp flow for averaging from cells
datamap = DataMap(args.datamap, min_mass=args.min_mass)

for row in datamap.cells:
    flow = 0.
    num_cells = 0
    y = row[0]['Y']

    for cell in row:
        if cell['M'] > args.min_mass:
            flow += cell['U']
            num_cells += 1

    if flow != 0. and y >= args.ymin and y <= args.ymax:
        flow /= num_cells
        profile.append(flow)
        height.append(y)


# Get some plot options
colours = get_colours(args.colour, 2)
linestyles = get_linestyles(args.linestyle, 2)
labels, draw_legend = get_labels(args.label, 2)
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title)
plt.plot(profile, height, color=colours[0], linestyle=linestyles[0], label=labels[0])

# Calculate and print linear fit if wanted
if args.fit:
    fitfunc = lambda p, h, f: f - p[0] - p[1] * h
    pinit = [1.0, 0.1]
    out = optimize.leastsq(fitfunc, pinit,
        args=(np.array(height), np.array(profile)), full_output=1)

    pfinal = out[0]
    A = pfinal[0]
    B = pfinal[1]

    print("Linear fit of flow f as a function of height h, f = A + B * h:")
    print("A = %g" % A)
    print("B = %g" % B)

    plt.plot(profile, (np.array(profile) - A) / B,
            color=colours[1], label=labels[1], linestyle='dashed')

if draw_legend:
    plt.legend(loc=7)

# Print profile if wanted
if args.print:
    for h, flow in zip(height, profile):
        print("%8.3f %12.6f" % (h, flow))

# Save if desired
if args.save:
    plt.savefig(args.save, dpi=args.dpi)

# Show figure if wanted
if args.show:
    plt.show()
