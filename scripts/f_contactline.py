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

def print_row(cells, columns, data):
    """
    Prints one formatted row of cells around the contact line
    of the chosen data type.

    Appends output data to 'data' list for statistics analysis.

    """

    def print_columns(cells, columns, data):
        """
        Print chosen data type of specified columns in cell row.

        """

        for col in columns:
            if cells[col]['droplet']:
                data.append(cells[col][var])
                print(" %8g" % cells[col][var], end='')
            else:
                print(" %8s" % '', end='')

        return None

    def print_height(cells):
        print("%8g |" % cells[0]['Y'], end='')

    if args.header:
        print_height(cells)

    print_columns(cells, columns[:int(len(columns)/2)], data)
    if print_separator:
        print("    ...   ", end='')
    print_columns(cells, columns[int(len(columns)/2):], data)
    print()

    if args.sparse:
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

def print_positions(cells, columns):
    """
    Print the position of columns along x, including header.

    """

    def print_footer(columns):
        print("%8s |" % "Y (nm)")
        print("----------", end='')
        for col in columns[:int(len(columns)/2)]:
            print("---------", end='')
        if print_separator:
            print("----------", end='')
        for col in columns[int(len(columns)/2):]:
            print("---------", end='')
        print()

        return None

    print_footer(columns)
    print("%8s  " % "X (nm)", end='')
    for col in columns[:int(len(columns)/2)]:
        print(" %8g" % cells[col]['X'], end='')
    if print_separator:
        print("    ...   ", end='')
    for col in columns[int(len(columns)/2):]:
        print(" %8g" % cells[col]['X'], end='')
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

def do_analysis(data):
    """
    Perform some statistics analysis on contact line data.

    """

    print("mean: %g" % np.mean(data), end=' ')
    if args.type == 'temp':
        print("(K)", end='   ')
    elif args.type == 'shear':
        print("(1/ps)", end='   ')

    print("stdev: %g" % np.std(data), end='   ')
    print("stderr: %g" % (np.std(data)/np.sqrt(len(data))), end='   ')

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
        choices=['shear', 'temp'],
        help="work on this data for output (default: temp)")
parser.add_argument('--statistics', action='store_true',
        help="output statistics on contact line data")
parser.add_argument('--sparse', action='store_true',
        help="sparse output")
parser.add_argument('--noheaders', action='store_false', dest='header',
        help="do not output position and height headers")

# Parse and control for action
args = parser.parse_args()

# If base given, create system
if args.base != None:
    system = System(base = args.base)
    system.files(start = args.begin, end = args.end)

else:
    system = System()
    system.datamaps = [args.file]

if args.type == 'temp':
    var = 'T'
elif args.type == 'shear':
    var = 'shear'


for frame, _file in enumerate(system.datamaps):
    if len(system.datamaps) > 1:
        print("\n==> %s <==" % _file)

    datamap = DataMap(_file, min_mass = args.min_mass)

    interface = datamap.interface(get_cell_numbers=True)
    floor = interface[0][1]
    ceil = floor + args.num_cells[1] - 1

    edge = {'left': interface[0][0], 'right': interface[-1][0]}
    columns = get_columns(edge)
    print_separator = to_print_separator(columns)

    data = []

    for row in range(ceil, floor-1, -1):
        print_row(datamap.cells[row], columns, data)

    if args.header:
        print_positions(datamap.cells[row], columns)

    if args.statistics:
        do_analysis(data)

print()
