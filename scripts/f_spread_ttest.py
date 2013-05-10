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

from flowtools.draw import plot_line
from flowtools.datamaps import Spread
from flowtools.utils import calc_radius, combine_spread, get_colours, get_labels, get_linestyles, get_shift
from pandas import DataFrame, Series
from scipy import stats

def t_test_plot(args):
    """Perform a Welch's t-test on two sets of spread data, plot probability."""

    def plot(spreading, _type, shift_array):
        def get_line(spread, _type):
            if _type == 'left' or _type == 'right':
                return spread.spread[_type]['val']
            elif _type == 'radius':
                return calc_radius(spread)

        data = {}
        n = 0
        for i, spread_list in enumerate(spreading):
            for j, _file in enumerate(spread_list):
                spread = Spread().read(_file)
                line = get_line(spread, _type)
                times = np.array(spread.times) - shift_array[i][j]
                data[n] = Series(data=line, index=times)
                n += 1

        # Create DataFrame for all values and drop nan
        df = DataFrame(data).dropna()
        domain = df.index

        n = 0
        data = [[], []]
        for i, spread_list in enumerate(spreading):
            for j, _ in enumerate(spread_list):
                data[i].append(df[n].tolist())
                n += 1
        t, p = stats.ttest_ind(data[0], data[1], equal_var=False)
        plot_line(line=p, domain=domain, label=label[0], color=colour[0],
                linestyle=linestyle['line'][0], hold=True)

        return None

    # Two sets of data must be given
    if len(args.spreading) != 2:
        parser.error("exactly two sets of spread data must be supplied with -f "
                "(%d given)" % len(args.spreading))

    # Get colours, labels and line styles from default
    colour = get_colours(args.colour, len(args.spreading))
    label, draw_legend = get_labels(args.label, len(args.spreading))

    linestyle = {}
    linestyle['line'] = get_linestyles(args.linestyle, 2)

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync)

    if args.radius:
        plot(args.spreading, 'radius', shift_array)
    else:
        plot(args.spreading, 'left', shift_array)
        plot(args.spreading, 'right', shift_array)

    plt.axis('normal')

    plt.title(args.title)
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)

    plt.xlim([args.t0, args.tend])

    if draw_legend:
        plt.legend()

    # Finish by saving and / or showing
    if args.save:
        plt.savefig(args.save)

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

    # --show or --noshow for drawing figure
    line_show = line.add_mutually_exclusive_group()
    line_show.add_argument('--show', action='store_true', dest='show',
            default=True,
            help=("show graph (default: true, --noshow to turn off)"))
    line_show.add_argument('--noshow', action='store_false', dest='show',
            help=argparse.SUPPRESS)

    line.add_argument('--sync', choices=['com', 'impact'], default='com',
            help="synchronise times of different data to a common distance "
            "to the center of mass ('com', default), or to time of impact "
            "('impact')")
    line.add_argument('--radius', action='store_true',
            help="perform the test on the total radius instead of edges")

    # Decoration options
    decoration = parser.add_argument_group(title="Graph decoration",
            description="options for decorating the graph")
    decoration.add_argument('-c', '--colour', action='append', default=[],
            help="line colour")
    decoration.add_argument('-l', '--label', action='append', default=[],
            help="line label")
    decoration.add_argument('--linestyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="line style (default: solid)")
    decoration.add_argument('-t0', type=float, default=None, metavar="TIME",
            dest='t0', help="start time of graph")
    decoration.add_argument('-tend', type=float, default=None, metavar="TIME",
            dest='tend', help="maximum time of graph")
    decoration.add_argument('--title',
            default="Probability of spreading data having equal mean",
            help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default="Time (ps)", help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default="Probability", help="label of y axis")

    ## Parse and control arguments

    args = parser.parse_args()
    t_test_plot(args)
