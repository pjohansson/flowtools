#!/usr/bin/env python

import argparse
import numpy as np
import pylab as plt

from flowtools.datamaps import Spread
from flowtools.draw import plot_line
from flowtools.utils import calc_radius, combine_spread, get_colours, get_labels, get_linestyles, get_shift

def spread_plot(args):
    """Draw the spreading as a function of time."""

    def get_line(spread, _type):
        if _type == 'left' or _type == 'right':
            return spread.spread[_type]['val']
        elif _type == 'radius':
            radius = calc_radius(spread)
            return radius

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
        if args.nomean:
            label = labels[i]
            for spread_data in data:
                if args.radius:
                    plot_line(
                            line=get_line(spread_data, 'radius'),
                            domain=spread_data.times,
                            color=colours[i], label=label,
                            linestyle=linestyles['line'][i]
                        )
                else:
                    plot_line(
                            line=get_line(spread_data, 'left'),
                            domain=spread_data.times,
                            color=colours[i], label=label,
                            linestyle=linestyles['line'][i]
                        )
                    plot_line(
                            line=get_line(spread_data, 'right'),
                            domain=spread_data.times,
                            color=colours[i], label=label,
                            linestyle=linestyles['line'][i]
                        )
                label = '_nolegend_'
        else:
            if args.radius:
                plot_line(
                    line=get_line(spread, 'radius'),
                    domain=spread.times,
                    color=colours[i], label=labels[i],
                    linestyle=linestyles['line'][i]
                    )
            else:
                plot_line(
                    line=get_line(spread, 'left'),
                    domain=spread.times,
                    color=colours[i], label=labels[i],
                    linestyle=linestyles['line'][i]
                    )
                plot_line(
                    line=get_line(spread, 'right'),
                    domain=spread.times,
                    color=colours[i], label=labels[i],
                    linestyle=linestyles['line'][i]
                    )

    plt.title(args.title, fontsize='medium')
    plt.xlabel(args.xlabel, fontsize='medium')
    plt.ylabel(args.ylabel, fontsize='medium')

    plt.axis('normal')

    plt.xlim([args.t0, args.tend])

    if draw_legend:
        plt.legend(loc=7)

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

    # Specifially add --nomean to plot
    line.add_argument('--nomean', action='store_true',
            help="don't take the mean of spread lines, "
            "instead draw individually")
    line.add_argument('--radius', action='store_true',
            help="draw radius instead of edge positions")

    # Error plotting
    error = parser.add_argument_group(title="Error",
            description="options for error of data")

    # --error or --noerror for drawing error bars
    error_group = error.add_mutually_exclusive_group()
    error_group.add_argument('--error', action='store_true', dest='error',
            default=True,
            help=("show error for lines if multiple files entered "
                    "(default: true, --noerror to turn off)"))
    error_group.add_argument('--noerror', action='store_false',
            dest='error', help=argparse.SUPPRESS)

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
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="line style (default: solid)")
    decoration.add_argument('--errorstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="error line style (default: dashed)")
    decoration.add_argument('-t0', type=float, default=None, metavar="TIME",
            dest='t0', help="start time of graph")
    decoration.add_argument('-tend', type=float, default=None, metavar="TIME",
            dest='tend', help="maximum time of graph")
    decoration.add_argument('--title',
            default="Spreading of droplet on substrate", help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default="Time (ps)", help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default="Spreading from center of mass (nm)",
            help="label of y axis")

    # Call appropriate function for operation
    args = parser.parse_args()
    spread_plot(args)
