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
Script for plotting flow maps of a system and saving to a base.

"""

import argparse
import numpy as np
import os

from flowtools.datamaps import System, DataMap

parser = argparse.ArgumentParser(
        description="Draw graphs of the flow in data maps.")

# Input base arguments
input_args = parser.add_argument_group('input')
input_args.add_argument('base', help="file name base of system")
input_args.add_argument('-s', '--start', type=int, default=1,
        help="initial frame number")
input_args.add_argument('-e', '--end', type=int, default=np.inf,
        help="final frame number")

# Output arguments
output_args = parser.add_argument_group('output modes')
output_args.add_argument('--show', action="store_true", help="show figures")
output_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
output_args.add_argument('--dpi', default=150, help="output graph dpi")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('--xmax', type=float, default=None, metavar='X')
draw_args.add_argument('--xmin', type=float, default=None, metavar='X')
draw_args.add_argument('--ymax', type=float, default=None, metavar='Y')
draw_args.add_argument('--ymin', type=float, default=None, metavar='Y')
draw_args.add_argument('--axis', default='scaled')
draw_args.add_argument('--colour', default='blue', help="quiver arrow colour")
draw_args.add_argument('--scale', type=float, default=None,
        help="arrow scale for quiver")
draw_args.add_argument('--width', type=float, default=None,
        help="arrow width for quiver")
draw_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
draw_args.add_argument('--temp', action="store_true",
        help="colour flow map with temperature")
draw_args.add_argument('--Tmin', type=float, default=None, metavar='T',
        help="bottom temperature colour at this value")
draw_args.add_argument('--Tmax', type=float, default=None, metavar='T',
        help="top temperature colour at this value")

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Position (nm)')
label_args.add_argument('--ylabel', default='Height (nm)')
label_args.add_argument('--title', default='')

# Parse and control for action
args = parser.parse_args()
if not (args.save or args.show):
    parser.error("at least one of --show or --save has to be specififed")

xlims = [args.xmin, args.xmax]
ylims = [args.ymin, args.ymax]

# Create system
system = System(base = args.base)
system.files(start = args.start, end = args.end)

for frame, _file in enumerate(system.datamaps):

    # If saved figures desired construct filename
    if args.save:
        save = '%s%05d%s' % (args.save, frame + args.start, '.png')
    else:
        save = ''

    datamap = DataMap(_file, min_mass = args.min_mass)
    datamap.flow(
            show = args.show, save = save, dpi = args.dpi,
            temp = args.temp, clim = [args.Tmin, args.Tmax],
            color = args.colour, xlim = xlims, ylim = ylims,
            axis = args.axis,
            width = args.width, scale = args.scale,
            xlabel = args.xlabel, ylabel = args.ylabel, title = args.title
            )
