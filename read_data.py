"""Tools for reading system from different files."""

from save_data import save_data_to_file
from util import parse_kwargs, reset_fields

def read_system(system, densmap = {}, saveto_filename = '', **kwargs):
    """If a precalculated data file is supplied in the system dictionary as
    system['datafile'], reads and stores total number of cells, as well as 
    for each direction the number of cells, cell dimensions, and system 
    displacement, in the same dictionary.

    The function can also read this data from a density map, given as an
    optional second argument. This data can be further saved by supplying
    a location of a file to store it in as a third argument."""

    opts = {'print' : True}
    parse_kwargs(opts, kwargs)

    if densmap == {}:
        if opts['print']:
            print("Reading data file '%s' ..." % system['datafile'] , end = ' ')
        success = read_data_from_file(system)
        if success and opts['print']:
            print("Done.")
        else:
            print("Could not read file.")

    else:
        success = read_data_from_densmap(system, densmap, opts['print'])
        if success and saveto_filename != '':
            save_data_to_file(system, saveto_filename, opts['print'])

    return None

def read_densmap(densmap_data, **kwargs):
    """Reads a density map and stores values in dictionary."""

    opts = {'print' : True}
    parse_kwargs(opts, kwargs)

    try:
        densmap = open(densmap_data['filename'])
    except IOError:
        print("Could not open density map '%s' for reading." 
                % densmap_data['filename'])
        return None

    fields = ['X', 'Y', 'N', 'T', 'M']
    reset_fields(densmap_data, fields)

    # Assert that first line is good header and read rest of file
    header = densmap.readline().strip().upper().split()

    if header == fields:
        if opts['print']:
            print("Reading density map '%s' ..." 
                    % densmap_data['filename'], end = ' ', flush = True)

        line = densmap.readline().strip()
        while (line != ''):
            values = line.split()

            if len(values) == 5:
                for i, value in enumerate(values):
                    densmap_data[fields[i]].append(float(value))

            line = densmap.readline().strip()

        # Convert values in N to integer
        for i, value in enumerate(densmap_data['N']):
            densmap_data['N'][i] = int(value)

        if opts['print']:
            print("Done.")
        densmap_data['read'] = True

    else:
        print("No good density map: '%s'" % densmap_data['filename'])
        densmap_data['read'] = False
    
    densmap.close()

    return None

def read_flowmap(flowmap_data, **kwargs):
    """Reads a flow map and stores values in dictionary."""

    opts = {'print' : True}
    parse_kwargs(opts, kwargs)

    try:
        flowmap = open(flowmap_data['filename'])
    except IOError:
        print("Could not open flow map '%s' for reading." 
                % flowmap_data['filename'])
        return None

    fields = ['X', 'Y', 'U', 'V']
    reset_fields(flowmap_data, fields)

    # Assert that first line is good header and read rest of file
    header = flowmap.readline().strip().upper().split()

    if header == fields:
        if opts['print']:
            print("Reading flow map '%s' ..." 
                    % flowmap_data['filename'], end = ' ', flush = True)

        line = flowmap.readline().strip()
        while (line != ''):
            values = line.split()

            if len(values) == 4:
                for i, value in enumerate(values):
                    flowmap_data[fields[i]].append(float(value))

            line = flowmap.readline().strip()

        if opts['print']:
            print("Done.")
        flowmap_data['read'] = True


    else:
        print("No good flow map: '%s'" % flowmap_data['filename'])
        flowmap_data['read'] = False
    
    flowmap.close()

    return None

def read_data_from_densmap(system, densmap, print_inp = True):
    """Reads system data into dictionary from density map."""

    if print_inp:
        print("Reading density map data ...", end = ' ', flush = True)
    
    if not ({'X', 'Y'} < densmap.keys()):
        print("Density map is not read yet.")
        return False

    numcells_total = len(densmap['X'])

    X_first = densmap['X'][0]
    for cell, X_value in enumerate(densmap['X']):
        if X_value != X_first:
            break

    numcells_y = cell
    numcells_x = numcells_total // numcells_y

    cell_dimensions_x = densmap['X'][numcells_y] - densmap['X'][0]
    cell_dimensions_y = densmap['Y'][1] - densmap['Y'][0]

    system['numcellstotal'] = numcells_total
    system['numcells'] = [numcells_x, numcells_y]
    system['celldimensions'] = [cell_dimensions_x, cell_dimensions_y]
    system['initdisplacement'] = [densmap['X'][0], densmap['Y'][0]]

    if print_inp:
        print("Done.")

    return True

def read_data_from_file(system):
    """Reads a data file and stores it in system. Returns a success flag."""

    try: 
        datafile = open(system['datafile'], 'r')
    except IOError:
        print("Could not open data file '%s' for reading." 
                % system['datafile'])
        return False

    data_list = {
            'numcellstotal', 'numcells', 'celldimensions', 'initdisplacement'
            }
    opt_list = {'max_mass'}

    line = datafile.readline().strip()
    while (line != ''):
        data, sign, *values = line.split()

        if data in data_list or opt_list:
            system[data] = []
            if len(values) == 1:
                system[data] = float(values[0])
            else:
                for var in values:
                    system[data].append(float(var))

        line = datafile.readline().strip()

    datafile.close()

    # Check if fully read
    if data_list <= system.keys():
        system['numcellstotal'] = int(system['numcellstotal'])
        system['numcells'][0] = int(system['numcells'][0])
        system['numcells'][1] = int(system['numcells'][1])

        success = True
    else:
        # Reset read data
        for data in data_list:
            if data in system.keys():
                del(system[data])

        success = False

    return success
