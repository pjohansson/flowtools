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
including the standard deviation.

"""

import argparse
import numpy as np
import sys

from flowtools.datamaps import Spread
from pandas import Series, DataFrame

parser = argparse.ArgumentParser()

parser.add_argument('--save', metavar="PATH", help="save combined data to file")
parser.add_argument('spreading', nargs='+',
        help="list of spreading data files to combine")

args = parser.parse_args()

impact_list = []
min_mass_list = []

left = {}
right = {}
com_left = {}
com_right = {}
dist = {}

# Read spread info from all files into dictionaries
for i, _file in enumerate(args.spreading):
    spread = Spread().read(_file)

    # Save curricular data
    impact_list.append(spread.impact * spread.delta_t)
    min_mass_list.append(spread.min_mass)

    left[i] = Series(spread.left, index = spread.times)
    right[i] = Series(spread.right, index = spread.times)
    com_left[i] = Series(spread.com['left'], index = spread.times)
    com_right[i] = Series(spread.com['right'], index = spread.times)
    dist[i] = Series(spread.dist, index = spread.times)

impact_time = np.array(impact_list).mean()
min_mass = max(min_mass_list)
variables = {
        'left': left, 'right': right,
        'com_left': com_left, 'com_right': com_right, 'dist': dist
        }

for var, series_data in variables.items():
    # Adjust impact times to mean
    for series in series_data.values():
        shift = series.index[0] - impact_time
        series.index -= shift

    # Convert to DataFrames and keep only full rows
    variables[var] = DataFrame(series_data).dropna(0)

    # Take mean and get standard deviation
    mean, std = variables[var].mean(1), variables[var].std(1)
    variables[var]['mean'] = mean
    variables[var]['std'] = std

# Add to new Spread data
delta_t = variables['left'].index[1] - variables['left'].index[0]
spread = Spread(delta_t = delta_t, min_mass = min_mass)

spread.left = variables['left']['mean'].tolist()
spread.right = variables['right']['mean'].tolist()
spread.com['left'] = variables['com_left']['mean'].tolist()
spread.com['right'] = variables['com_right']['mean'].tolist()
spread.dist = variables['dist']['mean'].tolist()

spread.times = list(variables['left'].index)
spread.frames = list(map(int, variables['left'].index / delta_t))

print(len(spread.times), len(spread.left))

spread.plot(times = True, show = True, axis = 'normal')

