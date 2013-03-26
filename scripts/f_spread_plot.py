#!/usr/bin/env python

import argparse
import numpy as np
import pylab as plt
import sys

from flowtools.draw import plot_line
from flowtools.datamaps import Spread
from pandas import Series, DataFrame
from scipy import stats

def combine_spread(spread_files, shift, drop_return_data=False):
    """
    Combine the spread of input files, return with mean and standard
    deviation calculated.

    """

    data = []
    values = {}
    for val in ('left', 'right', 'com', 'dist'):
        values[val] = {}

    # Collect data from all files into dictionaries
    for i, _file in enumerate(spread_files):
        data.append(Spread().read(_file))
        for val in values.keys():
            values[val][i] = Series(
                    data=data[i].spread[val]['val'],
                    index=data[i].times
                    )
        data[i].times = np.array(data[i].times) - shift[i]

    spread = Spread()

    for val in values.keys():

        # Shift time as per synchronisation
        for i in values[val]:
            values[val][i].index = np.array(values[val][i].index) - shift[i]

        # Convert to DataFrame
        df = DataFrame(data=values[val])

        # If not a single file, keep only indices with at least two non-NaN
        if len(spread_files) > 1:
            df = df.dropna()

        # If return data dropped, fill data here
        if drop_return_data:
            for i in df.columns:
                data[i].spread[val]['val'] = df[i].tolist()

        # Get times, mean and standard error as lists
        mean = list(df.mean(axis=1))
        std_error = list(df.std(axis=1))
        times = list(df.index)

        # Add to Spread object
        spread.spread[val]['val'] = mean
        spread.spread[val]['std_error'] = std_error
        spread.spread['times'] = times

    return spread, data

def get_colours(colours, num_lines):
    """Create list of colours for lines from default cycle."""

    default = (
            'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'
            )

    while len(colours) < num_lines:
        colours += default
    colours = colours[:num_lines]

    return colours

def get_labels(labels, num_lines):
    """Create list of labels for legend."""

    default = '_nolegend_'
    while len(labels) < num_lines:
        labels += [default]

    # Check if legend required
    if set(labels) == set(['_nolegend_']):
        draw_legend = False
    else:
        draw_legend = True

    return labels, draw_legend

def get_linestyles(linestyles, num_lines, default='solid'):
    """Create lists of line styles."""

    # If available, use last linestyle as default
    if linestyles:
        default = linestyles[-1]

    while len(linestyles) < num_lines:
        linestyles += [default]

    return linestyles

def get_shift(spread_files_array, sync=None):
    """
    Calculate the desired time shift for synchronisation, return as array
    with time shift values corresponding to file name positions.

    """

    # If common center of mass for synchronisation desired, find minimum
    if sync == 'com':
        min_dist = np.inf
        for spread_files in spread_files_array:
            for _file in spread_files:
                data = Spread().read(_file)
                if data.dist[0] < min_dist:
                    min_dist = data.dist[0]

    # Find shift array depending on synchronisation
    shift_array = []
    for i, spread_files in enumerate(spread_files_array):
        shift_array.append([])
        for _file in spread_files:
            data = Spread().read(_file)

            if sync == 'impact':
                shift = data.times[0]

            elif sync == 'com':
                j = 0
                while data.dist[j] > min_dist:
                    j += 1
                shift = data.times[j]

            else:
                shift = 0.

            shift_array[i].append(shift)

    return shift_array

def com_plot(args):
    """Draw the center of mass height as a function of time."""

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

        # Check if error bars need to be included
        error = args.error and len(spread_list) > 1

        # Create graph
        if args.nomean:
            label = labels[i]
            for spread_data in data:
                domain = spread_data.times
                line = spread_data.dist
                plot_line(line=line, domain=domain, color=colours[i],
                        label=label, linestyle=linestyles['line'][i])
                label = '_nolegend_'
        else:
            domain = spread.times
            line = spread.dist
            plot_line(line=line, domain=domain, color=colours[i],
                    label=labels[i], linestyle=linestyles['line'][i])

        if error:
            domain = spread.times
            line = list(np.array(spread.dist)
                    + np.array(spread.spread['dist']['std_error'])
                    * args.sigma)
            plot_line(line=line, domain=domain, color=colours[i],
                    linestyle=linestyles['error'][i])
            line = list(np.array(spread.dist)
                    - np.array(spread.spread['dist']['std_error'])
                    * args.sigma)
            plot_line(line=line, domain=domain, color=colours[i],
                    linestyle=linestyles['error'][i])

    plt.title(args.title)
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)

    plt.axis('normal')

    plt.xlim([args.t0, args.tend])

    if draw_legend:
        plt.legend()

    # Finish by saving and / or showing
    if args.save:
        plt.savefig(args.save)

    if args.show:
        plt.show()

    return None

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
def spread_plot(args):
    """Draw the spreading as a function of time."""

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
                spread_data.plot(error=False, color=colours[i],
                        label=label, linestyle=linestyles['line'][i])
                label = '_nolegend_'

        # Check if error bars need to be included
        error = args.error and len(spread_list) > 1

        # Create graph
        spread.plot(error=error, color=colours[i], label=labels[i],
                sigma=args.sigma, noline=args.nomean,
                linestyle=linestyles['line'][i],
                linestyle_error=linestyles['error'][i])

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

def sample_error_plot(args):
    """Draw the sample error for spread data."""

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
    subparsers = parser.add_subparsers(dest='operation', title='operations',
            description="different operations available for spread data")

    ##
    ## Spread plot
    ##

    plot_args = subparsers.add_parser('plot',
            help="draw plots of spread data, combined or not")
    plot_args.set_defaults(func=spread_plot)

    line = plot_args.add_argument_group(title="Main")
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

    # Error plotting
    error = plot_args.add_argument_group(title="Error",
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
    decoration = plot_args.add_argument_group(title="Graph decoration",
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

    ##
    ## std plot
    ##

    std_args = subparsers.add_parser('std',
            help="draw the standard deviation of combined spread data")
    std_args.set_defaults(func=sample_error_plot)

    line = std_args.add_argument_group(title="Main")
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
    decoration = std_args.add_argument_group(title="Graph decoration",
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
    ## Center of mass plot
    ##

    com_args = subparsers.add_parser('com',
            help="draw plots of center of mass height")
    com_args.set_defaults(func=com_plot)

    line = com_args.add_argument_group(title="Main")
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

    # Error plotting
    error = com_args.add_argument_group(title="Error",
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
    decoration = com_args.add_argument_group(title="Graph decoration",
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

    ##
    ## Welch's test
    ##

    t_test_args = subparsers.add_parser('t_test', aliases=['ttest'],
            help="perform a Welch's t-test on two sets of spread data")
    t_test_args.set_defaults(func=t_test_plot)

    line = t_test_args.add_argument_group(title="Main")
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
    decoration = t_test_args.add_argument_group(title="Graph decoration",
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

    ##
    ## Parse and control arguments
    ##

    args = parser.parse_args()
    if args.operation == None:
        parser.error("argument operation: none selected")

    # Call appropriate function for operation
    args.func(args)
