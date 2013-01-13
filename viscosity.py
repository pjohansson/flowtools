"""Modules that work with viscosity and flow fields."""

from os import path
from util import reset_fields
from numpy import average

def unmod_visc_flow(system, flowmap):
    """Uses data of viscosity increase close to a substrate to reverse the
    effect of it on a flowmap. Returns a one-dimensional array of the 
    viscosity-reversed flow divided by unmodified in every cell of the
    lowest layer of a spreading droplet.

    An optional vector of cut_height = [cut_min, cut_max] can be supplied
    to control the minimum layers and maximum layers to be included in the 
    calculation. If no maximum is given the function tries to find the 
    thinnest area and cut the calculation at that height. Setting these
    to -1.0 disables them."""

    # Find lowest (well-connected) row of droplet
    # Find how many rows to include in calculation
    # Calculate viscosity modification for every road from data file
    # Apply to every row, add, average
    # Divide by unmodified flow
    # Output

    return None

def calc_viscmod_in_rows(system, viscosity):
    """Reads a file with viscosity modification data and finds which values
    correspond to each row above the substrate for read cell size, storing
    in an array."""

    try:
        viscdata = open(viscosity['filename'])
    except IOError:
        print("Could not open data file '%s' for reading." 
                % viscosity['filename'])
        return None

    # Create array of height values
    reset_fields(viscosity, {'visc', 'error'})

    cell = {
            'num' : 0, 'y_min' : 0, 'y_max' : 0, 
            'viscmod' : [], 'error' : []
            }
    calc_row_y(cell, system)

    line = viscdata.readline().strip()
    while line != '':
            pos_y, viscmod, error = map(float, line.split())

            if pos_y <= cell['y_max']:
                cell['viscmod'].append(float(viscmod))
                cell['error'].append(float(error))
            else:
                finalise_visc_cell(cell, viscosity)
                advance_to_next_cell(cell, system)

            line = viscdata.readline().strip()

    viscdata.close()

    return None

def finalise_visc_cell(cell, viscosity):
    """Calculates the average viscosity modifier of the cell and corresponding 
    error. Appends to array in viscosity dict."""

    viscosity['visc'].append(average(cell['viscmod']))
    # Get two errors for every cell: From distance to mean and read error 
    # collected in array. Combine.
    # Then combine these errors as a Gaussian square.

    return None

def advance_to_next_cell(cell, system):
    """Resets cell data, moves to next in order and calculates information."""

    reset_fields(cell, {'viscmod', 'error'})
    cell['num'] += 1
    calc_row_y(cell, system)

    return None
