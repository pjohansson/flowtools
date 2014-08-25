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
import sys

from flowtools.datamaps import System, DataMap

def contact_line_velocity(frames, delta_t):
    """
    Find mean contact line velocities of frames, return as (left, right)
    tuple.

    """

    def find_edge(cells, iadd):
        i = min(0, iadd)
        while not t0_cells[i]['droplet']:
            i = i+iadd
        return cells[i]['X']

    t0_cells = frames[0][-1]['cells']
    t1_cells = frames[-1][-1]['cells']

    time = len(frames)*delta_t
    left = (find_edge(t1_cells, 1) - find_edge(t0_cells, 1))/time
    right = (find_edge(t1_cells, -1) - find_edge(t0_cells, -1))/time

    return (left, right)

def adjust_velocity(cells, cl_velocities):
    """
    Adjust the cell velocities by substracting contact line velocities.

    """

    middle = int(len(cells[0]['cells'])/2)
    for row in cells:
        for col in row['cells'][:middle]:
            col['U'] = col['U'] - cl_velocities[0]
        for col in row['cells'][middle:]:
            col['U'] = col['U'] - cl_velocities[1]

    return None

def avg_frames(frames):
    """
    Average data from all frames into one.

    """

    cells = frames[0].copy()
    num = np.zeros([2*args.num_cells[0], args.num_cells[1]])

    for n, frame in enumerate(frames):
        for i, row in enumerate(frame):
            for j, cell in enumerate(row['cells']):
                avgd = cells[i]['cells'][j]
                if cell['droplet']:
                    N = num[j][i]
                    oldM = avgd['M']
                    avgd['M'] = (N*avgd['M'] + cell['M'])/(N+1)
                    avgd['N'] = (N*avgd['N'] + cell['N'])/(N+1)
                    avgd['U'] = (N*oldM*avgd['U'] + cell['M']*cell['U'])/(avgd['M']*(N+1))
                    avgd['V'] = (N*oldM*avgd['V'] + cell['M']*cell['V'])/(avgd['M']*(N+1))
                    avgd['T'] = (N*oldM*avgd['T'] + cell['M']*cell['T'])/(avgd['M']*(N+1))
                    num[j][i] = num[j][i] + 1

    return cells

def add_row(cells, columns, data):
    """
    Returns data from specified columns of a row.

    Appends output data to 'data' list for statistics analysis.

    """

    def add_columns(cells, columns, data):
        """
        Add columns to row.

        """

        row = []

        for col in columns:
            cell = {}
            cell = cells[col]

            if cells[col]['droplet']:
                data.append(cells[col][var[0]])

            row.append(cell.copy())

        return row

    row = {}
    row['Y'] = cells[0]['Y']
    row['cells'] = add_columns(cells, columns, data)

    return row

def print_cells(cells):
    """
    Prints one formatted row of cells around the contact line
    of the chosen data type.

    """

    def print_columns(columns):
        """
        Print chosen data type of specified columns in cell row.

        """

        def to_nmns(nmps):
            return (10**3)*nmps

        length = 9 + (len(var)-1)*11
        strlen = "%c%d%c" % ('%', length, 's')
        if args.type in ['flow', 'U', 'V']:
            valtype = "%.3f"
        elif args.type == 'shear':
            valtype = "%8.3g"
        else:
            valtype = "%8.3f"

        for col in columns:
            buf = ""
            for i, v in enumerate(var):
                if col['droplet']:
                    if i > 0:
                        buf = buf + " "
                    value = col[v]
                    if args.type in ['flow', 'U', 'V']:
                        value = to_nmns(value)
                    buf = buf + valtype % value
            if len(var) > 1:
                buf = '(' + buf + ')'
            print(strlen % buf, end='')

        return None

    def print_height(height):
        print("%8.3f |" % height, end='')
        return None

    for row in cells:
        if args.header:
            print_height(row['Y'])

        print_columns(row['cells'][:int(len(row['cells'])/2)])
        if print_separator:
            print("    ...   ", end='')
        print_columns(row['cells'][int(len(row['cells'])/2):])
        print()

        if args.header and args.sparse:
            print("%8s |" % ' ')

    return None

def get_columns(edge):
    """
    Return a list of cell columns to print, removing duplicates.

    """

    columns = {
            'left': range(edge['left'], edge['left']+args.num_cells[0]),
            'right': range(edge['right']-args.num_cells[0]+1, edge['right']+1)
            }

    # Transfer column lists to set to remove duplicates
    column_set = set([
        col for key in columns.keys() for col in columns[key]
        ])

    return sorted(column_set)

def print_positions(cells, cells_other=[]):
    """
    Print the position of columns along x, including header.

    """

    def print_footer(num_columns):
        print("%8s |" % "Y (nm)")

        num = num_columns*(9 + (len(var)-1)*11) + 10
        if print_separator:
            num = num + 10
        for _ in range(num):
            print("-", end='')
        print()

        return None

    print_footer(len(cells[0]['cells']))
    print("%8s  " % "X (nm)", end='')

    num_cells = int(len(cells[0]['cells'])/2)
    row = cells[0]['cells']

    # Print positions left and right of a probable separator
    for i, col in enumerate(row[:num_cells]):
        for _ in range(len(var)-1):
            print("%11s" % '', end='')

        # If position range is to be printed, create buffer and print in one
        if not cells_other:
            print(" %8.3f" % col['X'], end='')
        else:
            print("\b\b\b\b\b\b\b\b\b\b\b", end='')
            buf = "(%.3f-%.3f)" % (col['X'], cells_other[0]['cells'][i]['X'])
            print("%20s" % buf, end='')

    if print_separator:
        print("    ...   ", end='')

    # Repeat for other side of separator
    for i, col in enumerate(row[num_cells:]):
        for _ in range(len(var)-1):
            print("%11s" % '', end='')
        if not cells_other:
            print(" %8.3f" % col['X'], end='')
        else:
            print("\b\b\b\b\b\b\b\b\b\b\b", end='')
            buf = "(%.3f-%.3f)" % (col['X'], cells_other[0]['cells'][num_cells+i]['X'])
            print("%20s" % buf, end='')
    print()

    return None

