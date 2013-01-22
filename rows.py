"""Module containing tools for rows in data maps."""

from util import reset_fields
from numpy import floor

def find_cells_in_row(row, flowmap, system):
    """Finds filled cells in a row from a flow map. Checks that cells are well
    connected."""

    fields = {'X', 'Y', 'U', 'V'}
    calc_row_y(row, system)
    reset_fields(row, fields)

    for i, pos_y in enumerate(flowmap['Y']):
        if row['y_min'] < pos_y <= row['y_max']:
            for field in fields:
                row[field].append(flowmap[field][i])

    return None

def find_edges_in_row(row, system):
    """Simple function to find the edges of a row, saved to row['edges'].
    If row is empty, so is the value set to."""

    if row['X'] != []:
        edge_min = min(row['X']) - system['celldimensions'][0] / 2
        edge_max = max(row['X']) + system['celldimensions'][0] / 2
        row['edges'] = [edge_min, edge_max]
    else:
        row['edges'] = []

    return None

def keep_droplet_cells_in_row(row, flowmap, system, above = True):
    """Goes through all cells in a row and controls if it is well connected 
    to a layer above it. If not it is discarded.
    
    Instead of the layer above, the one below can be controlled by giving
    the final input as above = False."""

    fields = {'X', 'Y', 'U', 'V'}

    if above:
        row_two = {'num' : row['num'] + 1}
        row_three = {'num' : row['num'] + 2}
    else:
        row_two = {'num' : row['num'] - 1}
        row_three = {'num' : row['num'] - 2}

    find_cells_in_row(row_two, flowmap, system)
    find_cells_in_row(row_three, flowmap, system)

    keep = {field : [] for field in fields}

    for i, pos_x in enumerate(row['X']):
        if control_cell(pos_x, row_two, row_three, system):
            for field in fields:
                keep[field].append(row[field][i])

    for field in fields:
        row[field] = keep[field]

    return None

def keep_droplet_cells_in_system(flowmap, system):
    """Remove all cells not part of droplet from flowmap."""

    row = {}
    fields = {'X', 'Y', 'U', 'V'}

    row_min = find_row(min(flowmap['Y']), system)
    row_max = find_row(max(flowmap['Y']), system)

    keep = {field : [] for field in fields}

    for row['num'] in range(row_min, row_max + 1):
        find_cells_in_row(row, flowmap, system)

        if row['num'] < row_max - 1:
            keep_droplet_cells_in_row(row, flowmap, system, above = True)
        else:
            keep_droplet_cells_in_row(row, flowmap, system, above = False)
        
        for field in fields:
            if row['X'] != []:
                for value in row[field]:
                    keep[field].append(value)

    for field in fields:
        flowmap[field] = keep[field]

    return None

def find_row(height, system):
    """Returns the corresponding cell row of the system for a certain height."""

    relative_position = height - ( system['initdisplacement'][1] - \
            system['celldimensions'][1] / 2 )
    row = int( floor(relative_position / system['celldimensions'][1]) )

    return row

def control_cell(pos_x, row_two, row_three, system):
    """Controls if a cell is well connected to two layer above it, that is
    if if a link can be created between it and the layer."""

    x_min_row_two = pos_x - 1.5 * system['celldimensions'][0]
    x_max_row_two = pos_x + 1.5 * system['celldimensions'][0]

    success = False

    for cell_row_two, pos_x_row_two in enumerate(row_two['X']):

        if x_min_row_two <= pos_x_row_two < x_max_row_two:
            x_min_row_three = pos_x_row_two - 1.5 * system['celldimensions'][0]
            x_max_row_three = pos_x_row_two + 1.5 * system['celldimensions'][0]

            for cell_row_three, pos_x_row_three in enumerate(row_three['X']):
                if x_min_row_three <= pos_x_row_three < x_max_row_three:
                    success = True

    return success

def calc_row_y(row, system):
    """Calculates the minimum, maximum and center position in y for a 
    given cell row."""

    row['y_min'] = system['initdisplacement'][1] + system['celldimensions'][1] * (row['num'] - 0.5)
    row['y_max'] = row['y_min'] + system['celldimensions'][1]
    row['Y'] = row['y_min'] + system['celldimensions'][1] / 2

    return None
