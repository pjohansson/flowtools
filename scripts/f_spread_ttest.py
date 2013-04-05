#!/usr/bin/env python

import argparse
import numpy as np
import pylab as plt
import sys

from flowtools.draw import plot_line
from flowtools.datamaps import Spread
from pandas import Series, DataFrame
from scipy import stats

from f_spread_plot import combine_spread, get_colours, get_labels, get_linestyles, get_shift

def t_test_plot(args):
    """Perform a Welch's t-test on two sets of spread data, plot probability."""

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

    left = {}
    right = {}
    n = 0
    for i, spread_list in enumerate(args.spreading):
        # Collect data to dicts
        for j, _file in enumerate(spread_list):
            spread = Spread().read(_file)
            times = np.array(spread.times) - shift_array[i][j]
            left[n] = Series(data=spread.left, index=times)
            right[n] = Series(data=spread.right, index=times)
            n += 1

    # Construct DataFrame and drop nan-indices
    df = {}
    df['left'] = DataFrame(left).dropna()
    df['right'] = DataFrame(right).dropna()

    domain = df['left'].index
    data = {}
    for num, array in enumerate(['left', 'right']):
        n = 0
        data[array] = [[], []]
        for i, spread_list in enumerate(args.spreading):
            for j, _ in enumerate(spread_list):
                data[array][i].append(df[array][n].tolist())
                n += 1

        t, p = stats.ttest_ind(
            data[array][0],
            data[array][1],
            equal_var=False
            )

        plot_line(line=p, domain=domain, label=label[num], color=colour[num],
                linestyle=linestyle['line'][num], hold=True)

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
