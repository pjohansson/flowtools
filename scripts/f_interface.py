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
Script for working with the interface of droplets.

"""

import argparse
import numpy as np
import os
import pylab as plt

from flowtools.datamaps import System, DataMap

parser = argparse.ArgumentParser(
        description="Draw graphs of the flow in data maps.")

# Input base arguments
input_args = parser.add_argument_group('input')
input_args.add_argument('base', nargs='?', default=None,
        help="file name base of system, combine with --start "
            "and --end to work on range of maps using this base")
input_args.add_argument('-s', '--start', type=int, default=1,
        help="initial frame number")
input_args.add_argument('-e', '--end', type=int, default=np.inf,
        help="final frame number")
input_args.add_argument('-f', '--file', help="specific file to work on")

# Output arguments
output_args = parser.add_argument_group('output modes')
output_args.add_argument('-l', '--length', action='store_true',
        help="output the interface length of maps")
output_args.add_argument('--noshow', action="store_false", dest='show',
        help="do not display figures")
output_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
output_args.add_argument('--dpi', default=150, type=int, help="output graph dpi")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
draw_args.add_argument('--xmax', type=float, default=None, metavar='X')
draw_args.add_argument('--xmin', type=float, default=None, metavar='X')
draw_args.add_argument('--ymax', type=float, default=None, metavar='Y')
draw_args.add_argument('--ymin', type=float, default=None, metavar='Y')
draw_args.add_argument('--axis', default='scaled')

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Position (nm)')
label_args.add_argument('--ylabel', default='Height (nm)')
label_args.add_argument('--title', default='')

# Parse
args = parser.parse_args()

xlims = [args.xmin, args.xmax]
ylims = [args.ymin, args.ymax]

# If base given, create system
if args.base != None:
    system = System(base = args.base)
    system.files(start = args.start, end = args.end)

else:
    system = System()
    system.datamaps = [args.file]

for frame, _file in enumerate(system.datamaps):

    # If saved figures desired construct filename
    if args.save:
        if args.base != None:
            save = '%s%05d%s' % (args.save, frame + args.start, '.png')
        else:
            save = args.save
    else:
        save = ''

    datamap = DataMap(_file, min_mass = args.min_mass)

    datamap.draw_interface()
    plt.axis(args.axis)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)
    plt.title(args.title)

    if args.length:
        print(datamap._interface_length())

    if args.show:
        plt.show()

    if args.save != '':
        plt.savefig(save, dpi=args.dpi)

    plt.clf()
