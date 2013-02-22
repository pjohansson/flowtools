import math
import numpy as np

class FlowSystem(object):
    """A system and corresponding information."""

    def __init__(self):
        pass


class DataMap(object):
    """A data map for flow field data from simulations.

    Contains cell information in self.cells, arranged into a 2d numpy array
    where the first index contains row and the second column number of cells.

    Example:
        DataMap('include/datamap.dat') returns a DataMap with cells read from
        the file 'include/datamap.dat'.

        self.cells[:, 10] returns cell information of all rows in the eleventh
        column.

        self.cells[16:22, 12:16] returns cell information of a small, cut box
        of the system.

    """

    def __init__(self, _path, _fields='all'):
        self.fields = _fields
        self.path = _path

        # Read if given path, otherwise keep empty
        if self.path:
            self.read()
            self.grid()

        return None

    class FlatArray(object):
        """Context manager for flattening arrays for certain operations,
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
    def fields(self):
        """Data fields contained in cells."""
        return self._fields

    @fields.setter
    def fields(self, _fields):
        """Sets which fields the data map contains.

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

    def read(self):
        """Reads information from the data map. Saves cell array in self.cells.

        """

        data = {field: None for field in self.fields}
        cells = []

        with open(self.path, 'r') as _file:
            # Assert that header contains desired fields
            header = _file.readline().strip().upper().split()
            if not self.fields.issubset(header):
                raise Exception

            # Read in header order until EOF
            line = _file.readline().strip().split()
            while line:
                for i, add in enumerate(line):
                    if header[i] in self.fields:
                        data[header[i]] = float(add)
                cells.append(data.copy())
                line = _file.readline().strip().split()

        self.cells = np.array(cells)
        return None

    def save(self, _path, fields=['X', 'Y', 'N', 'T', 'M', 'U', 'V']):
        """Save data map to file at given path.

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

    def info(self):
        """Scans cells for information data. Returns as dict()."""

        # Initiate total dictionary
        _info = {
                'cells': {},
                'size': {'X': [], 'Y': []}
                }

        with self.FlatArray(self.cells) as cells:
            # Find system size
            Dx = [self.cells[0]['X'], cells[-1]['X']]
            Dy = [self.cells[0]['Y'], cells[-1]['Y']]

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

    def grid(self):
        """Rearrange data map cells into 2d numpy array."""

        _info = self.info()
        self.cells.resize(
                _info['cells']['num_cells']['X'],
                _info['cells']['num_cells']['Y']
                )
        self.cells = self.cells.transpose()
        return None

    def cut(self, cutx, cuty):
        """Cut out a certain part of the system, specified by arrays cutx =
        [min(x), max(x)] and cuty = [min(y), max(y)] in system positions that
        should be kept.

        Returns a DataMap of the newly cut system, leaving the original intact.

        Example:
            self.cut([13.5, 20.0], [-2, 10])

        """

        def max_cell(cut, start, size, top_cell):
            return min(top_cell, math.floor((cut - start) / size - 0.5))

        def min_cell(cut, start, size):
            return max(0, math.ceil((cut - start) / size + 0.5))

        def min_max_cell(cut, start, size, num_cells):
            cut_cell_min = min_cell(cut[0], start, size)
            cut_cell_max = max_cell(cut[1], start, size, num_cells)
            return [cut_cell_min, cut_cell_max]

        # Get information
        _info = self.info()
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
        cells = {
                'X': min_max_cell(
                    cutx, start['X'], cell_size['X'], num_cells['X']
                    ),
                'Y': min_max_cell(
                    cuty, start['Y'], cell_size['Y'], num_cells['Y']
                    )
                }

        # Create and copy cut data map
        data_map = DataMap(None)
        data_map.cells = self.cells[
                cells['Y'][0]:(cells['Y'][1] + 1),
                cells['X'][0]:(cells['X'][1] + 1)
                ]
        return data_map

    def com(self):
        """Returns center of mass of map as dict()."""

        _com = {'X': 0, 'Y': 0}
        _mass = 0

        try:
            with self.FlatArray(self.cells) as cells:
                for cell in cells:
                    _com['X'] += cell['X'] * cell['M']
                    _com['Y'] += cell['Y'] * cell['Y']
                    _mass += cell['M']
                _com['X'] /= _mass
                _com['Y'] /= _mass

        except KeyError:
            print("No mass in data map.")

        return _com

    def __droplet(func):
        """Decorator for calling functions to test if cells are in droplets or
        not.

        Supplied func = func(cell) has to return a boolean of whether the
        cell is part of the droplet or not.

        """

        def wrapper(self, **kwargs):
            with self.FlatArray(self.cells) as _cells:
                for cell in _cells:
                    # Start from True before removing
                    if 'droplet' not in cell.keys():
                        cell['droplet'] = True

                    # All conditions must hold
                    if not (cell['droplet'] and func(cell, **kwargs)):
                        cell['droplet'] = False

            return None
        return wrapper

    @__droplet
    def flow(cell, **kwargs):
        """Check if a cell contains any flow, decorated to check entire system.

        """

        return cell['U'] or cell['V']

    @__droplet
    def min_mass(cell, **kwargs):
        """Check if cell contains mass above an input minimum, decorated to
        check entire system.

        Example:
            self.min_mass(min_mass = 25.4)

        """

        return cell['M'] >= kwargs.get('min_mass', 0.)
