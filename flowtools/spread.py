from flowtools.datamaps import DataMap, System, create_filenames
from flowtools.draw import draw

def spread(system, **kwargs):
    """
    Finds the edges of droplet at a certain floor for all DataMap objects
    in system.

    The floor can be input using the keyword 'floor', otherwise it is
    calculated using system.find_floor. Keywords can also be provided as
    for edges.

    Returns an array of the spreading in positions for each frame.

    """

    # Find or set floor
    floor = kwargs.pop('floor', None)
    if not floor:
        system.find_floor()
        floor = system.floor

    # Collect spreading
    spread = {'left': [], 'right': []}
    for file in system.datamaps:
        with system.open(file, **kwargs) as datamap:
            [left, right] = edges(datamap, floor = floor)

        spread['left'].append(left)
        spread['right'].append(right)

    return spread

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