def to_print_separator(columns):
    """
    Return True if separator needs to be printed in output.

    """

    for i in range(len(columns)-1):
        if (columns[i+1] - columns[i]) != 1:
            return True

    return False

def do_analysis(data, datamap):
    """
    Perform some statistics analysis on contact line data.

    """

    print("contact line: mean = %8.4g" % np.mean(data), end=' ')
    if args.type == 'temp':
        print("(K)", end='   ')
    elif args.type == 'shear':
        print("(1/ps)", end='   ')

    print("stdev = %8.4g" % np.std(data), end='   ')
    print("stderr = %8.4g" % (np.std(data)/np.sqrt(len(data))))

    system = datamap.mean(var[0])
    print("      system: mean = %8.4g" % system['mean'], end=' ')
    if args.type == 'temp':
        print("(K)", end='   ')
    elif args.type == 'shear':
        print("(1/ps)", end='   ')

    print("stdev = %8.4g" % system['stdev'], end='   ')
    print("stderr = %8.4g" % system['stderr'])

    return None

parser = argparse.ArgumentParser(
        description="Draw graphs of the flow in data maps.")

# Input base arguments
parser.add_argument('base', nargs='?', default=None,
        help="file name base of system, combine with --start "
            "and --end to work on range of maps using this base")
parser.add_argument('-f', '--file', help="specific file to work on")
parser.add_argument('-b', '--begin', type=int, default=1,
        help="initial frame number")
parser.add_argument('-e', '--end', type=int, default=np.inf,
        help="final frame number")
parser.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")
parser.add_argument('-n', '--num_cells', type=int, nargs=2, default=[1,1],
        help="display data for this many cells in x and y respectively"
        "around the contact line")
parser.add_argument('--type', '-t', default='temp',
        choices=['shear', 'temp', 'flow', 'U', 'V', 'M', 'N', 'T'],
        help="work on this data for output (default: temp), mass flow is"
        "in units of nm/ns, NOT nm/ps")
parser.add_argument('--shear_numcells', '-sn', type=int, default=1,
        help="number of cells to take finite difference over when calculating"
        "velocity for shear calculation")
parser.add_argument('--shear_remove_edges', action='store_true',
        help="remove edge cells of shear droplets, excluded from finite cell"
        "difference calculations")
parser.add_argument('--statistics', action='store_true',
        help="output statistics on contact line data")
parser.add_argument('--sparse', action='store_true',
        help="sparse output")
parser.add_argument('-avg', '--average', action='store_true',
        help="average data from all frames")
parser.add_argument('-vadj', '--adjust_velocity', action='store_true',
        help="remove averaged contact line velocity from flow velocity")
parser.add_argument('-dt', '--delta_t', type=float, default=10.,
        help="time between frames in ps (default: 10)")
parser.add_argument('--noheaders', action='store_false', dest='header',
        help="do not output position and height headers")
parser.add_argument('--nooutput', action='store_false', dest='do_output',
        help="do not output cells")

# Parse and control for action
args = parser.parse_args()

# If base given, create system
if args.base != None:
    system = System(base = args.base)
    system.files(start = args.begin, end = args.end)

else:
    system = System()
    system.datamaps = [args.file]

if args.average:
    args.do_output = False

var = []
if args.type == 'temp':
    var.append('T')
elif args.type == 'flow':
    var.append('U')
    var.append('V')
else:
    var.append(args.type)

frames = []
for frame, _file in enumerate(system.datamaps):
    cells = []
    if args.average and len(system.datamaps) > 1:
        print("\rReading %s (%d of %d) ... " % (_file, frame+1, len(system.datamaps)), end='')
        sys.stdout.flush()

    elif len(system.datamaps) > 1:
        print("\n==> %s <==" % _file)

    datamap = DataMap(_file, min_mass = args.min_mass)

    if args.type == 'shear':
        datamap._calc_cell_shear(args.shear_numcells, mass_flow=False,
                if_droplet=args.shear_remove_edges)

    interface = datamap.interface(get_cell_numbers=True)
    floor = interface[0][1]
    ceil = floor + args.num_cells[1] - 1

    edge = {'left': interface[0][0], 'right': interface[-1][0]}
    columns = get_columns(edge)
    print_separator = to_print_separator(columns)

    data = []

    for row in range(ceil, floor-1, -1):
        cells.append(add_row(datamap.cells[row], columns, data))
    frames.append(cells)

    if args.do_output:
        print_cells(cells)

    if args.do_output and args.header:
        print_positions(cells)

    if args.statistics:
        do_analysis(data, datamap)

if args.do_output or len(system.datamaps) > 1:
    print()

if args.average:
    # Average frames
    cells = avg_frames(frames)

    # Adjust velocities into contact line frame of view if desired
    if args.adjust_velocity:
        cl_velocity = contact_line_velocity(frames, args.delta_t)
        adjust_velocity(cells, cl_velocity)

    # Output
    print_cells(cells)
    if args.header:
        print_positions(frames[-1], frames[0])
