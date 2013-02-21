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
        self.cells[:, 10] returns cell information of all rows in the eleventh
        column.

        self.cells[16:22, 12:16] returns cell information of a small, cut box
        of the system.

    """

    def __init__(self, _path, _fields='all'):
        self.fields = _fields
        self._path = _path

        # Read if given path, otherwise keep empty
        if self._path:
            self.read()
            self.grid()

        return None

    @property
    def path(self):
        """Path to the data map file."""
        return self._path

    @path.setter
    def path(self, _path):
        self._path = _path
        self.read()
        return None

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

    def save(self, _path, _fields=['X', 'Y', 'N', 'T', 'M', 'U', 'V']):
        """Save data map to file at given path.

        A specific ordering of the written fields can be supplied through a
        list as _fields.

        Example:
            self.save(path_to_file, ['X', 'U', 'V', 'Y'])

        """

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
            for cell in self.cells:
                line = []
                for field in fields:
                    line.append('%f' % cell[field])
                line = ' '.join(line) + '\n'
                _file.write(line)

        return None

    def information(self):
        """Scans cells for information data. Returns as dict()."""

        # Initiate total dictionary
        _information = {
                'cells': {},
                'size': {'X': [], 'Y': []}
                }

        # Flatten
        _shape = self.cells.transpose().shape
        self.cells = self.cells.transpose().ravel()

        # Find system size
        Dx = [self.cells[0]['X'], self.cells[-1]['X']]
        _information['size']['X'] = Dx
        Dy = [self.cells[0]['Y'], self.cells[-1]['Y']]
        _information['size']['Y'] = Dy

        # Initiate with total number of cells
        cellinfo = {
                'total_cells': len(self.cells),
                'num_cells': {},
                'size': {}
                }

        # Find number of cells in each direction
        numcells = {'X': 0, 'Y': 0}
        x = self.cells[0]['X']
        while x == self.cells[numcells['Y']]['X']:
            numcells['Y'] += 1
        numcells['X'] = cellinfo['total_cells'] // numcells['Y']
        cellinfo['num_cells'] = numcells

        # Find cell dimensions
        cellinfo['size']['X'] = (self.cells[cellinfo['num_cells']['Y']]['X']
                - self.cells[0]['X'])
        cellinfo['size']['Y'] = self.cells[1]['Y'] - self.cells[0]['Y']

        _information['cells'] = cellinfo

        # Restore shape
        self.cells.resize(_shape)
        self.cells = self.cells.transpose()
        return _information

    def grid(self):
        """Rearrange data map cells into 2d numpy array."""

        information = self.information()
        self.cells.resize(
                information['cells']['num_cells']['X'],
                information['cells']['num_cells']['Y']
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
        information = self.information()
        start = {
                'X': information['size']['X'][0],
                'Y': information['size']['Y'][0]
                }
        cell_size = {
                'X': information['cells']['size']['X'],
                'Y': information['cells']['size']['Y']
                }
        num_cells = information['cells']['num_cells']

        # Find cell interval to keep
        cells = {
                'X': min_max_cell(
                    cutx, start['X'], cell_size['X'], num_cells['X']
                    ),
                'Y': min_max_cell(
                    cuty, start['Y'], cell_size['Y'], num_cells['Y']
                    )
                }

        # Create and copy data map
        data_map = DataMap(None)
        data_map.cells = self.cells[
                cells['Y'][0]:(cells['Y'][1] + 1),
                cells['X'][0]:(cells['X'][1] + 1)
                ]
        return data_map
