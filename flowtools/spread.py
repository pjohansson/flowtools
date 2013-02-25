from flowtools.datamaps import DataMap
from flowtools.draw import draw

def edges(datamap, **kwargs):
    """Return the positions of the edges of a droplet in a DataMap.

    Options for DataMap.droplet can be input as keyword arguments.

    """

    datamap.droplet(**kwargs)

    # Get row of floor cells
    floor = datamap.floor
    if floor == None:
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
