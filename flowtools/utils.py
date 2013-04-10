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
Utilities for scripting flow tools.

Functions:
    calc_radius - calculate the radius as a droplet spreads
    combine_spread - combine the spread of several data files to a single with
        errors and what not
    get_colours - get input colours from a default list
    get_labels - get labels for legend
    get_linestyles - get line styles for plot
    get_shift - find a time shift for a given synchronisation

"""

from flowtools.datamaps import Spread
from pandas import DataFrame, Series

import numpy as np

def calc_radius(spread, error=False):
    """
    Calculate and return a list of radius.

    Supply error=True to return tuple of radius and error values.

    """
    radius = list((np.array(spread.right) - np.array(spread.left)) / 2)
    if not error:
        return radius
    else:
        std_error = {'left': [], 'right': []}
        for key in std_error.keys():
            std_error[key] = np.array(spread.spread[key]['std_error'])**2
        return radius, np.sqrt(std_error['right'] + std_error['left'])

def combine_spread(spread_files, shift, drop_return_data=False):
    """
    Combine the spread of input files, return with mean and standard
    deviation calculated.

    """

    data = []
    values = {}
    for val in ('left', 'right', 'com', 'dist'):
        values[val] = {}

    # Collect data from all files into dictionaries
    for i, _file in enumerate(spread_files):
        data.append(Spread().read(_file))
        for val in values.keys():
            values[val][i] = Series(
                    data=data[i].spread[val]['val'],
                    index=data[i].times
                    )
        data[i].times = (np.array(data[i].times) - shift[i])

    spread = Spread()

    for val in values.keys():

        # Shift time as per synchronisation
        for i in values[val]:
            values[val][i].index = np.array(values[val][i].index) - shift[i]

        # Convert to DataFrame
        df = DataFrame(data=values[val])

        # If not a single file, keep only indices with at least two non-NaN
        if len(spread_files) > 1:
            df = df.dropna()

        # If return data dropped, fill data here
        if drop_return_data:
            for i in df.columns:
                data[i].spread[val]['val'] = df[i].tolist()

        # Get times, mean and standard error as lists
        mean = list(df.mean(axis=1))
        std_error = list(df.std(axis=1))
        times = list(df.index)

        # Add to Spread object
        spread.spread[val]['val'] = mean
        spread.spread[val]['std_error'] = std_error
        spread.spread['times'] = times

    return spread, data

def get_colours(colours, num_lines):
    """Create list of colours for lines from default cycle."""

    default = (
            'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'
            )

    while len(colours) < num_lines:
        colours += default
    colours = colours[:num_lines]

    return colours

def get_labels(labels, num_lines):
    """Create list of labels for legend."""

    default = '_nolegend_'
    while len(labels) < num_lines:
        labels += [default]

    # Check if legend required
    if set(labels) == set(['_nolegend_']):
        draw_legend = False
    else:
        draw_legend = True

    return labels, draw_legend

def get_linestyles(linestyles, num_lines, default='solid'):
    """Create lists of line styles."""

    # If available, use last linestyle as default
    if linestyles:
        default = linestyles[-1]

    while len(linestyles) < num_lines:
        linestyles += [default]

    return linestyles

def get_shift(spread_files_array, sync=None):
    """
    Calculate the desired time shift for synchronisation, return as array
    with time shift values corresponding to file name positions.

    """

    # If common center of mass for synchronisation desired, find minimum
    if sync == 'com':
        min_dist = np.inf
        for spread_files in spread_files_array:
            for _file in spread_files:
                data = Spread().read(_file)
                if data.dist[0] < min_dist:
                    min_dist = data.dist[0]

    # Find shift array depending on synchronisation
    shift_array = []
    for i, spread_files in enumerate(spread_files_array):
        shift_array.append([])
        for _file in spread_files:
            data = Spread().read(_file)

            if sync == 'impact':
                shift = data.times[0]

            elif sync == 'com':
                j = 0
                while data.dist[j] > min_dist:
                    j += 1
                shift = data.times[j]

            else:
                shift = 0.

            shift_array[i].append(shift)

    return shift_array
