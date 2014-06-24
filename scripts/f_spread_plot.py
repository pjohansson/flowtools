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
import os
import shutil

from flowtools.datamaps import Spread
from flowtools.draw import plot_line
from flowtools.utils import calc_radius, combine_spread, get_colours, get_labels, get_linestyles, get_shift

def spread_plot(args):
    """Draw the spreading of sets of droplets as a function of time."""

    def add_xvgdata(spread, xvg_set):
        """
        Adds data for current line to list of data to output in
        .xvg format.

        """
        add = {}
        line = []
        for _type in plot_type:
            add['legend'] = labels[i]
            add['line'] = spread.spread[_type]['val'][0:]
            add['time'] = np.array(spread.times[0:])
            line.append(add.copy())

        xvg_set.append(line)

        return None

    def save_xvgdata(xvg_data):
        """
        Saves spreading lines to .xvg files of input filenames.

        """

        def print_xvgfile(line, fnin):

            fnout = fnin.rsplit('.', 1)[0] + '.xvg'
            backup_file(fnout)
            with open(fnout, 'w') as _file:
                _file.write(
                        "@ title \"%s\"\n"
                        "@ xaxis label \"%s\"\n"
                        "@ yaxis label \"%s\"\n"
                        "@TYPE xy\n"
                        % (args.title, args.xlabel, args.ylabel)
                        )

                # Output legend information
                _file.write(
                        "@ legend on\n"
                        "@ legend box on\n"
                        "@ legend loctype view\n"
                        "@ legend 0.78 0.8\n"
                        "@ legend length 2\n"
                        "@s0 legend \"%s\"\n\n"
                        % line[0]['legend']
                        )

                for i in range(len(line[0]['time'])):
                    time = line[0]['time'][i]
                    _file.write("%f " % time)
                    for j in range(len(line)):
                        value = line[j]['line'][i]
                        _file.write("%f " % value)
                    _file.write("\n")

            return None

        def backup_file(fn):
            """If a file 'fn' exists, move to backup location."""

            fnmv = fn

            n = 0
            while (os.path.isfile(fnmv)):
                n += 1
                try:
                    _path, _file = fn.rsplit('/', 1)
                    _path += '/'
                except ValueError:
                    _path = ''
                    _file = fn

                fnmv = _path + '#' + _file.rsplit('.', 1)[0] + '.xvg.%d#' % n

            if (n > 0):
                print("File '%s' backed up to '%s'" % (fn, fnmv))
                shutil.move(fn, fnmv)

            return None

        for i, xvg_set in enumerate(xvg_data):
            # Print either all lines to separate files with extension switch
            if args.nomean:
                for j, line in enumerate(xvg_set):
                    # Replace last extension with .xvg
                    fnin = args.spreading[i][j]
                    print_xvgfile(line, fnin)

            # Or print combined lines to files with base filename as first file
            else:
                line = xvg_set[0]
                fnin = args.spreading[i][0]
                print_xvgfile(line, fnin)

        return None

    def plot_data(spread, times):
        """Plot either edges or radius of specified line."""

        for _type in plot_type:
            plot_line(
                    line=spread[_type]['val'][0:],
                    domain=np.array(times[0:]),
                    color=colours[i], label=label,
                    linestyle=linestyles['line'][i],
                    linewidth=2
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

    def get_scaling(input_time, input_radius,
            num_factors, default=1.0):
        """Get scaling factors for time and radii of all lines."""

        scaling = {}
        input_factors = {'time': input_time, 'radius': input_radius}

        for key in ['time', 'radius']:
            scaling[key] = []
            for i in range(0, num_factors):
                if i < len(input_factors[key]):
                    scaling[key].append(input_factors[key][i])
                else:
                    scaling[key].append(default)

        return scaling

    def apply_scaling(spread, all_data, scaling, num):
        """Apply time and radius scaling onto all spread data."""

        spread.scale_data(scaling['time'][num], scaling['radius'][num])
        for i, _ in enumerate(all_data):
            all_data[i].scale_data(scaling['time'][num], scaling['radius'][num])

        return None

    # Get colours, labels and line styles from default
    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))
    linestyles['error'] = get_linestyles(args.errorstyle, len(args.spreading),
            'dashed')

    # Find scaling factors for lines
    scaling = get_scaling(args.time_scaling, args.radius,
        len(args.spreading))

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync,
            radius_array=scaling['radius'], radius_fraction=args.sync_radius_fraction)

    # Initiate xvg data
    xvgdata = []

    for i, spread_list in enumerate(args.spreading):
        spread, data = combine_spread(spread_list, shift=shift_array[i])
        apply_scaling(spread, data, scaling, i)

        # Either draw all or a combined line; set which set here
        xvg_set = []
        if args.nomean:
            spread_array = data
        else:
            spread_array = [spread]

        label = labels[i]
        for spread_data in spread_array:
            plot_data(spread_data.spread, spread_data.times)
            label = '_nolegend_'

            if args.xvg:
                add_xvgdata(spread_data, xvg_set)

        # If error for line is desired, calculate and plot
        if args.error:
            plot_error(spread)

        # Add set of xvg data to array
        if args.xvg:
            xvgdata.append(xvg_set)

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

    if args.xvg:
        save_xvgdata(xvgdata)

    if args.show:
        plt.show()

    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Draw the spreading of sets of droplets as a function of time.

    Different sets, corresponding to different involved substrates,
    parameters or whatever choices, are supplied using -f. Sets can
    contain multiple collected data files, separated by spaces--only
    when another -f is supplied does a new set specification begin.
    Error analysis is performed setwise. The output graph decorations
    can be controlled on a per set basis by adding one flag per set.

    """, usage="%(prog)s [-h] -f [SET 1] -f [SET 2] [...]")

    line = parser.add_argument_group(title="Main")
    line.add_argument('-f', '--files', dest='spreading', action='append',
            nargs='+', metavar="FILES", required=True,
            help="list of spreading data files")
    line.add_argument('-s', '--save', metavar="PATH",
            help="optionally save output image to path")
    line.add_argument('--dpi', type=int, default=150,
            help="DPI of output image")
    line.add_argument('-x', '--xvg', action='store_true',
            help="output .xvg file with spreading data")

    line.add_argument('--loglog', action='store_true',
            help="draw graph with logarithms of the x and y axis")
    line.add_argument('--noshow', action='store_false', dest='show',
            help="do not show graph on screen")
    line.add_argument('--sync', choices=['com', 'impact', 'radius'], default='com',
            help="synchronise times of different data to a common distance "
            "to the center of mass ('com', default), time of impact "
            "('impact') or to a common fraction of spreading to droplet radius"
            "('radius'). In the latter case, set fraction of droplet radius "
            "using --sync_at_radius_fraction.")
    line.add_argument('--sync_radius_fraction', '-%r', type=float, default=0.1,
            metavar="FRACTION",
            help="if --sync 'radius' specified, synchronise the times for "
            "spreading data for when their spreading radius is this fraction "
            "of their droplet radius, input using --radius (default: 0.1)")

    line.add_argument('--time_scaling', '-ts', action='append',
            metavar="TAU", type=float, default=[],
            help="Scale time to t' = t/TAU, where TAU is input once per "
            "set of spreading data or defaulted to 1.")
    line.add_argument('--radius', '-R', action='append',
            metavar="R", type=float, default=[],
            help="Scale lengths L of data to L' = L/R, where R is input once "
            "per set of spreading data or defaulted to 1. Presumably this is "
            "the droplet radius given in nm.")

    line.add_argument('--nomean', action='store_true',
            help="don't take the mean of spread lines, "
            "instead draw individually")
    line.add_argument('-t', '--plot_type', default='radius',
            choices=['edges', 'radius', 'diameter'],
            help="draw the velocity of edges, radius, or diameter of "
            "droplet base (default: radius)")

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
    decoration.add_argument('--linestyle', '-ls', action='append', default=[],
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

    args = parser.parse_args()

    # Modify the plot type to allow for several edge plots
    if args.plot_type == 'edges':
        plot_type = ['left', 'right']
    else:
        plot_type = [args.plot_type]

    spread_plot(args)
