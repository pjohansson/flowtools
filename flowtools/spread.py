"""
Classes and tools for visualising the spreading of droplets on substrates.

Classes:
    Spread - spreading of a droplet

Functions:
    edges - find the edges of a DataMap for a specific row, or floor

"""

import pylab as plt

from flowtools.datamaps import DataMap, System, create_filenames
from flowtools.draw import draw

class Spread(object):
    """
    Class for a spreading dictionary of a system.

    Initialised with a System and optionally a keyword 'delta_t' for the
    time difference between DataMap objects.

    Methods:
        self.com - adjusts the spreading edges to the center of mass
        self.collect - collect the spreading edges to self.spread
        self.plot - plot the spreading
        self.times - add times to spreading from delta_t
        self.spread - the spreading, including frames, of the system
        self.system - the System object connected to the spread

    """

    def __init__(self, system=None, **kwargs):
        # If file to read supplied, else collect from system
        if kwargs.get('read', False):
            self.read(kwargs.get('read'))
        else:
            # Initiate system with keywords
            self.system = system

            # If no floor set, find
            if not self.system.floor:
                self.system.find_floor()

            self.collect(**kwargs)

        return None

    def collect(self, **kwargs):
        """
        Collect edges from all DataMap objects in system to self.spread.

        Keywords:
            columns - setting for DataMap.droplet when asserting if cell is
                inside droplet
            dist - True (default) or False, collect distance to center of mass
            min_mass - minimum mass for cells to count

        """

        delta_t = kwargs.pop('delta_t', None)
        dist = kwargs.pop('dist', True)
        self.min_mass = kwargs.setdefault('min_mass', self.system.min_mass)
        self.floor = self.system.floor
        _print = kwargs.pop('print', False)

        # Reset spread
        self.spread = {
                'left': [], 'right': [], 'cells': [],
                'frames': [], 'times': [], 'dist': []
                }

        for i, _file in enumerate(self.system.datamaps):
            if _print:
                print("\bReading '%s' (%d of %d)"
                        % (_file, i + 1, len(self.system.datamaps)))

            datamap = DataMap(_file, min_mass = self.min_mass)
            _edges = edges(datamap, floor = self.floor,
                    min_mass = self.min_mass)

            # Append if _edges not empty
            if _edges:
                self._add(_edges, i, datamap, dist = dist)

        # Get times
        if delta_t:
            self.times(delta_t = delta_t)

        return None

    def com(self):
        """
        Adjust the spread of the droplet around the center of the mass of
        the system at impact.

        """

        # Get COM from system
        impact = self.spread['frames'][0]
        com = DataMap(self.system.datamaps[impact]).com

        # Adjust for all frames
        for i, _ in enumerate(self.spread['frames']):
            self.spread['left'][i] -= com['X']
            self.spread['right'][i] -= com['X']

        return None

    def dist(self):
        """
        Add a keyword 'dist' to self.spread, filling it with a list
        of the distance between the floor and the center of mass of the
        droplet for corresponding frames.

        """

        self.spread['dist'] = []

        for datamap in self.system.datamaps:
            _map = DataMap(datamap)
            com = _map.com.get('Y')
            floor = _map.y(self.system.floor)

            self.spread['dist'].append(com - floor)

        return None

    def plot(self, **kwargs):
        """
        Draw the spread as a function of frames or times.

        Keywords:
            frames - True or False (default to draw as a function of frames
            times - True (default) or False to draw as a function of time
            Others as for draw.draw

        """

        @draw
        def plot_lines(**kwargs):
            """Plot the spread as a function of supplied list."""

            spread = kwargs.pop('spread')
            x = kwargs.pop('x')

            kwargs.setdefault('color', 'blue')
            label = kwargs.pop('label', None)

            plt.plot(x, spread['left'], label = label, **kwargs)
            plt.plot(x, spread['right'], label = '_nolegend_', hold = True,
                    **kwargs)


            return None

        times = kwargs.pop('times', False)
        frames = kwargs.pop('frames', False)
        dist = kwargs.pop('dist', False)

        kwargs.update({'spread': self.spread})
        kwargs.update({'figure': False})
        kwargs.setdefault('ylabel', 'Positions (nm)')
        kwargs.setdefault('title', 'Spreading of droplet on substrate')

        if self.spread['times'] and times:
            kwargs.update({'x': self.spread['times']})
            kwargs.setdefault('xlabel', 'Time (ps)')
            kwargs.setdefault('axis', 'equal')

            plot_lines(**kwargs)

        if self.spread['frames'] and frames:
            kwargs.update({'x': self.spread['frames']})
            kwargs.setdefault('xlabel', 'Frame')
            kwargs.setdefault('axis', 'equal')

            plot_lines(**kwargs)

        if self.spread['dist'] and dist:
            kwargs.update({'x': self.spread['dist']})
            kwargs.setdefault(
                    'xlabel', 'Distance from substrate to center of mass (nm)'
                    )
            kwargs.setdefault('axis', 'normal')

            plot_lines(**kwargs)

            # Invert x axis for distance
            plt.gca().invert_xaxis()

        return None

    def read(self, _path):
        """Read spread information from a file at _path."""

        self.spread = {
                'left': [], 'right': [], 'cells': [],
                'frames': [], 'times': [], 'dist': []
                }

        with open(_path) as _file:
            frame = _file.readline().strip().split()[-1]
            floor = _file.readline().strip().split()[-1]
            min_mass = _file.readline().strip().split()[-1]

            frame = int(frame)
            self.floor = int(floor)
            self.min_mass = float(min_mass)

            line = _file.readline().strip()
            while line.strip().split() != ['left', 'right', 'times', 'dist']:
                line = _file.readline().strip()

            line = _file.readline().strip()
            while line:
                (left, right, times, dist) = line.split()

                self.spread['left'].append(float(left))
                self.spread['right'].append(float(right))
                self.spread['times'].append(float(times))
                self.spread['dist'].append(float(dist))
                self.spread['frames'].append(frame)

                frame += 1

                line = _file.readline()

        return None

    def save(self, _path):
        """Save the spread information to a file at _path."""

        spread = self.spread

        with open(_path, 'w') as _file:
            # Write general information
            _file.write('Impact frame: %d\n' % spread['frames'][0])
            _file.write('Floor: %d\n' % self.floor)
            _file.write('Min mass: %d\n' % self.min_mass)
            _file.write('\n')

            # Write header and then fields
            header = '%8s %8s %8s %8s\n' % ('left', 'right', 'times', 'dist')
            _file.write(header)

            for i, _ in enumerate(self.spread['frames']):
                line = ('%8.3f %8.3f %8.3f %8.3f\n'
                        % (spread['left'][i], spread['right'][i],
                            spread['times'][i], spread['dist'][i]))
                _file.write(line)

            return None

    def times(self, **kwargs):
        """
        Adds a keyword 'times' to self.spread containing corresponding
        times of the keyword 'frames', using self.system.delta_t as a
        time difference between frames.

        By default these are absolute times
        counting the times from the start of the system, this can be
        changed with the keyword 'relative'.

        Keywords:
            relative - True or False (default). If True, counts the time
                with the first frame in self.spread['frames'] as t = 0.
                Otherwise the maybe non-zero datamaps position number will
                be used as a starting point.
            delta_t - If submitted, uses this value as a time difference
                between DataMap objects instead of self.system.delta_t.

        """

        start = 0
        if kwargs.pop('relative', False):
            start = self.spread['frames'][0]

        self.delta_t = kwargs.pop('delta_t', None)
        if not self.delta_t:
            self.delta_t = self.system.delta_t

        self.spread['times'] = []

        try:
            for frame in self.spread['frames']:
                self.spread['times'].append(self.delta_t * (frame - start))
        except TypeError:
            print("'delta_t' not in self.system.delta_t or submitted.")

        return None

    def _add(self, _edges, num, datamap, dist):
        """Add edges of droplet to spread."""

        # Add datamap number
        self.spread['frames'].append(num)

        # Add cell numbers
        self.spread['cells'].append(_edges)

        # Add system position of edges; adjust to edge positions of cells!
        size = datamap._info['cells']['size']['X']
        self.spread['left'].append(datamap.x(_edges[0]) - size/2)
        self.spread['right'].append(datamap.x(_edges[1]) + size/2)

        # If distance demanded, add
        if dist:
            com = datamap.com.get('Y')
            floor = datamap.y(self.system.floor)
            self.spread['dist'].append(com - floor)

        return None


def edges(datamap, **kwargs):
    """
    Return the positions of the edges of a droplet in a DataMap.

    Options for DataMap.droplet can be input as keyword arguments. A floor
    can be set by the keyword 'floor', otherwise it is searched for.

    """

    datamap.droplet(**kwargs)

    # Get row of floor cells
    floor = kwargs.pop('floor', None)
    if not floor:
        floor = datamap.floor
        if not floor:
            return []

    row = datamap.cells[floor, :]

    # Find edges
    left = None
    _edges = []
    for i, cell in enumerate(row):
        if cell['droplet'] and not left:
            left = i
        if cell['droplet']:
            right = i
            _edges = [left, right]

    return _edges
