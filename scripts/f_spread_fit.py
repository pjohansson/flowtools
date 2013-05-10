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
from scipy import optimize

def spread_plot(args):
    """Draw the spreading as a function of time."""

    # Get colours and line styles from default
    colours = get_colours(args.colour, len(args.spreading))
    labels, draw_legend = get_labels(args.label, len(args.spreading))

    linestyles = {}
    linestyles['line'] = get_linestyles(args.linestyle, len(args.spreading))
    linestyles['fit'] = get_linestyles(args.fitstyle, len(args.spreading),
            'dashed')

    # Create linear fitting function
    fitfunc = lambda p, t, r: r - p[0] - p[1] * t
    pinit = [1.0, 1/7]

    # Find shift array for synchronisation
    shift_array = get_shift(args.spreading, sync=args.sync)
    impact_shift = get_shift(args.spreading, sync='impact')

    # Create dicts for lists of fit constants (r = amp * t**index)
    amp = {}
    index = {}
    ampError = {}
    indexError = {}

    ampMean = []
    ampMeanError = []
    indexMean = []
    indexMeanError = []

    for i, spread_list in enumerate(args.spreading):
        amp[i] = []
        index[i] = []
        ampError[i] = []
        indexError[i] = []

        spread, full_data = combine_spread(spread_list, shift=shift_array[i])
        spread.times = np.array(spread.times) - spread.times[0]

        for k, _file in enumerate(spread_list):
            data = Spread().read(_file)
            data.times = np.array(data.times) - impact_shift[i][k]

            # Get radius and domain
            radius = {'real': np.array(calc_radius(data))}
            domain = {'real': np.array(data.times)}

            # Cut times outside of range
            for j, time in enumerate(domain['real']):
                if time > args.tend:
                    radius['real'] = radius['real'][:j]
                    domain['real'] = domain['real'][:j]

            # Add logged values
            radius['log'] = np.log10(radius['real'][1:])
            domain['log'] = np.log10(domain['real'][1:])

            # Cut in log range
            for j, logt in enumerate(domain['log']):
                if logt > args.tendlog:
                    radius['log'] = radius['log'][:j]
                    domain['log'] = domain['log'][:j]

            # Fit constants to data
            out = optimize.leastsq(fitfunc, pinit,
                    args=(domain['log'], radius['log']), full_output=1)

            pfinal = out[0]
            covar = out[1]

            # Add unlogged constants to lists
            amp[i].append(10**pfinal[0])
            index[i].append(pfinal[1])
            ampError[i].append(np.sqrt(covar[1][1]) * amp[i][-1])
            indexError[i].append(np.sqrt(covar[0][0]))

            if args.draw == 'log' and args.nomean:
                plot_line(
                        line=radius['log'],
                        domain=domain['log'],
                        color=colours[i],
                        linestyle=linestyles['line'][i]
                    )
                if not args.nofit:
                    plot_line(
                            line=out[0][0] + out[0][1] * domain['log'],
                            domain=domain['log'],
                            color=colours[i], linestyle=linestyles['fit'][i]
                            )
            if args.draw == 'real' and args.nomean:
                plot_line(
                        line=radius['real'],
                        domain=domain['real'],
                        color=colours[i], linestyle=linestyles['line'][i]
                        )
                if not args.nofit:
                    plot_line(
                            line=amp[i][-1] * (domain['real']**index[i][-1]),
                            domain=domain['real'],
                            color=colours[i], linestyle=linestyles['fit'][i]
                            )

        ampMean.append(np.mean(amp[i]))
        ampMeanError.append(np.std(amp[i]) / np.sqrt(len(amp[i]) - 1))
        indexMean.append(np.mean(index[i]))
        indexMeanError.append(np.std(index[i]) / np.sqrt(len(index[i]) - 1))

        if not args.nomean:
            if args.draw == 'log':
                plot_line(
                        line=np.log10(calc_radius(spread)),
                        domain=np.log10(spread.times),
                        label=labels[i],
                        color=colours[i], linestyle=linestyles['line'][i]
                        )
                if not args.nofit:
                    plot_line(
                            line=(np.log10(ampMean[i])
                                    + indexMean[i] * np.log10(spread.times)),
                            domain=np.log10(spread.times),
                            label='C=%.2f, n=%.2f'%(ampMean[i], indexMean[i]),
                            color=colours[i], linestyle=linestyles['fit'][i]
                            )
            if args.draw == 'real':
                plot_line(
                        line=calc_radius(spread),
                        domain=spread.times,
                        label=labels[i],
                        color=colours[i], linestyle=linestyles['line'][i]
                        )
                if not args.nofit:
                    plot_line(
                            line=ampMean[i] * (domain['real']**indexMean[i]),
                            domain=domain['real'],
                            label='C=%.2f, n=%.2f'%(ampMean[i], indexMean[i]),
                            color=colours[i], linestyle=linestyles['fit'][i]
                            )

    plt.title(args.title, fontsize='medium')
    plt.axis('normal')

    plt.legend()

    # Default xlabel and xlims based on draw method
    if args.draw == 'real':
        if args.ylabel == None:
            args.ylabel = "Spread radius (nm)"
        if args.xlabel == None:
            args.xlabel = "Time (ps)"
        if (args.tend and args.tendlog) < np.inf:
            plt.xlim([None, min(args.tend, 10**args.tendlog)])
    elif args.draw == 'log':
        if args.ylabel == None:
            args.ylabel = "log10 of radius (in nm)"
        if args.xlabel == None:
            args.xlabel = "log10 of time (in ps)"
        if (args.tend and args.tendlog) < np.inf:
            plt.xlim([None, min(args.tend, args.tendlog)])

    plt.xlabel(args.xlabel, fontsize='medium')
    plt.ylabel(args.ylabel, fontsize='medium')

    if args.xlim:
        plt.xlim(args.xlim)

    # Print collected output
    print("Fitting spread radius 'R' of input file sets to power law functions "
            "of time 't' as 'R = C * (t ** n)' and taking means:")
    for i, _ in enumerate(amp):
        print()
        # If nomean, print individual line values
        if args.nomean:
            for values in zip(amp[i], ampError[i], index[i], indexError[i]):
                print("%f +/- %f" % (values[0], values[1]), end=', ')
                print("%f +/- %f" % (values[2], values[3]))

        # Print mean values
        if args.nomean:
            print("  -> ", end='')
        print("C = %f +/- %f" % (ampMean[i], ampMeanError[i]))
        if args.nomean:
            print("  -> ", end='')
        print("n = %f +/- %f" % (indexMean[i], indexMeanError[i]))

    # Finish by saving and / or showing
    if args.save:
        plt.savefig(args.save)

    if args.draw != 'off':
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

    line.add_argument('--sync', choices=['com', 'impact'], default='impact',
            help="synchronise times of different data to a common distance "
            "to the center of mass time of impact (default: 'impact')")
    line.add_argument('-tend', type=float, default=np.inf, metavar="TIME",
            help="maximum time for fit")
    line.add_argument('-tendlog', type=float, default=np.inf,
            metavar="TIME", help="maximum log10 of time for fit")

    # Specifially add --nomean to plot
    line.add_argument('--nomean', action='store_true',
            help="don't take the mean of spread lines, "
            "instead draw individually")
    line.add_argument('--radius', action='store_true',
            help="draw radius instead of edge positions")
    line.add_argument('--draw', choices=['off', 'log', 'real'],
            default='real',
            help="choose output figure or turn off (default: real)")
    line.add_argument('--nofit', action='store_true',
            help="don't fit data to curves")

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
    decoration.add_argument('--fitstyle', action='append', default=[],
            choices=['solid', 'dashed', 'dashdot', 'dotted'],
            help="error line style (default: dashed)")
    decoration.add_argument('--title',
            default="Spreading of droplet on substrate", help="graph title")
    decoration.add_argument('--xlabel', metavar="LABEL",
            default=None, help="label of x axis")
    decoration.add_argument('--ylabel', metavar="LABEL",
            default=None, help="label of y axis")
    decoration.add_argument('--xlim', nargs=2, type=float, default=None,
            help="manual control of xaxis limits")

    # Call appropriate function for operation
    args = parser.parse_args()
    spread_plot(args)
