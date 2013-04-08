#!/usr/bin/env python

import argparse
import numpy as np
import pylab as plt

from flowtools.draw import plot_line
from flowtools.datamaps import Spread
from flowtools.utils import combine_spread, get_colours, get_labels, get_linestyles, get_shift

def sample_error_plot(args): """Draw the sample error for spread data."""

    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))
    complabels, draw_comp = get_labels(args.complabel, len(args.spreading))
    draw_legend = draw_legend or draw_comp

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))
    linestyles['compare'] = get_linestyles(args.compstyle, len(args.spreading),
            'dashed')

    for i, spread_list in enumerate(args.spreading):
        if args.sync == 'com':
            shift = get_shift([spread_list], sync='com')
            comp_shift = get_shift([spread_list], sync='impact')
        else:
            shift = get_shift([spread_list], sync='impact')
            comp_shift = get_shift([spread_list], sync='com')

        spread, _ = combine_spread(spread_list, shift=shift[0])

        domain = spread.times
        line = (np.array(spread.spread['left']['std_error'])
                + np.array(spread.spread['right']['std_error'])) / 2

        plot_line(
                line=line, domain=domain,
                color=colours[i], label=labels[i],
                axis='normal', linestyle=linestyles['line'][i]
                )

        if args.compare:
            spread, data = combine_spread(spread_list, shift=comp_shift[0])
            domain = spread.times

            line = (np.array(spread.spread['left']['std_error'])
                    + np.array(spread.spread['right']['std_error'])) / 2

            plot_line(
                    line=line, domain=domain,
                    color=colours[i], label=complabels[i],
                    axis='normal', linestyle=linestyles['compare'][i]
                    )

    plt.title(args.title)
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)

    plt.xlim([args.t0, args.tend])

    if draw_legend:
        plt.legend()

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
    line.add_argument('--sigma', type=float, default=1.,
            help="number of standard deviations from mean, or Z-score, "
                    "for error (default: 1)")
    line.add_argument('--compare', action='store_true',
            help="draw the other synchronisation type as a line for comparison")

    # Decoration options
    decoration = parser.add_argument_group(title="Graph decoration",
            description="options for decorating the graph")
    decoration.add_argument('-c', '--colour', action='append', default=[],
            help="line colour, add once per line")
    decoration.add_argument('-l', '--label', action='append', default=[],
            help="line label, add once per line")
    decoration.add_argument('-cl', '--complabel', action='append', default=[],
            help="comparison line label, add once per line")
    decoration.add_argument('--linestyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="line style (default: solid)")
    decoration.add_argument('--compstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="comparison line style (default: dashed)")
    decoration.add_argument('-t0', type=float, default=None, metavar="TIME",
            dest='t0', help="start time of graph")
    decoration.add_argument('-tend', type=float, default=None, metavar="TIME",
            dest='tend', help="maximum time of graph")
    decoration.add_argument('--title',
            default="Sample error of spreading", help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default='Time (ps)', help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default='Sample error (nm)', help="label of y axis")

    ##
    ## Parse and control arguments
    ##

    args = parser.parse_args()
    sample_error_plot(args)
