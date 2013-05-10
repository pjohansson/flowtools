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
Script for printing flow maps to stdout.

"""

import argparse
import numpy as np
import os

from flowtools.datamaps import System, DataMap

parser = argparse.ArgumentParser(
        description="Print data from maps.")

# Input base arguments
parser.add_argument('datamap', nargs='+',
        help="file name base of system")
parser.add_argument('--droplet', action='store_true',
        help="filter cells that are part of main droplet (default: false), optionally supply a minimum mass for filtering using '-m'")
parser.add_argument('-m', '--min_mass', type=float, default=0.,
        metavar='MASS', help="minimum mass of cell to include")

args = parser.parse_args()

for i, _file in enumerate(args.datamap):
    if len(args.datamap) > 1:
        print('%s:' % _file)

    datamap = DataMap(_file, min_mass = args.min_mass)
    datamap.print(droplet=args.droplet)

    if len(args.datamap) > 1 and i < len(args.datamap) - 1:
        print()
