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
Script for calculating the energy lost due to viscous dissipation
during impact.

"""

import argparse
import numpy as np
import os
import pylab as plt

from flowtools.datamaps import System, DataMap

def calc_slip_dissipation(datamap, floor):
    """
    Calculate the energy dissipated due to slip in current DataMap.
    This slip is calculated as between the active wetting layer, which
    is the layer just above the input floor.

    Returns a value in MD units (kJ*mol-1).

    """

    dissipated_energy = 0
    for column, cell in enumerate(datamap.cells[floor+1]):
        if cell['droplet']:
            try:
                floor_cell = datamap.cells[floor][column]
            except IndexError:
                return 0.

            difference = 0.5*(cell['M']*cell['U']**2
                    - floor_cell['M']*floor_cell['U']**2)
            dissipated_energy += difference

    return dissipated_energy

parser = argparse.ArgumentParser(
        description="Draw a graph of the viscous energy dissipation over time. "
        "Energy is given in MD units (kJ*mol-1).")

# Input base arguments
input_args = parser.add_argument_group('input')
input_args.add_argument('base', help="file name base of system")
input_args.add_argument('-s', '--start', type=int, default=1,
        help="initial frame number")
input_args.add_argument('-e', '--end', type=int, default=np.inf,
        help="final frame number")

# Output arguments
output_args = parser.add_argument_group('output modes')
output_args.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
output_args.add_argument('--noshow', action="store_true",
        help="do not show the graph")
output_args.add_argument('--print', action="store_true",
        help="print energy dissipation to stdout")
output_args.add_argument('--save', default='', metavar='PATH',
        help="save a graph to this path")
output_args.add_argument('--dpi', default=150, type=int, help="output graph dpi")

# Viscosity calculation options
visc_args = parser.add_argument_group("viscous dissipation calculation options")
visc_args.add_argument('--viscosity', '-vv', type=float, default=0.642e-3,
        metavar="VISCOSITY",
        help="droplet viscosity (in Pa*s) used in viscosity dissipation"
        "energy calculation")
visc_args.add_argument('--num_cells', '-N', type=int, default=1,
        metavar="N",
        help="number of cells used in viscosity dissipation energy calculation")
visc_args.add_argument('--width', '-w', type=float, default=1.,
        metavar="WIDTH",
        help="droplet width (in nm) used in viscosity dissipation energy calculation")
visc_args.add_argument('--delta_t', '-dt', type=float, default=1.,
        metavar="DT",
        help="time (in ps) used in viscosity dissipation energy calculation")
visc_args.add_argument('--mass_flow', action='store_true',
        help="use mass flow as basis for viscous dissipation energy calculations")

# Compare with slip dissipation
slip_args = parser.add_argument_group('slip dissipation options',
        "options for calculating the dissipation due to slip for comparison")
slip_args.add_argument('--slip', action='store_true',
        help="compare viscous to slip dissipation, using value of --floor as basis")
slip_args.add_argument('--floor', type=int, default=0,
        help="floor row of cells for slip calculation")

# Options
draw_args = parser.add_argument_group('draw options',
        'options detailing the output graph appearances')
draw_args.add_argument('--xmax', type=float, default=None, metavar='X')
draw_args.add_argument('--xmin', type=float, default=None, metavar='X')
draw_args.add_argument('--ymax', type=float, default=None, metavar='Y')
draw_args.add_argument('--ymin', type=float, default=None, metavar='Y')
draw_args.add_argument('--time_start', '-t0', type=float, default=0.,
        metavar="T", help="set initial time")
draw_args.add_argument('--axis', default='on')

# Decorations
label_args = parser.add_argument_group('label options',
        'pick labels for output figures')
label_args.add_argument('--xlabel', default='Time (ps)')
label_args.add_argument('--ylabel', default='Dissipated energy (kJ/mol)')
label_args.add_argument('--title', default='')

args = parser.parse_args()

xlims = [args.xmin, args.xmax]
ylims = [args.ymin, args.ymax]

times = []
d_visc_energy = []
d_slip_energy = []

# Create system
system = System(base = args.base)
system.files(start = args.start, end = args.end)

for frame, _file in enumerate(system.datamaps):
    datamap = DataMap(_file, min_mass = args.min_mass)

    times.append(frame*args.delta_t)
    d_visc_energy.append(datamap._sum_viscous_dissipation(args.width,
            args.delta_t, args.num_cells, args.viscosity, args.mass_flow))

    if args.slip:
        d_slip_energy.append(calc_slip_dissipation(datamap, args.floor))

times = list(np.array(times) + args.time_start)

if args.print:
    for i, (time, energy) in enumerate(zip(times, d_visc_energy)):
        print(time, energy, end=' ')
        if args.slip:
            print(d_slip_energy[i], end='')
        print()

plt.plot(times, d_visc_energy)

if args.slip:
    plt.hold(True)
    plt.plot(times, d_slip_energy)

plt.axis(args.axis)
plt.xlim(xlims)
plt.ylim(ylims)
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title)

if args.save:
    plt.savefig(args.save, dpi=args.dpi, bbox_inches='tight')

if not args.noshow:
    plt.show()
