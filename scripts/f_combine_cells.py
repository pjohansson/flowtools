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
Script for combining cells of data maps.

"""

import argparse
import numpy as np
import os

from flowtools.datamaps import System, DataMap

parser = argparse.ArgumentParser(
        description="Combine cells of data map.")

# Input base arguments
parser.add_argument('-f', '--file', type=str, required=True,
        help="datamap to combine cells of")
parser.add_argument('-o', '--output', type=str, required=True,
        help="output datamap to this file")
parser.add_argument('-n', '--num_cells', type=int, nargs=2, required=True,
        help="combine this many cells in directions corresponding to x and y")
parser.add_argument('-d', '--debug', action='store_true', help="output debug information")

args = parser.parse_args()

data = DataMap(args.file)
combined = data.combine(nx=args.num_cells[0], ny=args.num_cells[1], verbose=args.debug)
combined.save(args.output)


