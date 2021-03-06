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

"""
Classes and tools for data maps.

Classes:
    DataMap - a single data map
    Spread - the spreading of a System object
    System - a set of DataMap objects

Functions:
    create_filenames - creates file names for System.

"""

from flowtools.draw import draw, plot_line

import itertools
import math
import numpy as np
import os
import pylab as plt
import struct
import sys

class Spread(object):
    """
    The spreading collected from a System.

    Can be supplied with the base filenames, minimum mass and floor of
    DataMaps that are used in the creation.

    Keywords:
        base - base filename
        delta_t - time difference between frames
        floor - floor of system
        min_mass - minimum mass of system

    Properties:
        impact - the impact frame of the system

    Methods:
        plot - draw the spreading
        read - read spreading information from a file
        save - save spreading information to a file
        scale_data - scale the position and time information

    """

    def __init__(self, **kwargs):
        self.base = kwargs.pop('base', None)
        self.delta_t = kwargs.pop('delta_t', None)
        self.floor = kwargs.pop('floor', None)
        self.min_mass = kwargs.pop('min_mass', None)

        self._reset()

        return None

    @property
    def left(self):
        return self.spread['left']['val']
    @left.setter
    def left(self, _list):
        self.spread['left']['val'] = _list
        return None

    @property
    def right(self):
        return self.spread['right']['val']
    @right.setter
    def right(self, _list):
        self.spread['right']['val'] = _list
        return None

    @property
    def com(self):
        return self.spread['com']['val']
    @com.setter
    def com(self, _list):
        self.spread['com']['val'] = _list
        return None

    @property
    def diameter(self):
        return self.spread['diameter']['val']
    @diameter.setter
    def diameter(self, _list):
        self.spread['diameter']['val'] = _list
        return None

    @property
    def dist(self):
        return self.spread['dist']['val']
    @dist.setter
    def dist(self, _list):
        self.spread['dist']['val'] = _list
        return None

    @property
    def radius(self):
        return self.spread['radius']['val']
    @radius.setter
    def radius(self, _list):
        self.spread['radius']['val'] = _list
        return None

    @property
    def times(self):
        return self.spread['times']
    @times.setter
    def times(self, _list):
        self.spread['times'] = _list

    def plot(self, **kwargs):
        """
        Draw the spread as a function of times or distance from
        substrate floor to center of mass. By default plots the distance
        from edges to center of mass of impact, plot radius by supplying
        keyword line = radius.

        Keywords:
            error - True of False (default) to draw error bars if available
            line - 'com' (default) or 'radius' for line type
            noline - True or False (default) to not draw spreading line,
                useful to enable for only drawing the error
            relative - True or False (default) to start time at impact
            sigma - number of standard deviations from mean to use as
                error lines (default: 1)
            type - 'times' (default) or 'dist' to plot spread as a function of

            Others as for draw.draw

        """

        def calc_error(line, sigma):
            """Calculate and return error for given line and sigma."""

            error = {
                    'up': list(
                        np.array(line['val'])
                        + np.array(line['std_error']) * sigma
                            ),
                    'down': list(
                        np.array(line['val'])
                        - np.array(line['std_error']) * sigma
                        )
                    }

            return error

        def draw_com(spread, **kwargs):
            """Draw edges of droplet around center of mass."""

            kwargs.setdefault('ylabel', 'Positions (nm)')

            for line in (spread['left'], spread['right']):
                if draw_line:
                    kwargs.update({'linestyle': linestyle['line']})

                    kwargs.update({'line': line['val']})
                    plot_line(**kwargs)

                kwargs.update({'label': '_nolegend_'})

                if draw_error:
                    kwargs.update({'linestyle': linestyle['error']})

                    for line_error in calc_error(line, sigma).values():
                        kwargs.update({'line': line_error})
                        plot_line(**kwargs)

            return None

        def draw_radius(spread, **kwargs):
            """Draw the radius of spreading droplet."""

            kwargs.setdefault('ylabel', 'Droplet radius (nm)')

            if draw_line:
                kwargs.update({'linestyle': linestyle['line']})

                kwargs.update({'line': spread['radius']['val']})
                plot_line(**kwargs)
            if draw_error:
                kwargs.update({'linestyle': linestyle['error']})

                for line_error in calc_error(spread['radius'], sigma):
                    kwargs.update({'line': line_error})
                    plot_line(**kwargs)

            return None

        @draw
        def plot_line(**kwargs):
            """Decorator for line styles."""

            domain = kwargs.pop('domain')
            line = kwargs.pop('line')

            plt.plot(domain, line, **kwargs)

            return None

        # Get options
        draw_error = kwargs.pop('error', False)
        draw_line = not kwargs.pop('noline', False)
        relative = kwargs.pop('relative', False)
        sigma = kwargs.pop('sigma', 1)
        linestyle = {
                'line': kwargs.pop('linestyle', 'solid'),
                'error': kwargs.pop('linestyle_error', 'dashed')
                }

        # Set defaults for @draw
        kwargs.update({'figure': False})
        kwargs.setdefault('axis', 'normal')
        kwargs.setdefault('title', 'Spreading of droplet on substrate')
        kwargs.setdefault('color', 'blue')

        # Catch some particular draw options
        save = kwargs.pop('save', None)
        show = kwargs.pop('show', False)
        kwargs.update({'save': False})
        kwargs.update({'show': False})

        # Set domain to times
        kwargs.update({'domain': self.spread['times']})
        kwargs.setdefault('xlabel', 'Time (ps)')

        line_type = kwargs.pop('line', 'com')
        if line_type == 'com':
            draw_com(self.spread, **kwargs)

        elif line_type == 'radius':
            draw_radius(self.spread, **kwargs)

        else:
            raise KeyError("line plot has to be 'com' or 'radius' type")

        # Perform eventual caught options
        if save:
            plt.save(save, dpi=kwargs.get('dpi', None))
        if show:
            plt.show()

        return None

    def read(self, _path):
        """Read spread information from a file at _path."""

        def read_xvg(_file):
            """
            Read spread information from a .xvg file. Data columns of
            file must be:

                time(ps) radius(nm)

            with space separation.

            """

            def add_line(time, radius):
                self.times.append(time)
                self.radius.append(radius)
                self.diameter.append(2*radius)
                self.left.append(-radius)
                self.right.append(radius)
                self.com.append(0.)
                self.dist.append(0.)

                return None

            lines = _file.readlines()

            for line in lines:
                try:
                    time, radius = map(float, line.strip().split())
                    add_line(time, radius)
                except ValueError:
                    next

            self.floor = 0
            self.delta_t = self.times[-1]/len(self.times)
            self.min_mass = 0.

            return None

        def read_std(_file):
            """Read from standard home brewn format."""
            line = _file.readline().strip()

            while not line.lower().startswith('spread:'):
                if line.lower().startswith('floor'):
                    self.floor = int(line.split(':')[-1])
                if line.lower().startswith('min mass'):
                    self.min_mass = float(line.split(':')[-1])
                if line.lower().startswith('delta_t'):
                    self.delta_t = float(line.split(':')[-1])

                line = _file.readline().strip()

            # Append spreading until end of file
            header = _file.readline().strip().split()
            line = _file.readline().strip()
            while line:
                values = line.split()
                for i, val in enumerate(values):
                    if header[i] == 'times':
                        self.spread[header[i]].append(float(val))
                    else:
                        self.spread[header[i]]['val'].append(float(val))

                line = _file.readline().strip()

            self._calc_diamrad()

            return None

        self._reset()

        with open(_path) as _file:
            if _path.endswith('.xvg'):
                read_xvg(_file)
            else:
                read_std(_file)


        return self

    def save(self, _path):
        """Save the spread information to a file at _path."""

        with open(_path, 'w') as _file:
            # Write general information
            if self.base != None:
                _file.write("Path: %s\n" % self.base)
            if self.delta_t != None:
                _file.write("Delta_t: %f\n" % self.delta_t)
            if self.floor != None:
                _file.write("Floor: %d\n" % self.floor)
            if self.min_mass != None:
                _file.write("Min mass: %f\n" % self.min_mass)
            _file.write('\n')

            # Write header and then fields
            _file.write("Spread:\n")
            header = ("%9s %9s %9s %9s %9s"
                    % (
                        'left', 'right', 'com', 'times', 'dist'
                        )
                    )

            header += '\n'
            _file.write(header)

            for i, _ in enumerate(self.times):
                line = ("%9.3f %9.3f %9.3f %9.3f %9.3f"
                        % (
                            self.left[i], self.right[i], self.com[i],
                            self.times[i], self.dist[i]
                            )
                        )

                line += '\n'
                _file.write(line)

            return None

    def scale_data(self, tau=1.0, R=1.0):
        """
        Rescale times t to t/tau and all positions l to l/R, where 'tau'
        and 'R' are some input time and length scales ('R' presumably
        the droplet radius).

        """

        self.times = list(np.array(self.times)/tau)
        for _type in ['left', 'right', 'radius', 'diameter', 'dist', 'com']:
            for key in self.spread[_type].keys():
                self.spread[_type][key] = list(
                        np.array(self.spread[_type][key])/R
                        )

        return None

    def time_set(self, start=0.0, delta_t=0.0):
        """Set the times array by supplying a time of initial frame
        using 'start' and a time difference using 'delta_t'.

        """

        times = []
        for i, _ in enumerate(self.times):
            times.append(start + i*delta_t)

        self.times = times.copy()

        return None

    def _add(self, frame):
        """Add a frame of spreading."""

        try:
            self.left.append(frame['left'])
            self.right.append(frame['right'])
            self.com.append(frame['com'])
            self.dist.append(frame['dist'])
            self.times.append(frame['time'])
        except KeyError:
            raise KeyError("not all values present to add")

        return None

    def _calc_diamrad(self):
        """Calculate diameter and radius of spreading lists."""

        for left, right in zip(self.spread['left']['val'], self.spread['right']['val']):
            self.diameter.append(right - left)
            self.radius.append(self.diameter[-1]/2)

        return None

    def _reset(self):
        """Reset the system."""

        spread = {}
        spread['times'] = []
        for field in ('left', 'right', 'com', 'dist', 'radius', 'diameter'):
            spread.update({field: {'val': [], 'std_error': []}})

        self.spread = spread

        return None


