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
Script for combining spread data from files and saving to a new one,
including the error.

"""

import argparse
import sys

from flowtools.datamaps import Spread
from pandas import Series, DataFrame

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--save', required=True,
        help="save combined data to file")
parser.add_argument('spreading', nargs='+',
        help="list of spreading data files to combine")

args = parser.parse_args()

left = {}
right = DataFrame()
com_left = DataFrame()
com_right = DataFrame()
dist = DataFrame()

for i, _file in enumerate(args.spreading):
    spread = Spread().read(_file)

    left[i] = Series(spread.left, index = spread.times)
    right[i] = Series(spread.right, index = spread.times)
    com_left[i] = Series(spread.com['left'], index = spread.times)
    com_right[i] = Series(spread.com['right'], index = spread.times)
    dist[i] = Series(spread.dist, index = spread.times)

left = DataFrame(left).mean
right = DataFrame(right)
com_left = DataFrame(com_left)
com_right = DataFrame(com_right)
dist = DataFrame(dist)

print(left)
