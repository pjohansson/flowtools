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

def combine_spread(spread_files, plot=False, **kwargs):
    """
    Combine the spread of input files, return with mean and standard
    deviation calculated.

    """

    impact_list = []
    min_mass_list = []

    left = {}
    right = {}
    com_left = {}
    com_right = {}
    dist = {}

    # Read spread info from all files into dictionaries
    for i, _file in enumerate(spread_files):
        spread = Spread().read(_file)

        # Plot if desired
        if plot:
            label = kwargs.pop('label', '_nolegend_')
            spread.plot(label=label, **kwargs)

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
            'com_left': com_left, 'com_right': com_right,
            'dist': dist
            }

    for var, series_data in variables.items():
        # Adjust impact times to mean
        for series in series_data.values():
            shift = series.index[0] - impact_time
            series.index -= shift

        # Convert to DataFrames and keep only full rows
        variables[var] = DataFrame(series_data).dropna(0)

        # Take mean and get standard error
        mean = variables[var].mean(1)
        std_error = np.sqrt(
                (variables[var].sub(mean, axis='index')**2).mean(1)
                / len(spread_files)
                )
        variables[var]['mean'] = mean
        variables[var]['std_error'] = std_error

    delta_t = variables['left'].index[1] - variables['left'].index[0]

    spread = Spread(delta_t = delta_t, min_mass = min_mass)

    spread.left = variables['left']['mean'].tolist()
    spread.spread['left']['com'] = variables['com_left']['mean'].tolist()
    spread.spread['left']['std_error'] = variables['left']['std_error'].tolist()
    spread.right = variables['right']['mean'].tolist()
    spread.spread['right']['com'] = variables['com_right']['mean'].tolist()
    spread.spread['right']['std_error'] \
            = variables['right']['std_error'].tolist()

    spread.dist = variables['dist']['mean'].tolist()
    spread.times = list(variables['left'].index)
    spread.frames = list(map(int, variables['left'].index / delta_t))

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
    line.add_argument('--nomean', action='store_true',
            help="don't draw the mean of the spread, but individual lines")

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
            help="line style, add once per line (default: solid)")
    decoration.add_argument('--errorstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot'],
            help="error line style, add once per line (default: dashed)")
    decoration.add_argument('--title', default='', help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL", default='',
            help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL", default='',
            help="label of y axis")

    # Create mutually exclusive group for plot type
    type_group = parser.add_argument_group(title="Graph type",
            description="choice of metric for spreading, default is time")
    _type = type_group.add_mutually_exclusive_group()
    _type.add_argument('--time', dest='type', action='store_const',
            const='times', default='times',
            help="graph as a function of time")
    _type.add_argument('--dist', dest='type', action='store_const',
            const='dist', help="distance from surface to center of mass")
    _type.add_argument('--frames', dest='type', action='store_const',
            const='frames', help="frame number")
    type_group.add_argument('--relative', action='store_true',
            help="for time and frame graphs, set start at impact")

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
            ('type', args.type), ('relative', args.relative),
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

    # If individual lines desired, collect data

    # Plot lines for all file lists
    for i, spread_list in enumerate(args.spreading):
        # Update kwargs for line styles
        kwargs.update({
            'linestyle': linestyles[i],
            'error_linestyle': errorstyles[i]
            })

        spread = combine_spread(spread_list, plot=args.nomean,
                color=colours[i], label=labels[i], **kwargs)

        # Check if error bars need to be included
        error = args.error and len(spread_list) > 1

        # Create graph
        spread.plot(error=error, color=colours[i], label=labels[i],
                sigma=args.sigma, drawline=False, **kwargs)

    # Finish with decorations and output options
    if legend:
        plt.legend()

    if args.save:
        kwargs = {}
        get_savekwargs(kwargs, args)
        plt.savefig(args.save, dpi=args.dpi, **kwargs)

    if args.show:
        plt.show()