class System(object):
    """
    A system, made for operations on a set of DataMap objects.

    Can be initialised with keywords as for DataMap.droplet, as well
    as 'floor' for a collective floor of the system, 'datamaps' for
    initial datamaps and 'delta_t' for difference in time between maps.

    Methods:
        base - a base file name
        datamaps - an array of file names of DataMaps.
        delta_t - the difference in time between DataMaps
        droplet_columns - an option for DataMap.droplet
        files - create file names from a base
        floor - the collective floor row number of the system
        info - collective information of the system
        min_mass - an option for DataMap.droplet
        x - position along x of column
        y - position along y of row

    """

    def __init__(self, **kwargs):
        self.base = kwargs.pop('base', None)

        self.datamaps = kwargs.pop('datamaps', [])
        self.delta_t = kwargs.pop('delta_t', 0.)
        self.floor = kwargs.pop('floor', None)
        self.min_mass = kwargs.pop('min_mass', 0.)
        self._droplet_columns = kwargs.pop('columns', 1)

        return None

    def files(self, **kwargs):
        """
        Construct file names for self.datamaps from self.base and frame
        numbers for start and end. These default to 1 and Infinity,
        meaning that all matches with the provided base will be included.

        Verifies that all files within specified frames exist, only creates
        file names for those.

        Keywords:
            base - set a new base file name
            ext - an extension for the file name, defaults to '.dat'
            numdigits - the number of digits included in frame number for
                file names, defaults to 5
            start - frame number to start from
            end - frame number to end with

        """

        def create(base, frame, numdigits, ext):
            # Create variable-digits string
            num = ('%%0%dd' % numdigits) % frame
            return '%s%s%s' % (base, num, ext)

        self.base = kwargs.pop('base', self.base)
        if self.base == None:
            raise KeyError("self.base not set")

        self.datamaps = []

        ext = kwargs.pop('ext', '.dat')
        numdigits = kwargs.pop('numdigits', 5)

        self._end = kwargs.pop('end', np.inf)
        self._start = kwargs.pop('start', 1)

        frame = self._start
        filename = create(self.base, frame, numdigits, ext)

        while os.path.isfile(filename) and frame <= self._end:
            self.datamaps.append(filename)

            frame += 1
            filename = create(self.base, frame, numdigits, ext)

        return None

    @property
    def datamaps(self):
        """The DataMaps of the system as a list."""

        return self._datamaps

    @datamaps.setter
    def datamaps(self, datamaps):
        # Ensure that datamaps is a list
        if not isinstance(datamaps, list):
            datamaps = [datamaps]
        self._datamaps = datamaps

        return None

    @property
    def info(self):
        """
        Information of the system, read from the first DataMap in
        the list self.datamaps.

        """

        if self.datamaps:
            self._info = DataMap(self.datamaps[0]).info
            return self._info

        return dict()

    def spread(self, **kwargs):
        """
        Find and return the spreading of a droplet for datamaps in
        the system.

        Spreading is returned as Spread class object.

        Keywords:
            print - True (default) or False to print status for collection

        """

        def collect(edges, floor, delta_t, com_impact, datamap):
            """
            Collect frame information into dictionary for Spread
            object.

            """
            com_current = datamap.com
            frame = {
                    'left': edges['left'] - com_impact['X'],
                    'right': edges['right'] - com_impact['X'],
                    'com': com_current['X'],
                    'time': (i + 1) * delta_t,
                    'dist': com_current['Y'] - datamap.y(floor)
                    }

            return frame

        def find_edges(datamap, floor):
            """
            Find edges of DataMap in row floor.

            Return dictionary with keys 'left' and 'right' for edge
            positions if found. If no positions found an empty dictionary
            is returned.

            """

            edges = {}
            row = datamap.cells[floor, :]

            # Get first and last droplet cells in row
            left = None
            right = None

            for i, cell in enumerate(row):
                if cell['droplet']:

                    right = i
                    if left == None:
                        left = i

            # Get positions from edges and cell dimensions
            if left != None and right != None:
                cell_size = datamap.info['cells']['size']['X']
                edges = {
                        'left': (datamap.x(left) - cell_size / 2),
                        'right': (datamap.x(right) + cell_size / 2)
                        }

            return edges

        self._spread = Spread(
                min_mass = self.min_mass, delta_t = self.delta_t,
                floor = self.floor
                )
        if self.floor == None:
            raise KeyError("self.floor not set")

        for i, _file in enumerate(self.datamaps):
            # Print status if desired
            if kwargs.get('print', True):
                print("\rReading '%s' (%d of %d) ..."
                        % (_file, i + 1, len(self.datamaps)), end = ' '
                        )

            # Read DataMap with options
            datamap = DataMap(
                    _file, min_mass = self.min_mass,
                    columns = self._droplet_columns
                    )

            # If edges found, collect and append frame information
            edges = find_edges(datamap, self.floor)
            if edges:

                # At impact, get center of mass
                if self._spread.times == []:
                    com_impact = DataMap(_file).com

                frame = collect(
                        edges, self.floor, self.delta_t, com_impact, datamap
                        )
                self._spread._add(frame)

        # Calculate diameter and radius of spreading
        self._spread._calc_diamrad

        if kwargs.get('print', True):
            print()

        return self._spread


