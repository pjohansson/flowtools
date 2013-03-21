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
import pylab as plt
import sys

from flowtools.datamaps import Spread
from pandas import Series, DataFrame

def combine_spread(spread_files, shift, plot=False, **kwargs):
    """
    Combine the spread of input files, return with mean and standard
    deviation calculated.

    """

    values = {}
    for val in ('left', 'right', 'com', 'dist'):
        values[val] = {}

    # Collect data from all files into dictionaries
    for i, _file in enumerate(spread_files):
        data = Spread().read(_file)
        for val in values.keys():
            values[val][i] = Series(
                    data=data.spread[val]['val'],
                    index=data.times
                    )

        # If not drawing mean, draw individual graphs
        if plot:
            data.times = list(np.array(data.times) - shift[i])
            if i > 0:
                kwargs.update({'label': '_nolegend_'})
            data.plot(**kwargs)

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

        # Get times, mean and standard error as lists
        mean = list(df.mean(axis=1))
        std_error = list(df.std(axis=1))
        times = list(df.index)

        # Add to Spread object
        spread.spread[val]['val'] = mean
        spread.spread[val]['std_error'] = std_error
        spread.spread['times'] = times

    return spread

if __name__ == '__main__':
    def get_colours(args):
        """Create list of colours for lines."""

        colours = args.colour.copy()
        default = [
                'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'
                ]

        while len(colours) < len(args.spreading):
            colours += default
        colours = colours[:len(args.spreading)]

        return colours

    def get_labels(args):
        """Create list of labels for legend."""

        labels = args.label.copy()

        default = ['_nolegend_']
        while len(labels) < len(args.spreading):
            labels += default

        # Check if legend required
        if set(labels) == set(['_nolegend_']):
            legend = False
        else:
            legend = True

        return labels, legend

    def get_linestyles(args):
        """Create lists of line styles."""

        linestyles = args.linestyle.copy()
        error_linestyles = args.errorstyle.copy()

        default = ['solid']
        while len(linestyles) < len(args.spreading):
            linestyles += default

        default = ['dashed']
        while len(error_linestyles) < len(args.spreading):
            error_linestyles += default

        return linestyles, error_linestyles

    def get_shift(spread_files_array, sync='none'):
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

    def get_plotkwargs(kwargs, args):
        """Modify plot option keywords."""

        plotkwargs = args.linekwargs.copy()
        while plotkwargs:
            value = plotkwargs.pop()
            keyword = plotkwargs.pop()
            kwargs.update({keyword: value})

        return None

    def get_savekwargs(kwargs, args):
        """Modify plot option keywords."""

        savekwargs = args.savekwargs.copy()
        while savekwargs:
            value = savekwargs.pop()
            keyword = savekwargs.pop()
            kwargs.update({keyword: value})

        return None


    # Get input files and options
    parser = argparse.ArgumentParser()

    line = parser.add_argument_group(title="Main")
    line.add_argument('-f', '--files', dest='spreading', action='append',
            nargs='+', metavar="FILES", required=True,
            help="list of spreading data files to graph")
    line.add_argument('-s', '--save', metavar="PATH",
            help="optionally save output image to path")
    line_show = line.add_mutually_exclusive_group()
    line_show.add_argument('--show', action='store_true', dest='show',
            default=True,
            help=("show graph (default: true, --noshow to turn off)"))
    line_show.add_argument('--noshow', action='store_false', dest='show',
            help=argparse.SUPPRESS)

    # Create mutually exclusive group for plot type
    graph = parser.add_argument_group(title="Graph type",
            description="choice of plotting droplet edge positions or radius, "
                    "and modifying domain")
    graph.add_argument('--nomean', action='store_true',
            help="don't draw the mean of the spread, but individual lines")
    _line = graph.add_mutually_exclusive_group()
    _line.add_argument('--com_edges', dest='line', action='store_const',
            const='com_edges', default='com_edges',
            help="draw edges from center of mass (default)")
    _line.add_argument('--radius', dest='line', action='store_const',
            const='radius', help="total radius of spread")
    sync = graph.add_mutually_exclusive_group()
    sync.add_argument('--dist', action='store_const', const='com',
            dest='sync', help="for time and frame graphs, set start at impact")
    sync.add_argument('--relative', action='store_const', const='impact',
            dest='sync', default='none',
            help="for time and frame graphs, set start at impact")

    # Error plotting
    error = parser.add_argument_group(title="Error",
            description="options for error of data")
    error_group = error.add_mutually_exclusive_group()
    error_group.add_argument('--error', action='store_true', dest='error',
            default=True,
            help=("show error for lines if multiple files entered "
                    "(default: true, --noerror to turn off)"))
    error_group.add_argument('--noerror', action='store_false', dest='error',
            help=argparse.SUPPRESS)
    error.add_argument('--sigma', type=float, default=1.,
            help="number of standard deviations from mean, or Z-score, "
                    "for error lines (default: 1)")

    # Decoration options
    decoration = parser.add_argument_group(title="Graph decoration",
            description="options for decorating the graph")
    decoration.add_argument('-c', '--colour', action='append', default=[],
            help="line colour, add once per line")
    decoration.add_argument('-l', '--label', action='append', default=[],
            help="line label, add once per line")
    decoration.add_argument('--linestyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot'],
            help="line style (default: solid)")
    decoration.add_argument('--errorstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot'],
            help="error line style (default: dashed)")
    decoration.add_argument('--title', default='', help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL", default='',
            help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL", default='',
            help="label of y axis")

    # Advanced options
    kwargs_opts = parser.add_argument_group(title="Keywords",
            description="additional keyword arguments for advanced options")
    kwargs_opts.add_argument('--linekwargs', nargs='*', default=[],
            metavar="KEYWORD VALUE",
            help="add any plot keyword and arguments")
    kwargs_opts.add_argument('--savekwargs', nargs='*', default=[],
            metavar="KEYWORD VALUE",
            help="add any savefig keyword and arguments")

    # Parse arguments
    args = parser.parse_args()

    # Get colours, labels and line styles from default
    colours = get_colours(args)
    labels, legend = get_labels(args)
    linestyles, errorstyles = get_linestyles(args)

    # Create option keywords for title, etc.
    kwargs = {}
    for name, opt in (
            ('title', args.title), ('xlabel', args.xlabel),
            ('ylabel', args.ylabel)
            ):
        if opt:
            kwargs.setdefault(name, opt)

    # Get additional plot keywords
    try:
        get_plotkwargs(kwargs, args)
    except IndexError:
        parser.error("non-complete keyword-value argument in --linekwargs")

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync)

    # Plot lines for all file lists
    for i, spread_list in enumerate(args.spreading):
        # Update kwargs for line styles
        kwargs.update({'linestyle': linestyles[i]})
        kwargs.update({'linestyle_error': errorstyles[i]})

        spread = combine_spread(spread_list, shift=shift_array[i],
                plot=args.nomean, color=colours[i], label=labels[i], **kwargs)

        # Check if error bars need to be included
        error = args.error and len(spread_list) > 1

        # Create graph
        spread.plot(error=error, color=colours[i], label=labels[i],
                sigma=args.sigma, noline=args.nomean, **kwargs)

    # Finish with decorations and output options
    if legend:
        plt.legend()

    if args.save:
        kwargs = {}
        get_savekwargs(kwargs, args)
        plt.savefig(args.save, dpi=args.dpi, **kwargs)

    if args.show:
        plt.show()
