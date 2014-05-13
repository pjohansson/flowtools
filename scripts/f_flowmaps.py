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
import pylab as plt
import sys

from flowtools.datamaps import System, DataMap

def draw_colourmap(densmap, quantity, xlims, ylims):
    """
    Draw a colour mesh map of a desired quantity for a given DataMap.

    """

    # Set quantity keyword
    for value, keyword in zip(['mass', 'number', 'temp', 'shear'], ['M', 'N', 'T', 'shear']):
        if quantity == value:
            _type = keyword

    # Initiate empty lists for cell values
    x = []; y = []; values = []

    # Get shape of system
    shape = datamap.cells.T.shape

    # With cells as a flat list, read values for position and quantity
    with DataMap.FlatArray(datamap.cells) as cells:
        for cell in cells:
            x.append(cell['X'])
            y.append(cell['Y'])
            values.append(cell[_type])

    # Draw quantity as 2D histogram for speed
    plt.hist2d(x, y, weights=values, bins=shape, vmin=args.Tmin, vmax=args.Tmax)#, xlim=xlims, ylim=ylims)
    plt.axis(args.axis)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.colorbar()

    if save:
        plt.savefig(save, dpi=args.dpi)

    if args.show:
        plt.show()

    plt.clf()

    return None


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
output_args.add_argument('--type', '-t', default='flow',
        choices=['flow', 'mass', 'number', 'temp', 'shear'],
        help="type of data to draw, 'flow' for a quiver of mass flow, "
            "or using 'mass', 'number' (of atoms), 'temp', 'shear' for colour meshes"
            "of those respective quantities")
output_args.add_argument('--noshow', action="store_false", dest='show',
        help="do not display figures")
output_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
output_args.add_argument('--dpi', default=150, type=int, help="output graph dpi")
output_args.add_argument('--transparent', '-trans', action='store_true',
        help="save image with transparent background")
output_args.add_argument('--noaxis', action='store_true',
        help="output without axis")

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
draw_args.add_argument('--shear_numcells', '-sn', type=int, default=1,
        metavar='N', help="number of cells to take finite difference over for "
        "shear calculation")
draw_args.add_argument('--shear_massflow', action='store_true',
        help="use mass flow when calculation shear in cells")
draw_args.add_argument('--quiet', '-q', action='store_true',
        help="talk less")

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Position (nm)')
label_args.add_argument('--ylabel', default='Height (nm)')
label_args.add_argument('--title', default='')

# Parse and control for action
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


    if not args.quiet:
        print("\rReading %s (%d of %d) ... " % (_file, frame+1, len(system.datamaps)), end='')
        sys.stdout.flush()

    datamap = DataMap(_file, min_mass = args.min_mass)

    if not args.quiet:
        print("Done!", end='')

    if args.type == 'flow':
        datamap.flow(
                show = args.show, save = save, dpi = args.dpi, transparent = args.transparent,
                temp = args.temp, clim = [args.Tmin, args.Tmax],
                color = args.colour, xlim = xlims, ylim = ylims,
                axis = args.axis, noaxis = args.noaxis,
                width = args.width, scale = args.scale,
                xlabel = args.xlabel, ylabel = args.ylabel, title = args.title
                )
    else:
        if args.type == 'shear':
            datamap._calc_cell_shear(args.shear_numcells, args.shear_massflow)
        draw_colourmap(datamap, args.type, xlims, ylims)

if not args.quiet:
    print()
