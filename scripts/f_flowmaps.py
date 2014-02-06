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

from flowtools.datamaps import System, DataMap
from matplotlib.colors import LogNorm, Normalize

def draw_colourmap(densmap, quantity, xlims, ylims):
    """
    Draw a colour mesh map of a desired quantity for a given DataMap.

    """

    # Set quantity keyword
    for value, keyword in zip(['mass', 'number', 'temp', 'visc'],
            ['M', 'N', 'T', 'visc_dissipation']):
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
    plt.hist2d(x, y, weights=values, bins=shape, norm=normalise)
    plt.axis(args.axis)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.colorbar()
    plt.show()
#                axis = args.axis,

    return None

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
output_args.add_argument('--type', '-t', default='flow',
        choices=['flow', 'mass', 'number', 'temp', 'visc'],
        help="type of data to draw, 'flow' for a quiver of mass flow, "
            "or using 'mass', 'number' (of atoms), 'temp' for colour meshes"
            "of those respective quantities")
output_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
output_args.add_argument('--noshow', action="store_true", help="show figures")
output_args.add_argument('--save', default='', metavar='PATH',
        help="save images to this file base, conserving frame numbers")
output_args.add_argument('--dpi', default=150, type=int, help="output graph dpi")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('--xmax', type=float, default=None, metavar='X')
draw_args.add_argument('--xmin', type=float, default=None, metavar='X')
draw_args.add_argument('--ymax', type=float, default=None, metavar='Y')
draw_args.add_argument('--ymin', type=float, default=None, metavar='Y')
draw_args.add_argument('--axis', default='scaled')

# Flow options
flow_args = parser.add_argument_group('flow drawing options',
        "options detailing the output of mass flow graphs")
flow_args.add_argument('--colour', default='blue', help="quiver arrow colour")
flow_args.add_argument('--scale', type=float, default=None,
        help="arrow scale for quiver")
flow_args.add_argument('--width', type=float, default=None,
        help="arrow width for quiver")
flow_args.add_argument('--temp', action="store_true",
        help="colour flow map with temperature")
flow_args.add_argument('--Tmin', type=float, default=None, metavar='T',
        help="bottom temperature colour at this value")
flow_args.add_argument('--Tmax', type=float, default=None, metavar='T',
        help="top temperature colour at this value")

# Colour map options
map_args = parser.add_argument_group('colour map drawing options',
        "options detailing the output of colour maps (see also --Tmin and --Tmax)")
map_args.add_argument('--log', action='store_true',
        help="output the log of height map values")
map_args.add_argument('--viscosity', '-vv', type=float, default=0.642e-3,
        help="droplet viscosity used in viscosity dissipation energy calculation")
map_args.add_argument('--visc_num_cells', '-vN', type=int, default=1,
        help="number of cells used in viscosity dissipation energy calculation")
map_args.add_argument('--visc_width', '-vw', type=float, default=1.,
        help="droplet width used in viscosity dissipation energy calculation")
map_args.add_argument('--visc_delta_t', '-vt', type=float, default=1.,
        help="time used in viscosity dissipation energy calculation")

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Position (nm)')
label_args.add_argument('--ylabel', default='Height (nm)')
label_args.add_argument('--title', default='')

# Parse and control for action
args = parser.parse_args()
if args.noshow and not args.save:
    parser.error("at least one of --show or --save has to be specififed")

xlims = [args.xmin, args.xmax]
ylims = [args.ymin, args.ymax]

if args.log:
    normalise = LogNorm(vmin=args.Tmin, vmax=args.Tmax)
else:
    normalise = Normalize(vmin=args.Tmin, vmax=args.Tmax)

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
    if args.type == 'flow':
        datamap.flow(
                show = args.show, save = save, dpi = args.dpi,
                temp = args.temp, clim = [args.Tmin, args.Tmax],
                color = args.colour, xlim = xlims, ylim = ylims,
                axis = args.axis,
                width = args.width, scale = args.scale,
                xlabel = args.xlabel, ylabel = args.ylabel, title = args.title
                )
    else:
        if args.type == 'visc':
            datamap._calc_viscous_dissipation(args.visc_num_cells, args.viscosity, args.visc_width, args.visc_delta_t)
        draw_colourmap(datamap, args.type, xlims, ylims)
