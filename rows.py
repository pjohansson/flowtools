"""Module containing tools for rows in data maps."""

from util import reset_fields

def find_cells_in_row(row, flowmap, system):
    """Finds filled cells in a row from a flow map. Checks that cells are well
    connected."""

    fields = {'X', 'U', 'V'}
    reset_fields(row, fields)
    calc_row_y(row, system)

    for i, pos_y in enumerate(flowmap['Y']):
        if row['y_min'] < pos_y <= row['y_max']:
            for field in fields:
                row[field].append(flowmap[field][i])

    return None

def find_edges_in_row(row, system):
    """Simple function to find the edges of a row."""

    edge_min = min(row['X']) - system['celldimensions'][0] / 2
    edge_max = max(row['X']) + system['celldimensions'][0] / 2
    row['edges'] = [edge_min, edge_max]

    return None

def keep_droplet_cells_in_row(row, flowmap, system):
    """Goes through all cells in a row and controls if it is well connected 
    to a layer above it. If not it is discarded."""

    fields = {'X', 'U', 'V'}

    row_two = {'num' : row['num'] + 1}
    find_cells_in_row(row_two, flowmap, system)

    keep = {field : [] for field in fields}

    for i, pos_x in enumerate(row['X']):
        if control_cell(pos_x, row_two, system):
            for field in fields:
                keep[field].append(row[field][i])

    for field in fields:
        row[field] = keep[field]

    return None

def control_cell(pos_x, row_two, system):
    """Controls if a cell is well connected to a layer above it, that is
    if the upper layer has at least two filled cells in direct connection 
    to it, or if only one, if that cell is connected to another neighbour."""

    x_min = pos_x - 1.5 * system['celldimensions'][0]
    x_max = pos_x + 1.5 * system['celldimensions'][0]

    count = 0
    for cell_two, pos_x_two in enumerate(row_two['X']):
        if x_min < pos_x_two <= x_max:
            count += 1

    if count > 1:
        success = True
    elif count == 1:
        success = True
    else:
        success = False

    return success

def calc_row_y(row, system):
    """Calculates the minimum, maximum and center position in y for a 
    given cell row."""

    row['y_min'] = system['initdisplacement'][1] + \
            system['celldimensions'][1] * (row['num'] - 0.5)
    row['y_max'] = row['y_min'] + system['celldimensions'][1]
    row['pos_y'] = row['y_min'] + system['celldimensions'][1] / 2

    return None
