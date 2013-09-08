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
input_args.add_argument('datamap', nargs='?',
        help="specified data map to plot profile for, or a data map base for combining several "
        "(see -n, -s for options)")
input_args.add_argument('--number', '-n', type=int, default=0, dest='num_combine', metavar='N',
        help="combine this many maps into a single profile")
input_args.add_argument('--start', '-s', type=int, default=1, metavar='FRAME',
        help="start combining from this data map frame number")
input_args.add_argument('--noshow', dest="show", action="store_false",
        help="do not draw plot of profile")
input_args.add_argument('--print', action="store_true", help="print profile to stdout")
input_args.add_argument('--nofit', action="store_false", dest="fit",
        help="do not make a linear fit for the velocity profile")
input_args.add_argument('--error', action="store_true",
        help="if --print specified, also print standard deviation for flow profile")
input_args.add_argument('--quiet', '-q', action="store_true",
        help="output less")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('--draw_fit', action='store_true', help="overlay linear fit in plot")
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

# Define system and add data maps
system = System()
if args.num_combine == 0:
    system.datamaps.append(args.datamap)
elif args.num_combine >= 1:
    system.files(base=args.datamap, start=args.start, end=args.start+args.num_combine-1)
else:
    parser.error('negative -n supplied')

# Collect profile data into 2D arrays
profile = {'data': [], 'count': [], 'std': [], 'error': []}

for i, _file in enumerate(system.datamaps):
    datamap = DataMap(_file, min_mass=args.min_mass)
    height = {'data': []}

    for _type in profile.keys():
        profile[_type].append([])

    for row in datamap.cells:
        count = 0
        flow = []
        y = row[0]['Y']
        height['data'].append(y)

        for cell in row:
            if cell['M'] > args.min_mass:
                flow.append(cell['U'])
                count += 1
            else:
                flow.append(0.)

        profile['data'][i].append(np.array(flow).mean())
        profile['count'][i].append(count)
        profile['std'][i].append(np.array(flow).std())
        profile['error'][i].append(np.array(flow).std()/(np.sqrt(count)))

# Combine data into single profile
combined = {}
combined['data'] = list(np.array(profile['data']).mean(axis=0))
combined['count'] = list(np.array(profile['count']).mean(axis=0))
combined['std'] = list(np.array(profile['data']).std(axis=0))
combined['error'] = list(np.array(combined['std'])/np.sqrt(len(system.datamaps)))

# If height inside desired and count is non-zero, add to final profile
final = {'data': [], 'error': [], 'std': [], 'height': []}
for i, (h, count) in enumerate(zip(height['data'], combined['count'])):
    if h >= args.ymin and h <= args.ymax and count > 0:
        final['height'].append(h)
        for _type in ['data', 'std', 'error']:
            final[_type].append(combined[_type][i])

# Get some plot options
colours = get_colours(args.colour, 2)
linestyles = get_linestyles(args.linestyle, 2)
labels, draw_legend = get_labels(args.label, 2)
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title)
plt.plot(final['data'], final['height'], color=colours[0], linestyle=linestyles[0], label=labels[0])

# Calculate and print linear fit if wanted
if args.fit:
    fitfunc = lambda p, h, f: f - p[0] - p[1] * h
    pinit = [1.0, 0.1]
    out = optimize.leastsq(fitfunc, pinit,
        args=(np.array(final['height']), np.array(final['data'])), full_output=1)

    pfinal = out[0]
    A = pfinal[0]
    B = pfinal[1]

    print("Linear fit of flow U as a function of height H, U = A + B * H:")
    print("A = %g" % A)
    print("B = %g" % B)

    if args.draw_fit:
        plt.plot(A + B * np.array(final['height']), final['height'],
                color=colours[1], label=labels[1], linestyle='dashed')

if draw_legend:
    plt.legend(loc=7)

# Print profile if wanted
if args.print:
    print()
    if not args.quiet:
        print("%8s %12s" % ("H", "(avg) U"), end=' ')
        if args.draw_fit:
            print("%12s" % "(fit) U", end=' ')
        if args.error:
            print("%12s %12s" %("std error", "std"), end=' ')
        print()

    for h, flow, flowerror, flowstd in zip(
            final['height'], final['data'], final['error'], final['std']):
        print("%8.3f %12.6f" % (h, flow), end=' ')
        if args.draw_fit:
            print("%12.6f" % (A + B * h), end=' ')
        if args.error:
            print("%12.6f %12.6f" % (flowerror, flowstd), end=' ')
        print()

# Save if desired
if args.save:
    plt.savefig(args.save, dpi=args.dpi)

# Show figure if wanted
if args.show:
    plt.show()