class DataMap(object):
    """
    A data map for flow field data from simulations.

    Contains cell information in self.cells, arranged into a 2d numpy array
    where the first index contains row and the second column number of cells.

    Keyword arguments can be provided on init as for self.droplet.

    Example:
        DataMap('include/datamap.dat') returns a DataMap with cells read from
        the file 'include/datamap.dat'.

        DataMap('include/datamap.dat', min_mass = 25) returns the same
        DataMap, but with 'droplet' only being cells of a minimum mass 25.

        self.cells[:, 10] returns cell information of all rows in the eleventh
        column.

        self.cells[16:22, 12:16] returns cell information of a small, cut box
        of the system.

    Methods:
        com - get the center of mass of the system
        cut - return a new DataMap with cells inside a specified cut
        dens - plot the density field of the map
        draw_interface - draw a contour of the interface
        droplet - mark cells as 'droplet' or not depending on conditions
        flow - plot flow fields of the map
        fields - get the fields of the droplet
        floor - get the lowest row of the system with 'droplet' cells
        info - get information from the DataMap
        interface - get a list of droplet interface coordinates
        mean - get the mean, standard deviation and standard error of some variable
        print - a simple print to stdout of system
        save - save the DataMap to a file

    Classes:
        FlatArray - context manager for working on a one-dimensional
            array for the cells

    """

    def __init__(self, _path=None, **kwargs):
        self.fields = kwargs.pop('fields', 'all')
        self.path = _path

        # Read if given path, otherwise keep empty
        if self.path:
            self._read()
            self._info = self.info
            self._grid()
            self.droplet(**kwargs)

        return None

    class FlatArray(object):
        """
        Context manager for flattening arrays for certain operations,
        restoring them on exit. Returns modified array.

        Example:
            with FlatArray(array) as flat_array:
                ...

        """

        def __init__(self, _array):
            self.array = _array
            return None

        def __enter__(self):
            self.shape = self.array.shape
            self.array = self.array.transpose().ravel()
            return self.array

        def __exit__(self, type, value, traceback):
            self.array.resize(self.shape)
            self.array = self.array.transpose()
            return self.array


    @property
    def com(self):
        """Returns center of mass of map as dict()."""

        _com = {'X': 0, 'Y': 0}
        _mass = 0

        try:
            with self.FlatArray(self.cells) as cells:
                for cell in cells:
                    # Add if 'droplet'
                    if cell['droplet']:
                        _com['X'] += cell['X'] * cell['M']
                        _com['Y'] += cell['Y'] * cell['M']
                        _mass += cell['M']

                # Average over mass
                _com['X'] /= _mass
                _com['Y'] /= _mass

        except KeyError:
            print("No mass in data map.")

        return _com

    @property
    def fields(self):
        """Data fields contained in cells."""
        return self._fields

    @fields.setter
    def fields(self, _fields):
        """
        Sets which fields the data map contains.

        'all', 'dens' or 'flow' can be supplied as arguments to set fields
        accordingly. The default is 'all'.

        """

        self._fields = {'X', 'Y'}

        if _fields == 'all':
            _add = {'U', 'V', 'M', 'N', 'T'}
        elif _fields == 'dens':
            _add = {'M', 'N', 'T'}
        elif _fields == 'flow':
            _add = {'U', 'V'}

        self._fields.update(_add)
        return None

    @property
    def floor(self):
        """
        Returns the floor of the system, i.e. the lowest row occupied by
        droplet cells.

        """

        # Initiate with no floor
        self._floor = None

        # Check for first row with 'droplet' cell
        for row, row_cells in enumerate(self.cells):
            for cell in row_cells:
                if cell['droplet']:
                    self._floor = row
                    return self._floor
        return None

    @property
    def info(self):
        """Scans cells for information data. Returns as dict()."""

        # Initiate total dictionary
        _info = {
                'cells': {},
                'size': {'X': [], 'Y': []}
                }

        with self.FlatArray(self.cells) as cells:
            # Find system size
            Dx = [cells[0]['X'], cells[-1]['X']]
            Dy = [cells[0]['Y'], cells[-1]['Y']]

            # Initiate with total number of cells
            cellinfo = {
                    'total_cells': len(cells),
                    'num_cells': {},
                    'size': {}
                    }

            # Find number of cells in each direction
            numcells = {'X': 0, 'Y': 0}
            x = cells[0]['X']
            while x == cells[numcells['Y']]['X']:
                numcells['Y'] += 1

            numcells['X'] = cellinfo['total_cells'] // numcells['Y']
            cellinfo['num_cells'] = numcells

            # Find cell dimensions
            cellinfo['size']['X'] = (
                    cells[cellinfo['num_cells']['Y']]['X']
                    - cells[0]['X']
                    )
            cellinfo['size']['Y'] = cells[1]['Y'] - cells[0]['Y']

        _info['size']['X'] = Dx
        _info['size']['Y'] = Dy
        _info['cells'] = cellinfo

        return _info

    def combine(self, nx=1, ny=1, verbose=False):
        """
        Combine cells of DataMap into larger ones, the number of which given
        by kwargs 'nx' and 'ny' for cells in x and y respectively. If an even
        division cannot be found for these numbers, the remainder of cells
        which could not be included in the combination are cut from the right
        and top of the system.

        """

        def find_cells(cells, num_combine):
            """Return two arrays respectively containing cell ranges in
            x and y to cut.

            """

            cut = []
            for var in ['X', 'Y']:
                n = cells[var]
                start = n*num_combine[var]
                end = (n+1)*num_combine[var] - 1
                cut.append([start, end])

            return cut

        def combine_cells(all_cells):
            """Combine cell information of all cells in 'cells', return
            as new cell.

            """

            def print_add_cell(cell, final):
                print("X = %.3f, Y = %.3f" % (cell['X'], cell['Y']))
                print("N = %.3f + %.3f" % (final['N'], cell['N']))
                print("M = %.3f + %.3f" % (final['M'], cell['M']))
                print("T = %.3f + (N=%.3f)*%.3f" % (final['T'], cell['N'], cell['T']))
                print("U = %.3f + (M=%.3f)*%.3f" % (final['U'], cell['M'], cell['U']))
                print("V = %.3f + (M=%.3f)*%.3f" % (final['V'], cell['M'], cell['V']))

                return None

            def print_avg_cell(final):
                print("X = %.3f, Y = %.3f" % (final['X']/len(cell_list), final['Y']/len(cell_list)))
                print("N = %.3f" % final['N'])
                print("M = %.3f" % final['M'])
                print("T = T/N = %.3f/%.3f = %.3f"
                        % (final['T'], final['N'], final['T']/final['N']))
                print("U = U/M = %.3f/%.3f = %.3f"
                        % (final['U'], final['M'], final['U']/final['M']))
                print("V = V/M = %.3f/%.3f = %.3f"
                        % (final['V'], final['M'], final['V']/final['M']))

            with self.FlatArray(all_cells.cells) as cell_list:
                # Create cell to collect data into
                final = {var: 0. for var in ['X', 'Y', 'N', 'M', 'T', 'U', 'V']}
                final['droplet'] = False

                for i, cell in enumerate(cell_list[0:]):
                    if verbose:
                        print("Adding cell %d:" % i)
                        print_add_cell(cell, final)

                    # Add variables
                    for var in ['X', 'Y', 'M', 'N']:
                        final[var] += cell[var]

                    # Add mass flow
                    for var in ['U', 'V']:
                        final[var] += cell['M']*cell[var]

                    # Att temperate, scaled by N
                    final['T'] += cell['T']*cell['N']
                    final['droplet'] = final['droplet'] or cell['droplet']

                if verbose:
                    print("Final cell:")
                    print_avg_cell(final)

                # Average positions
                for var in ['X', 'Y']:
                    final[var] /= len(cell_list)

                # Finalise mass flow
                if final['M'] > 0:
                    for var in ['U', 'V']:
                        final[var] /= final['M']

                # Finalise temperature
                if final['N'] > 0:
                    final['T'] /= final['N']

                if verbose:
                    print(final)

            return final

        num_combine = {'X': nx, 'Y': ny}
        if verbose:
            print("Combining %d cells along x and %d along y."
                    % (num_combine['X'], num_combine['Y']))

        num_cells = {}
        for var, n in self._info['cells']['num_cells'].items():
            num_cells[var] = int(n/num_combine[var])
        if verbose:
            print("Combining %dx%d cells into %dx%d."
                    % (self.info['cells']['num_cells']['X'], self.info['cells']['num_cells']['Y'],
                        num_cells['X'], num_cells['Y']))

        # Quickly create a DataMap of final size by cutting self
        combined = DataMap(None)
        combined.cells = self.cells[
                0:num_cells['Y'],
                0:num_cells['X']
                ]
        if verbose:
            print(combined.info)

        # Go through all cells in new system
        for x in range(num_cells['X']):
            for y in range(num_cells['Y']):

                # Find cells to include
                cell_num = {'X': x, 'Y': y}
                if verbose:
                    print("Finding cells to include for output cell (%d,%d):"
                            % (x, y), end=' ')
                cutx, cuty = find_cells(cell_num, num_combine)
                if verbose:
                    print("[%d:%d, %d:%d]" % (cutx[0], cutx[1], cuty[0], cuty[1]))
                    sys.stdout.flush()

                # Combine cells
                new = self.cut(cutx=cutx, cuty=cuty, input_is_cells=True)
                combined.cells[y, x] = combine_cells(new)

        return combined

    def contactangle(self, num_layers=1, floor=0):
        """
        Returns the left and right contact angles in degrees calculated
        from the interface. The angle is calculated by a trigonometric
        fit from the cell at 'floor' and 'num_layers' above.

        Requires self.droplet to have been run.

        """

        def angle(cells, mid):
            dx = np.abs(mid - cells['bottom'][0]) - np.abs(mid - cells['top'][0])
            dy = cells['top'][1] - cells['bottom'][1]
            return np.arccos(dx/np.sqrt(dx**2 + dy**2))*180/np.pi

        if floor < 0 or num_layers < 1:
            raise Exception(
                "Angles can only be calculated if floor (%d) is non-negative "
                "and num_layers (%d) is positive integer" % (floor, num_layers)
                )

        interface = self.interface()
        if floor+num_layers > len(interface)/2:
            raise Exception("Trying to calculate angle from cells outside of droplet height")

        left = {'bottom': interface[floor], 'top': interface[floor+num_layers]}
        right = {'bottom': interface[-(floor+1)], 'top': interface[-(floor+num_layers+1)]}
        mid = (right['bottom'][0] + left['bottom'][0])/2

        return [angle(cell, mid) for cell in [left, right]]

    def cut(self, **kwargs):
        """
        Cut out a certain part of the system, specified by keywords
        'cutx' = [min(x), max(x)] and 'cuty' = [min(y), max(y)] in system
        positions that should be kept.

        If cell indices instead of system positions are desired for cut,
        specify keywords 'input_is_cells' = True.

        Returns a DataMap of the newly cut system, leaving the original intact.

        Example:
            self.cut(cuty = [13.5, 20.0]) to cut only in y.

            self.cut(cutx = [-10, 5], cuty = [0, 15]) to cut in x and y.

        """

        def max_cell(cut, start, size, top_cell):
            return min(top_cell, math.floor((cut - start) / size - 0.5))

        def min_cell(cut, start, size):
            return max(0, math.ceil((cut - start) / size + 0.5))

        def min_max_cell(cut, start, size, num_cells):
            cut_cell_min = min_cell(cut[0], start, size)
            cut_cell_max = max_cell(cut[1], start, size, num_cells)
            return [cut_cell_min, cut_cell_max]

        cutx = kwargs.pop('cutx', [-np.inf, np.inf])
        cuty = kwargs.pop('cuty', [-np.inf, np.inf])
        input_is_cells = kwargs.pop('input_is_cells', False)

        # Get information
        _info = self._info

        # Check system limits
        if not input_is_cells:
            cutx[0] = max(cutx[0], _info['size']['X'][0])
            cutx[1] = min(cutx[1], _info['size']['X'][1])
            cuty[0] = max(cuty[0], _info['size']['Y'][0])
            cuty[1] = min(cuty[1], _info['size']['Y'][1])

        start = {
                'X': _info['size']['X'][0],
                'Y': _info['size']['Y'][0]
                }
        cell_size = {
                'X': _info['cells']['size']['X'],
                'Y': _info['cells']['size']['Y']
                }
        num_cells = _info['cells']['num_cells']

        # Find cell interval to keep
        if not input_is_cells:
            cells = {
                    'X': min_max_cell(
                        cutx, start['X'], cell_size['X'], num_cells['X']
                        ),
                    'Y': min_max_cell(
                        cuty, start['Y'], cell_size['Y'], num_cells['Y']
                        )
                    }
        else:
            cells = {
                    'X': [cutx[0], cutx[1]],
                    'Y': [cuty[0], cuty[1]]
                    }

        # Create and copy cut data map
        data_map = DataMap(None)
        data_map.cells = self.cells[
                cells['Y'][0]:(cells['Y'][1] + 1),
                cells['X'][0]:(cells['X'][1] + 1)
                ]
        data_map._info = data_map.info
        return data_map

    def dens(self, **kwargs):
        """
        Draw the density map of the data map.

        Keywords:
            min_frac - a minimum fraction to include
            min_mass - a minimum mass to include.
            norm - a mass value which will be set as '1' in the plot.
            Others as for hist2d.

        """

        @draw
        def plot(**kwargs):
            """Plot maps using hist2d."""

            x = kwargs.pop('x', [])
            y = kwargs.pop('y', [])
            mass = kwargs.pop('mass', [])

            # Get bins from system
            num_cells = list(self._info['cells']['num_cells'].values())
            num_cells.reverse()

            # Get minimum to draw, prioritise fraction
            min_frac = kwargs.pop('min_mass')
            if 'min_frac' in kwargs:
                min_frac = kwargs.pop('min_frac', 0.)

            plt.hist2d(
                    x, y, weights = mass,
                    bins = num_cells,
                    cmin = min_frac,
                    **kwargs)

            return None

        min_mass = kwargs.setdefault('min_mass', 0.)

        # Collect 'droplet' cells into arrays
        x = []
        y = []
        mass = []

        for row in self.cells:
            for cell in row:
                x.append(cell['X'])
                y.append(cell['Y'])
                if cell['droplet'] and cell['M'] >= min_mass:
                    mass.append(cell['M'])
                else:
                    mass.append(-1.)

        # Get and apply density normalising
        norm = kwargs.pop('norm', max(mass))
        min_mass /= norm
        for i, _ in enumerate(mass):
            mass[i] /= norm

        kwargs.update({'x': x})
        kwargs.update({'y': y})
        kwargs.update({'mass': mass})

        plot(**kwargs)

        return None

    def draw_interface(self, **kwargs):
        """
        Draw a contour of the droplet interface, as marked by edge
        'droplet' cells.

        See also:
            self.interface()

        """

        @draw
        def plot(**kwargs):
            X = kwargs.get('X')
            Y = kwargs.get('Y')
            plt.plot(X, Y)

        X, Y = self._get_interface()

        kwargs.update({'X': X})
        kwargs.update({'Y': Y})
        kwargs.setdefault('xlabel', 'x (nm)')
        kwargs.setdefault('ylabel', 'y (nm)')
        kwargs.setdefault('title', 'Droplet interface')

        plot(**kwargs)

        return None

    def droplet(self, **kwargs):
        """
        Check entire system for droplet cells, flagging 'droplet' as
        True or False in the cell list.

        Checks flow, mass, and runs a function to find connections to
        ignore precursor films as well as stray cells.

        Specify a minimum mass using the keyword 'mass', default is 0.

        Additionally, a tolerance for 'stray droplet cells' can be given
        as the keyword 'width' to check for connections in. The default
        is 1 cell on each side of the considered cell. Raising this might
        make more cells from the precursor film be included, consider the
        way in which a droplet spreads on a substrate.

        Example:
            self.droplet(mass = 30.0, width = 2)

        This is equivalent to calling the methods _flow(), _mass() and
        _inside() with equal parameters.

        """

        # Read arguments
        min_mass = kwargs.pop('min_mass', 0.)
        columns = kwargs.pop('columns', 1)

        # Call controllers in order
        #self._cells_flow()
        self._cells_min_mass(min_mass = min_mass)
        self._cells_inside(columns = columns)

        return None

    def flow(self, **kwargs):
        """
        Draw flow fields of the system using quiver.

        Can colour the quiver arrows by the cell temperature by supplying
        temp = True.

        Keywords:
            color - color the arrows.
            min_mass - include only cells with a minimum mass.
            temp - color quiver arrows by their temperature.
            xlim, ylim - cut the plot view.
            Others as for quiver.

        """

        @draw
        def plot(**kwargs):
            """Draw a quiver field of vectors."""

            x = kwargs.pop('x')
            y = kwargs.pop('y')
            u = kwargs.pop('u')
            v = kwargs.pop('v')
            t = kwargs.pop('t')

            if kwargs.pop('temp', False):
                plt.quiver(x, y, u, v, t, **kwargs)
            else:
                plt.quiver(x, y, u, v, **kwargs)

            return None

        # Fill in cell values
        x = []
        y = []
        u = []
        v = []
        t = []

        min_mass = kwargs.pop('min_mass', 0.)

        for row in self.cells:
            for cell in row:
                if cell['droplet'] and cell['M'] >= min_mass:
                    x.append(cell['X'])
                    y.append(cell['Y'])
                    u.append(cell['U'])
                    v.append(cell['V'])
                    t.append(cell['T'])

        # Set some defaults if not input
        kwargs.update({
            'xlim': kwargs.pop('xlim', self._info['size']['X']),
            'ylim': kwargs.pop('ylim', self._info['size']['Y']),
            'color': kwargs.pop('color', 'blue'),
            'title': kwargs.pop('title', 'Flow of droplet on substrate')
            })

        # If temperature, default to colorbar
        if kwargs.get('temp', False):
            kwargs.setdefault('colorbar', True)

        plot(x = x, y = y, u = u, v = v, t = t, **kwargs)

        return None

    def interface(self, get_cell_numbers=False):
        """
        Find interface cells of droplets and return ordered list of
        cell center coordinates by default, or cell numbers by calling
        with 'get_cell_numbers=True'.

        Cells are ordered counting from the left edge to the right along
        the interface, with the final cell being the right contact line
        edge.

        See also:
            self.draw_interface()
            self._get_interface()
            self._interface_length()

        """

        cells = {'left': [], 'right': []}
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                if cell['droplet']:
                    if get_cell_numbers:
                        cells['left'].append([j, i])
                    else:
                        cells['left'].append([cell['X'], cell['Y']])
                    break

            for j, cell in enumerate(reversed(row)):
                if cell['droplet']:
                    if get_cell_numbers:
                        cells['right'].append([len(row)-j-1, i])
                    else:
                        cells['right'].append([cell['X'], cell['Y']])
                    break

        interface = cells['left']
        interface.extend(reversed(cells['right']))

        return interface

    def mean(self, variable, if_droplet=True):
        """
        From a given variable of 'M', 'N', 'T', 'U' and 'V' calculates the
        mean, standard deviation and standard error of entire system.

        By default only 'droplet' cells are included in calculation,
        supply 'if_droplet=False' to use all cells.

        """

        values = []
        for row in self.cells:
            for cell in row:
                if not if_droplet or cell['droplet']:
                    values.append(cell[variable])

        data = {
                'mean': np.mean(values),
                'stdev': np.std(values),
                }
        data['stderr'] = data['stdev']/np.sqrt(len(values))

        return data

    def print(self, droplet=False, order=['X', 'Y', 'N', 'T', 'M', 'U', 'V'],
            **kwargs):
        """
        Print data map fields to stdout. By default prints all cells, specify
        keywords droplet = True to only print those as part of droplet cells.
        The order of printed fields can be changed by supplying another.

        """

        def print_header(fields, order):
            """Print header from order."""

            for field in order:
                if field in fields:
                    print('%9c' % field, end=' ')
            print()
            for field in order:
                if field in fields:
                    print("----------", end='')
            print()

            return None

        def print_cell(cell, order):
            """Print cell in order."""

            for field in order:
                if field in cell:
                    print('%9.3f' % cell[field], end=' ')
            print()

            return None

        def to_print(cell, droplet):
            """Check if cell should be printed."""

            if not droplet:
                return True
            else:
                return cell['droplet']

        # If only part of droplet desired and not already controlled for,
        # control all cells
        if droplet and 'droplet' not in self.cells[0][0].keys():
            self.droplet(**kwargs)

        # Print header and then cells
        print_header(self.cells[0][0].keys(), order)
        for row in self.cells:
            for cell in row:
                if to_print(cell, droplet):
                    print_cell(cell, order)

        return None

    def save(self, _path, fields=['X', 'Y', 'N', 'T', 'M', 'U', 'V']):
        """
        Save data map to file at given path.

        A specific ordering of the written fields can be supplied through a
        list as _fields.

        Example:
            self.save(path_to_file, ['X', 'U', 'V', 'Y'])

        """

        with self.FlatArray(self.cells) as cells:
            with open(_path, 'w') as _file:
                # Write ordered header
                header = []
                for field in fields[:]:
                    if field in self.fields:
                        header.append('%s' % field)
                    else:
                        fields.remove(field)
                header = ' '.join(header) + '\n'
                _file.write(header)

                # Write all cells in header order
                for cell in cells:
                    line = []
                    for field in fields:
                        line.append('%f' % cell[field])
                    line = ' '.join(line) + '\n'
                    _file.write(line)

        return None

    def x(self, column):
        """Return the system position of column, i.e. along the x axis."""
        return self.cells[0, column]['X']

    def y(self, row):
        """Return the system position of row, i.e. along the y axis."""
        return self.cells[row, 0]['Y']

    def __cells_droplet(func):
        """
        Decorator for calling functions to test if cells are in droplets or
        not.

        Supplied func = func(cell) has to return a boolean of whether the
        cell is part of the droplet or not.

        """

        def wrapper(self, **kwargs):
            # Copy information into keywords for functions
            kwargs['cells'] = self.cells

            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    kwargs['position'] = {'column': j, 'row': i}
                    kwargs['cell'] = cell

                    cell['droplet'] = func(**kwargs)

            return None
        return wrapper

    def _sum_viscous_dissipation(self, width=1., delta_t=1.,
            N=1, viscosity=0.642e-3, mass_flow=False,
            force=False):
        """
        Returns the total amount of energy being dissipated in the system
        at this instant over a time frame set by delta_t.

        Force recalculation of viscous dissipation by supplying force=True.

        Options as for _calc_viscous_dissipation().

        """

        if force or 'visc_dissipation' not in self.cells[0][0].keys():
            self._calc_viscous_dissipation(N, viscosity, width, delta_t, mass_flow)

        energy = 0.
        for cell_row in self.cells:
            for cell in cell_row:
                energy += cell['visc_dissipation']

        return energy

    def _calc_cell_shear(self, N=1, mass_flow=False, if_droplet=False):
        """
        Calculate the fluid shear inside all cells by taking finite central
        differences over surrounding N cells. Shear in terms of 1/ps saved
        as keyword 'shear' in droplet cell dictionaries.

        Specify 'mass_flow = True' to base shear calculations on mass flow
        instead of absolute, 'if_droplet = True' to remove cells without
        shear from 'droplet' status.

        """

        def calc_central_difference(cells, direction, N, dx,
                diff_rows, diff_columns):
            """
            Calculate the central difference of cell flow along the
            specified direction.

            """

            def get_cell_indices(rows, columns):
                """Convert any combination of rows and columns to indices."""

                indices = (
                        {'row': rows[0], 'column': columns[0]},
                        {'row': rows[-1], 'column': columns[-1]}
                        )
                return indices

            if direction not in ['U', 'V']:
                raise KeyError("Selected flow direction must be 'U' or 'V'")

            indices = get_cell_indices(diff_rows, diff_columns)
            flow = [{}, {}]
            for i, index in enumerate(indices):
                # Control if cell in droplet
                if not cells[index['row']][index['column']]['droplet']:
                    raise Exception

                flow[i]['mass'] = cells[index['row']][index['column']]['M']
                flow[i]['flow'] = cells[index['row']][index['column']][direction]
                flow[i]['mass_flow'] = flow[i]['mass']*flow[i]['flow']

            if not mass_flow:
                difference = flow[1]['flow'] - flow[0]['flow']
            else:
                total_mass = flow[0]['mass'] + flow[1]['mass']
                if total_mass != 0.:
                    difference = (flow[1]['mass_flow'] - flow[0]['mass_flow'])/total_mass
                else:
                    difference = 0.

            if difference == 0.:
                return difference

            return difference/(2*N*dx)

        def shear_in_cell(cells, row, column, N, size, mass_flow):
            """
            Calculate the shear in one cell. Base calculations
            on mass flow by setting mass_flow to True.

            """

            dx = size['X']
            dy = size['Y']

            rows = [row - N, row + N]
            columns = [column - N, column + N]

            try:
                dudx = calc_central_difference(cells, 'U', N, dx, [row], columns)
                dvdx = calc_central_difference(cells, 'V', N, dx, [row], columns)
                dudy = calc_central_difference(cells, 'U', N, dy, rows, [column])
                dvdy = calc_central_difference(cells, 'V', N, dy, rows, [column])

                shear = np.sqrt(2*(dudx**2 + dvdy**2 - (1/3)*(dudx + dvdy)**2)
                        + (dudy + dvdx)**2)

            # Catch if some cell involved in calculation is not part of droplet
            except Exception:
                shear = 0.

            return shear

        size = self.info['cells']['size']

        for cell_row in self.cells:
            for cell in cell_row:
                cell['shear'] = 0.

        # Cell borders must be N deep
        for i, cell_row in enumerate(self.cells[N:-N]):
            row = i + N
            for j, cell in enumerate(cell_row[N:-N]):
                column = j + N
                if cell['droplet']:
                    shear = shear_in_cell(self.cells, row, column, N, size, mass_flow)
                    self.cells[row][column]['shear'] = shear

        # Remove droplets with zero shear from 'droplet' status
        if if_droplet:
            for row, cell_row in enumerate(self.cells):
                for column, cell in enumerate(cell_row):

                    if self.cells[row][column]['shear'] == 0.:
                        self.cells[row][column]['droplet'] = False

        return None

    def _calc_viscous_dissipation(self, N=1, viscosity=0.642e-3,
            width=1., delta_t=1., mass_flow=False):
        """
        Calculate the viscous energy dissipation for each cell in a liquid
        with given viscosity by taking finite central differences over
        surrounding N cells. A width and time step of system can be supplied
        to vary output units from energy dissipation per unit volume and time
        to absolute dissipation.

        Viscosity input is given in Pa*s, width in nm and delta_t in ps.

        Output energy dissipation is added as extra keyword 'visc_dissipation'
        in cell data dictionary and is given in MD units (kJ*mol-1).

        """

        def calc_central_difference(cells, direction, N, dx,
                diff_rows, diff_columns):
            """
            Calculate the central difference of cell flow along the
            specified direction.

            """

            def get_cell_indices(rows, columns):
                """Convert any combination of rows and columns to indices."""

                indices = (
                        {'row': rows[0], 'column': columns[0]},
                        {'row': rows[-1], 'column': columns[-1]}
                        )
                return indices

            if direction not in ['U', 'V']:
                raise KeyError("Selected flow direction must be 'U' or 'V'")

            indices = get_cell_indices(diff_rows, diff_columns)
            flow = [{}, {}]
            for i, index in enumerate(indices):
                flow[i]['mass'] = cells[index['row']][index['column']]['M']
                flow[i]['flow'] = cells[index['row']][index['column']][direction]
                flow[i]['mass_flow'] = flow[i]['mass']*flow[i]['flow']

            if not mass_flow:
                difference = flow[1]['flow'] - flow[0]['flow']
            else:
                total_mass = flow[0]['mass'] + flow[1]['mass']
                if total_mass != 0.:
                    difference = (flow[1]['mass_flow'] - flow[0]['mass_flow'])/total_mass
                else:
                    difference = 0.

            if difference == 0.:
                return difference

            return difference/(2*N*dx)

        def convert_viscosity(viscosity):
            """
            Convert viscosity from Pa*s to MD units kJ*ps*mol-1*nm-3.

            """

            return viscosity*(1e6/1.66054)

        def dissipation_in_cell(cells, row, column, viscosity,
                N, size, delta_t, mass_flow):
            """
            Calculate the viscous dissipation in one cell. Base calculations
            on mass flow by setting mass_flow to True.

            """

            dx = size['X']
            dy = size['Y']
            dz = size['Z']
            volume = dx*dy*dz

            rows = [row - N, row + N]
            columns = [column - N, column + N]

            dudx = calc_central_difference(cells, 'U', N, dx, [row], columns)
            dvdx = calc_central_difference(cells, 'V', N, dx, [row], columns)
            dudy = calc_central_difference(cells, 'U', N, dy, rows, [column])
            dvdy = calc_central_difference(cells, 'V', N, dy, rows, [column])

            dissipation_per_time_and_volume = viscosity*(2*(dudx**2 + dvdy**2
                    - (1/3)*(dudx + dvdy)**2) + (dudy + dvdx)**2)

            return dissipation_per_time_and_volume*volume*delta_t

        size = self.info['cells']['size']
        size['Z'] = width

        viscosity = convert_viscosity(viscosity)

        for cell_row in self.cells:
            for cell in cell_row:
                cell['visc_dissipation'] = 0.

        for i, cell_row in enumerate(self.cells[N:-N]):
            row = i + N
            for j, cell in enumerate(cell_row[N:-N]):
                column = j + N
                if cell['droplet']:
                    dissipation = dissipation_in_cell(self.cells, row, column,
                            viscosity, N, size, delta_t, mass_flow)
                    self.cells[row][column]['visc_dissipation'] = dissipation

        return None

    @__cells_droplet
    def _cells_flow(cell, **kwargs):
        """
        Check if a cell contains any flow, decorated to check entire system.

        """

        return cell['U'] or cell['V']

    @__cells_droplet
    def _cells_min_mass(cell, **kwargs):
        """
        Check if cell contains mass above an input minimum, decorated to
        check entire system.

        Example:
            self.min_mass(min_mass = 25.4)

        """

        if cell['M'] == 0.:
            return False
        else:
            return cell['M'] >= kwargs.get('min_mass', 0.)

    @__cells_droplet
    def _cells_inside(cells, position, **kwargs):
        """
        Check if cell at position is well connected to other droplet
        cells, by going over a set of cells in columns around the considered,
        checking if any column within this range has a 'droplet' cell in the
        row above the current. If so, it is controlled if this cell is
        connected by 'droplet' cells to the initial cell.

        The number of columns by default is one in each direction around the
        initial cell. This can be changed by supplying the keyword argument
        columns = number.

        Example:
            self.inside(columns = 3) controls three columns on each side of
            the cell, inside the same row.

        A large column number may not cut out the precursor film on the
        substrate.

        Depends on 'droplet' status being set in cells already, since it only
        removes.

        """

        num_columns = kwargs.get('columns')
        row = position['row']
        column = position['column']

        # Add upper and lower rows to look in, inside of system
        check_rows = list(filter(
                lambda x: x >= 0 and x < cells.shape[0],
                [row + 1, row - 1]
                ))

        # Similarly for columns numbers to left and right
        check_columns = [
                list(filter(lambda x: x >= 0 and x < cells.shape[1], column))
                for column in [
                    range(column, column + num_columns + 1, 1),
                    range(column, column - num_columns - 1, -1)
                    ]
                ]

        # Go through rows and columns to left and right
        for other_row in check_rows:
            for dir_columns in check_columns:
                for other_column in dir_columns:
                    # If not connected in own row break,
                    # connection found if connected in own and other row
                    if not cells[row][other_column]['droplet']:
                        break
                    elif cells[other_row][other_column]['droplet']:
                        return True

        return False

    def _get_interface(self):
        """
        Returns separated lists of X and Y coordinates of interface.

        X, Y = self._get_interface()

        """

        coordinates = self.interface()
        X = [coord[0] for coord in coordinates]
        Y = [coord[1] for coord in coordinates]

        return X, Y

    def _interface_length(self):
        """
        Returns the total length of the droplet interface.

        """

        length = 0.
        interface = self.interface()

        for i, _ in enumerate(interface[:-1]):
            dx = interface[i+1][0] - interface[i][0]
            dy = interface[i+1][1] - interface[i][1]
            length += np.sqrt(dx**2 + dy**2)

        return length

    def _read(self):
        """
        Reads information from the data map. Saves cell array in self.cells.

        """

        def is_binary(_path, checksize=512):
            """
            Returns True of data file is binary format, else False.

            """

            with open(_path, 'r') as _file:
                try:
                    line = _file.read(checksize)
                    if '\n' in line:
                        return False
                    else:
                        raise UnicodeDecodeError

                except UnicodeDecodeError:
                    return True

        def read_binary(_path, bytes_per_val=4):
            """
            Read the data from a binary data file.

            """

            def bytes_from_file(_path, chunksize=7168):
                """
                Read and return chunks of bytes from file.

                """

                with open(_path, 'rb') as _file:
                    while True:
                        chunk = _file.read(chunksize)
                        if chunk:
                            yield chunk
                        else:
                            break

                return None

            # Order of fields must not change
            fields = ['X', 'Y', 'N', 'T', 'M', 'U', 'V']
            data = {field: None for field in fields}
            size = bytes_per_val * len(fields)
            cells = []

            for chunk in bytes_from_file(_path):
                lines = [chunk[i:i+size] for i in range(0, len(chunk), size)]
                for line in lines:
                    for i, value in enumerate(struct.unpack('fffffff', line)):
                        data[fields[i]] = value
                    cells.append(data.copy())

            return cells

        def read_plaintext(_path, fields):
            """
            Read the data from a plain text data file.

            """

            data = {field: None for field in fields}
            cells = []

            with open(_path, 'r') as _file:
                # Assert that header contains desired fields
                header = _file.readline().strip().upper().split()
                if not fields.issubset(header):
                    raise Exception

                # Read in header order until EOF
                line = _file.readline().strip().split()
                while line:
                    for i, add in enumerate(line):
                        if header[i] in self.fields:
                            data[header[i]] = float(add)
                    cells.append(data.copy())
                    line = _file.readline().strip().split()

            return cells

        if is_binary(self.path):
            cells = read_binary(self.path)
        else:
            cells = read_plaintext(self.path, self.fields)

        self.cells = np.array(cells)

    def _grid(self):
        """Rearrange data map cells into 2d numpy array."""

        _info = self.info
        self.cells.resize(
                _info['cells']['num_cells']['X'],
                _info['cells']['num_cells']['Y']
                )
        self.cells = self.cells.transpose()
        return None
