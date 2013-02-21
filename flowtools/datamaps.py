import numpy as np


class DataMap(object):
    """A data map for flow field data from simulations."""

    def __init__(self, _path, _fields='all'):
        self.fields = _fields
        self.path = _path

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
