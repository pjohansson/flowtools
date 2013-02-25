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

    Methods:
        self.com - get the center of mass of the system
        self.cut - return a new DataMap with cells inside a specified cut
        self.droplet - mark cells as 'droplet' or not depending on
            conditions
        self.fields - get the fields of the droplet
        self.floor - get the lowest row of the system with 'droplet' cells
        self.info - get information from the DataMap
        self.save - save the DataMap to a file

    """

    def __init__(self, _path, **kwargs):
        self.fields = kwargs.pop('fields', 'all')
        self.path = _path

        # Read if given path, otherwise keep empty
        if self.path:
            self._read()
            self._info = self.info
            self._grid()
            self.droplet()

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

    @property
    def floor(self):
        """Returns the floor of the system, i.e. the lowest row occupied by
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

    def cut(self, **kwargs):
        """Cut out a certain part of the system, specified by keywords
        'cutx' = [min(x), max(x)] and 'cuty' = [min(y), max(y)] in system
        positions that should be kept.

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

        # Get information
        _info = self._info

        # Check system limits
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
        data_map._info = data_map.info
        return data_map

    def droplet(self, **kwargs):
        """Check entire system for droplet cells, flagging 'droplet' as
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
        self._flow()
        self._min_mass(min_mass = min_mass)
        self._inside(columns = columns)

        return None

    def __cells_droplet(func):
        """Decorator for calling functions to test if cells are in droplets or
        not.

        Supplied func = func(cell) has to return a boolean of whether the
        cell is part of the droplet or not.

        """

        def wrapper(self, **kwargs):
            # Copy information into keywords for functions
            kwargs['cells'] = self.cells

            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    # Copy cell information to keywords
                    kwargs['pos'] = {'column': j, 'row': i}
                    kwargs['cell'] = cell

                    # Default 'droplet' to True
                    # Keep as True only if, and checker function returns it
                    if not (
                            cell.setdefault('droplet', True)
                            and func(**kwargs)
                            ):
                        cell['droplet'] = False

            return None
        return wrapper

    @__cells_droplet
    def _flow(cell, **kwargs):
        """Check if a cell contains any flow, decorated to check entire system.

        """

        return cell['U'] or cell['V']

    @__cells_droplet
    def _min_mass(cell, **kwargs):
        """Check if cell contains mass above an input minimum, decorated to
        check entire system.

        Example:
            self.min_mass(min_mass = 25.4)

        """

        return cell['M'] >= kwargs.get('min_mass', 0.)

    @__cells_droplet
    def _inside(cells, pos, **kwargs):
        """Check if cell at position pos is well connected to other droplet
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

        Depends on 'droplet' status being set in cells already.

        """

        def check_cell(check, row, cell, cells):
            """Return True if column 'cell' is well connected to cell on
            row above or belove 'row', starting at column 'check'.

            """

            # Get row to check
            if row < cells.shape[0] - 1:
                row += 1
            else:
                row -= 1

            # Get sign for movement
            sign = int(math.copysign(1, cell - check))

            # Check if first check cell is droplet,
            # then move to original and break if bad connection is found
            if cells[row, check]['droplet']:
                for column in list(range(check, cell, sign)):
                    if (not cells[row, column]['droplet']
                            and not cells[row, column + sign]['droplet']):
                        return False
            else:
                return False
            return True

        # Set width and get shape of system into dict
        width = kwargs.get('columns', 1)
        _shape = dict(list(zip(['rows', 'columns'], cells.shape)))

        # Go through columns inside width
        columns = list(range(
            pos['column'] - width, pos['column'] + width + 1
            ))
        columns.remove(pos['column'])

        for i in columns:
            # If current column inside row and connection found, return True
            if (0 <= i < _shape['columns']
                    and check_cell(i, pos['row'], pos['column'], cells)):
                return True
        return False

    def _read(self):
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

    def _grid(self):
        """Rearrange data map cells into 2d numpy array."""

        _info = self._info
        self.cells.resize(
                _info['cells']['num_cells']['X'],
                _info['cells']['num_cells']['Y']
                )
        self.cells = self.cells.transpose()
        return None
