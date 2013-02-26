from flowtools.datamaps import DataMap, System, create_filenames
from flowtools.draw import draw

def spread(system, **kwargs):
    """
    Finds the edges of droplet at a certain floor for all DataMap objects
    in system, returns as dictionary with edges and corresponding datamap
    numbers in the system.datamaps list.

    The floor can be input using the keyword 'floor', otherwise it is
    calculated using system.find_floor. Keywords can also be provided as
    for edges.

    By default the spread is adjusted to the center of mass of the system
    at the impact frame, change this by inputting the keyword 'com'
    as False.

    Returns an array of the spreading in positions for each frame.

    """

    def add_spread(_spread, _edges, num, datamap):
        """Add edges of droplet to spread."""

        # Add datamap number
        _spread['frames'].append(num)

        # Add cell numbers
        _spread['cells'].append(_edges)

        # Add system position of edges; adjust to edge positions of cells!
        size = datamap._info['cells']['size']['X']
        _spread['left'].append(datamap.x(_edges[0]) - size/2)
        _spread['right'].append(datamap.x(_edges[1]) + size/2)

        return None

    def adjust_com(system, _spread):
        """
        Adjust the spread of the droplet around the center of the mass of
        the system at impact.

        """

        # Get COM from system
        impact = _spread['frames'][0]
        com = DataMap(system.datamaps[impact]).com

        # Adjust for all frames
        for i, _ in enumerate(_spread['frames']):
            _spread['left'][i] -= com['X']
            _spread['right'][i] -= com['X']

        return None

    # Find or set floor
    floor = kwargs.pop('floor', None)
    if not floor:
        system.find_floor()
        floor = system.floor

    # Collect spreading
    _spread = {'left': [], 'right': [], 'cells': [], 'frames': []}
    for i, _file in enumerate(system.datamaps):
        datamap = DataMap(_file, **kwargs)
        _edges = edges(datamap, floor = floor)

        # Append if _edges not empty
        if _edges:
            add_spread(_spread, _edges, i, datamap)

    # Adjust for COM
    if kwargs.pop('com', True):
        adjust_com(system, _spread)

    return _spread

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
def plot():
    return None
