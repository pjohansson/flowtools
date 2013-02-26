"""
Classes and tools for visualising the spreading of droplets on substrates.

Classes:
    Spread - spreading of a droplet

Functions:
    edges - find the edges of a DataMap for a specific row, or floor
    plot - plot a Spread object

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
        self.times - add times to spreading from delta_t
        self.spread - the spreading, including frames, of the system
        self.system - the System object connected to the spread

    """

    def __init__(self, system, delta_t=None):
        # Initiate system with keywords
        self.system = system

        # If no floor set, find
        if not self.system.floor:
            self.system.find_floor()

        self.collect(delta_t)

        return None

    def collect(self, delta_t=None):
        """
        Collect edges from all DataMap objects in system to self.spread.

        """

        # Reset spread
        self.spread = {
                'left': [], 'right': [], 'frames': [], 'cells': [], 'times': []
                }

        for i, _file in enumerate(self.system.datamaps):
            datamap = DataMap(_file)
            _edges = edges(datamap, floor = self.system.floor)

            # Append if _edges not empty
            if _edges:
                self._add(_edges, i, datamap)

        # Get times
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

        delta_t = kwargs.pop('delta_t', None)
        if not delta_t:
            delta_t = self.system.delta_t

        try:
            for frame in self.spread['frames']:
                self.spread['times'].append(delta_t * (frame - start))
        except TypeError:
            print("'delta_t' not in self.system.delta_t or submitted.")

        return None

    def _add(self, _edges, num, datamap):
        """Add edges of droplet to spread."""

        # Add datamap number
        self.spread['frames'].append(num)

        # Add cell numbers
        self.spread['cells'].append(_edges)

        # Add system position of edges; adjust to edge positions of cells!
        size = datamap._info['cells']['size']['X']
        self.spread['left'].append(datamap.x(_edges[0]) - size/2)
        self.spread['right'].append(datamap.x(_edges[1]) + size/2)

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
    for i, cell in enumerate(row):
        if cell['droplet'] and not left:
            left = i
        if cell['droplet']:
            right = i

    return [left, right]

@draw
def plot(spread):


    return None
