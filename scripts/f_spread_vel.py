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

def vel_plot(args):
    """Draw the spreading as a function of time."""

    def plot_data(spread, times):
        """Plot either edges or radius of specified line."""

        for _type in args.plot_type:
            velocity = spread[_type]['val']
            plot_line(
                    line=velocity,
                    domain=times,
                    color=colours[i], label=label,
                    linestyle=linestyles['line'][i]
                )

        return None

    def calc_velocity(spread, plot_type, N, N_sample):
        """
        Returns the velocity of the spreading curve, as a running average
        over N frames.

        """

        def get_velocity(spreading, times, N_sample):
            velocity = []
            for i, _ in enumerate(spreading):
                i_min = max(0, i-N_sample)
                i_max = min(i+N_sample, len(spreading)-1)
                delta_x = spreading[i_max] - spreading[i_min]
                delta_t = times[i_max] - times[i_min]
                velocity.append(delta_x/delta_t)

            return velocity

        def calc_running_avg(velocity, full_times, N):
            N0 = N
            running_avg = {'val': [], 'std': []}
            times = []

            for i, _ in enumerate(velocity):
                if args.include == 'equal':
                    N = min(i - max(0, i-N0), min(i+N0, len(velocity)-1)-i)

                i_min = max(0, i-N)
                i_max = min(i+N, len(velocity)-1)

                if N == 0 or (args.include == 'limited' and i_max - i_min != 2*N):
                    continue

                running_avg['val'].append(np.average(velocity[i_min:i_max+1]))
                times.append(full_times[i])

            return running_avg, times

        running_avg = {}
        for _type in plot_type:
            velocity = get_velocity(spread.spread[_type]['val'], spread.times, N_sample)
            running_avg[_type], times = calc_running_avg(velocity, spread.times, N)

        return running_avg, times

    def print_vel(velocity, times):
        """Output the mean spread velocity to standard output."""

        print("%9c Velocity of (nm / ps)" % ' ')
        print("%9s " % "Time (ps)", end='')
        for _key in velocity.keys():
            print("%9s " % _key.capitalize(), end='')
        print()

        for i, time in enumerate(times[1:]):
            print("%9g " % time, end='')
            for _type in velocity.keys():
                print("%9g " % velocity[_type]['val'][i+1], end='')
            print()

        return None

    # Get colours, labels and line styles from default
    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync)

    for i, spread_list in enumerate(args.spreading):
        spread, data = combine_spread(spread_list, shift=shift_array[i])

        # If --nomean, draw lines here
        label = labels[i]
        if args.nomean:
            for spread_data in data:
                vel, times = calc_velocity(spread_data, args.plot_type,
                        args.num_average, args.num_sample)
                plot_data(vel, times)
                label = '_nolegend_'

        # Else draw the mean result
        else:
            vel, times = calc_velocity(spread, args.plot_type,
                    args.num_average, args.num_sample)
            plot_data(vel, times)

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
                args.save, dpi=args.dpi,
                transparent=args.transparent,
                bbox_inches='tight'
                )

    if args.print:
        if args.nomean:
            vel = calc_velocity(spread, args.plot_type, args.num_average, args.num_sample)
        print_vel(vel, spread.times)

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
    line.add_argument('-n', '--num_average', metavar='N', type=int, default=5,
            help="take running average over N points for velocity (default: 5)")
    line.add_argument('-ns', '--num_sample', type=int, default=1, metavar='N',
            help="sample positions for velocity calculations every N frames, "
            "helps to smoothen the sampling a bit but reduces accuracy (default: 1)")
    line.add_argument('-s', '--save', metavar="PATH",
            help="optionally save output image to path")
    line.add_argument('--dpi', type=int, default=150,
            help="DPI of output image")

    line.add_argument('--include', choices = ['full', 'equal', 'limited'],
            help=("for the rolling mean, either keep calculations for all "
                "samples (full), samples with an average from an equal number "
                "of points on both sides of it (equal), or samples where "
                "--num_average of points exist on both sides (limited)"))
    line.add_argument('--loglog', action='store_true',
            help="draw graph with logarithms of the x and y axis")
    line.add_argument('--noshow', action='store_false', dest='show',
            help=("do not show graph on screen"))
    line.add_argument('--sync', choices=['com', 'impact'], default='com',
            help="synchronise times of different data to a common distance "
            "to the center of mass ('com', default), or to time of impact "
            "('impact')")

    line.add_argument('--nomean', action='store_true',
            help="draw all spread curves instead of their combined mean")
    line.add_argument('-t', '--plot_type', default='diameter',
            choices=['edges', 'radius', 'diameter'],
            help="draw the velocity of edges, radius, or diameter of "
            "droplet base (default: diameter)")
    line.add_argument('--print', action='store_true',
            help="Print spread velocity data to standard output")

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
    decoration.add_argument('--transparent', action='store_true',
            help="figure saved with transparent background")
    decoration.add_argument('-t0', type=float, default=None, metavar="TIME",
            dest='t0', help="start time of graph (ps)")
    decoration.add_argument('-tend', type=float, default=None, metavar="TIME",
            dest='tend', help="maximum time of graph (ps)")
    decoration.add_argument('--title',
            default="Velocity of spreading of droplet on substrate", help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default="Time (ps)", help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default="Velocity (nm / ps)",
            help="label of y axis")

    # Call appropriate function for operation
    args = parser.parse_args()

    if args.plot_type == 'edges':
        args.plot_type = ['left', 'right']
    else:
        args.plot_type = [args.plot_type]

    vel_plot(args)
