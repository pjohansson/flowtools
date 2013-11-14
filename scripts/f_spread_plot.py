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

import argparse
import numpy as np
import pylab as plt

from flowtools.datamaps import Spread
from flowtools.draw import plot_line
from flowtools.utils import calc_radius, combine_spread, get_colours, get_labels, get_linestyles, get_shift

def spread_plot(args):
    """Draw the spreading as a function of time."""

    def plot_data(spread, times):
        """Plot either edges or radius of specified line."""

        for _type in plot_type:
            plot_line(
                    line=spread[_type]['val'][1:],
                    domain=times[1:],
                    color=colours[i], label=label,
                    linestyle=linestyles['line'][i]
                )

        return None

    def plot_error(spread):
        """Plot the error of either the edges or radius of a line."""

        def draw_error_line(spread):
            mean = np.array(get_line(spread, _type, error=False))
            std = np.array(get_line(spread, _type, error=True))

            # If not standard deviation desired, calculate std error
            if args.std:
                error = std
            else:
                error = (std / np.sqrt(spread.spread['num']))*args.sigma

            plot_line(
                    line=(mean + error),
                    domain=spread.times,
                    color=colours[i],
                    linestyle=linestyles['error'][i]
                )
            plot_line(
                    line=(mean - error),
                    domain=spread.times,
                    color=colours[i],
                    linestyle=linestyles['error'][i]
                )

            return None

        for _type in plot_type:
            draw_error_line(spread)

        return None

    def get_line(spread, _type, error=False):
        """Return a desired line to plot."""

        _value = 'val'
        if error:
            _value = 'std'

        return spread.spread[_type][_value]

    # Get colours, labels and line styles from default
    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))
    linestyles['error'] = get_linestyles(args.errorstyle, len(args.spreading),
            'dashed')

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync)

    for i, spread_list in enumerate(args.spreading):
        spread, data = combine_spread(spread_list, shift=shift_array[i])

        # If --nomean, draw lines here
        label = labels[i]
        if args.nomean:
            for spread_data in data:
                plot_data(spread_data.spread, spread_data.times)
                label = '_nolegend_'

        # Else draw the mean result
        else:
            plot_data(spread.spread, spread.times)

        # If error for line is desired, calculate and plot
        if args.error:
            plot_error(spread)

    plt.title(args.title, fontsize='medium')
    plt.xlabel(args.xlabel, fontsize='medium')
    plt.ylabel(args.ylabel, fontsize='medium')

    if args.loglog:
        plt.xscale('log')
        plt.yscale('log')

    plt.axis('normal')

    plt.xlim([args.t0, args.tend])

    if draw_legend:
        plt.legend(loc=args.legend_loc)

    # Finish by saving and / or showing
    if args.save:
        plt.savefig(
                args.save,
                dpi=args.dpi,
                transparent=args.transparent,
                bbox_inches='tight'
                )

    if args.show:
        plt.show()

    return None

if __name__ == '__main__':
    # Initiate subparsers for operations
    parser = argparse.ArgumentParser()

    line = parser.add_argument_group(title="Main")
    line.add_argument('-f', '--files', dest='spreading', action='append',
            nargs='+', metavar="FILES", required=True,
            help="list of spreading data files")
    line.add_argument('-s', '--save', metavar="PATH",
            help="optionally save output image to path")
    line.add_argument('--dpi', type=int, default=150,
            help="DPI of output image")

    line.add_argument('--loglog', action='store_true',
            help="draw graph with logarithms of the x and y axis")
    line.add_argument('--noshow', action='store_false', dest='show',
            help="do not show graph on screen")
    line.add_argument('--sync', choices=['com', 'impact'], default='com',
            help="synchronise times of different data to a common distance "
            "to the center of mass ('com', default), or to time of impact "
            "('impact')")

    line.add_argument('--nomean', action='store_true',
            help="don't take the mean of spread lines, "
            "instead draw individually")
    line.add_argument('-t', '--plot_type', default='diameter',
            choices=['edges', 'radius', 'diameter'],
            help="draw the velocity of edges, radius, or diameter of "
            "droplet base (default: diameter)")

    # Error plotting
    error = parser.add_argument_group(title="Error",
            description="options for error of data")

    # --error or --noerror for drawing error bars
    error_group = error.add_mutually_exclusive_group()
    error_group.add_argument('--error', action='store_true', dest='error',
            default=True,
            help=("show standard deviation or error for lines if multiple "
                "files entered (default: true, --noerror to turn off)"))
    error_group.add_argument('--noerror', action='store_false',
            dest='error', help=argparse.SUPPRESS)

    # --std drawing standard deviation
    error.add_argument('--std', action='store_true', dest='std',
            help=("show standard deviation instead of standard error "
                "(default: false)"))
    error.add_argument('--sigma', '-z', type=float, default=1.96, metavar='Z',
            help="number of standard errors from mean, or Z-score, "
                    "for error lines (default: 1.96, giving a 95%% CI)")

    # Decoration options
    decoration = parser.add_argument_group(title="Graph decoration",
            description="options for decorating the graph")
    decoration.add_argument('-c', '--colour', action='append', default=[],
            help="line colour, add once per line")
    decoration.add_argument('-l', '--label', action='append', default=[],
            help="line label, add once per line")
    decoration.add_argument("--legend_loc", type=str,
            choices=[
                "upper right", "upper left", "lower left",
                "lower right", "right", "center left",
                "center right", "lower center", 'upper center',
                "center"],
            default='center right', help="location of legend (default: center right)")
    decoration.add_argument('--linestyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="line style (default: solid)")
    decoration.add_argument('--errorstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="error line style (default: dashed)")
    decoration.add_argument('--transparent', action='store_true',
            help="figure saved with transparent background")
    decoration.add_argument('-t0', type=float, default=None, metavar="TIME",
            dest='t0', help="start time of graph")
    decoration.add_argument('-tend', type=float, default=None, metavar="TIME",
            dest='tend', help="maximum time of graph")
    decoration.add_argument('--timescale', choices=['fs', 'ps', 'ns'],
            default='ps',
            help="output graph with selected timescale (default: ps)")
    decoration.add_argument('--title',
            default="Spreading of droplet on substrate", help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default="Time (ps)", help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default="Spreading from center of mass (nm)",
            help="label of y axis")

    # Call appropriate function for operation
    args = parser.parse_args()

    # Modify the plot type to allow for several edge plots
    if args.plot_type == 'edges':
        plot_type = ['left', 'right']
    else:
        plot_type = [args.plot_type]

    spread_plot(args)
