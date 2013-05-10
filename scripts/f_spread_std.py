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

def sample_error_plot(args):
    """Draw the sample error for spread data."""

    def plot(spreading, _type, shift, style):
        def get_line(spread, _type):
            if _type == 'left' or _type == 'right':
                return spread.spread[_type]['std_error']
            elif _type == 'radius':
                _, radius = calc_radius(spread, error=True)
                return radius

        for i, spread_list in enumerate(spreading):
            spread, _ = combine_spread(spread_list, shift=shift[0])

            domain = spread.times
            line = get_line(spread, _type)
            plot_line(
                    line=line, domain=domain,
                    color=colours[i], label=labels[i],
                    linestyle=style[i],
                    hold=True
                    )

        return None

    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))
    complabels, draw_comp = get_labels(args.complabel, len(args.spreading))
    draw_legend = draw_legend or draw_comp

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))
    linestyles['compare'] = get_linestyles(args.compstyle, len(args.spreading),
            'dotted')

    for i, spread_list in enumerate(args.spreading):
        if args.sync == 'com':
            shift = get_shift([spread_list], sync='com')
            comp_shift = get_shift([spread_list], sync='impact')
        else:
            shift = get_shift([spread_list], sync='impact')
            comp_shift = get_shift([spread_list], sync='com')

    if args.radius:
        plot(args.spreading, 'radius', shift, linestyles['line'])
        if args.compare:
            plot(args.spreading, 'radius', comp_shift, linestyles['compare'])
    else:
        for _type in ('left', 'right'):
            plot(args.spreading, _type, shift, linestyles['line'])
            if args.compare:
                plot(args.spreading, _type, comp_shift, linestyles['compare'])

    plt.title(args.title)
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)

    plt.axis('normal')

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
    line.add_argument('--radius', action='store_true',
            help="use the radius instead of edges for drawing")

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
