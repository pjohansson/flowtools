"""Tools for reading system from different files."""

from util import parse_kwargs, reset_fields

def read_system(system, **kwargs):
    """If a precalculated data file is supplied in the system dictionary as
    system['datafile'], reads and stores total number of cells, as well as 
    for each direction the number of cells, cell dimensions, and system 
    displacement, in the same dictionary.

    By giving a datamap using from_datamap as a **kwargs the system reads 
    from the map instead of from a aggregated file. Additionally the **kwargs 
    from_datafile can be filled with a which to calculate the data from, 
    by way of an ordinary data map reading."""

    opts = {'print' : True, 'from_datamap' : None, 'from_datafile' : None}
    parse_kwargs(opts, kwargs)

    if opts['from_datamap'] != None:
        read_data_from_datamap(system, opts['from_datamap'], opts['print'])

    elif opts['from_datafile'] != None:
        datamap = {}
        read_datamap(datamap, filename = opts['from_datafile'], 
            fields = {'X', 'Y'}, print = opts['print'])
        read_data_from_datamap(system, datamap, opts['print'])

    else:
        read_data_from_file(system)

    return None

def read_datamap(datamap, **kwargs):
    """Reads a data map datamap['filename'] and stores values in dictionary. 
    By default reads a full data map, ordinary density or flow maps can be 
    read by inputting type = 'density' or 'flow' as a **kwargs. If full control 
    over read fields is wanted, a set can be input using fields = set() in the 
    same way. This always takes precedense. A different filename can be 
    similarly specified using filename as a **kwargs."""

    opts = {'print' : True, 'type' : 'full', 'fields' : None, 'filename' : None}
    parse_kwargs(opts, kwargs)

    fields = set()
    if opts['fields'] != None:
        for field in opts['fields']:
            fields.add(field)
    elif opts['type'].lower() == 'full':
        fields = {'X', 'Y', 'N', 'T', 'M', 'U', 'V'}
    elif opts['type'].lower() == 'density':
        fields = {'X', 'Y', 'N', 'T', 'M'}
    elif opts['type'].lower() == 'flow':
        fields = {'X', 'Y', 'U', 'V'}

    if opts['filename'] == None:
        filename = datamap['filename']
    else:
        filename = opts['filename']

    try:
        datamap_file = open(filename)
    except IOError:
        print("Could not open data map '%s' for reading." % filename)
        return None

    reset_fields(datamap, fields)

    # Assert that header contains all desired fields
    header = datamap_file.readline().strip().upper().split()
    if not fields.issubset(header):
        print("No good data map: '%s'" % filename)

        datamap['read'] = False
        datamap_file.close()

        return None

    if opts['print']:
        print("Reading data map '%s' ..." % filename, end = ' ', flush = True)

    # Until end of file, read and split lines, append to corresponding
    # fields in datamap dictionary
    line = datamap_file.readline().strip()
    while (line != ''):
        all_values = line.split()

        if len(all_values) == len(header):
            for i, read_value in enumerate(all_values):
                if header[i] in fields:
                    datamap[header[i]].append(float(read_value))

        line = datamap_file.readline().strip()
    datamap_file.close()

    # Convert values in N to integer
    if 'N' in fields:
        for i, value in enumerate(datamap['N']):
            datamap['N'][i] = int(round(value))
    datamap['read'] = True

    if opts['print']:
        print("Done.")

    return None

def read_densmap(densmap, **kwargs):
    """Reads a density map and stores values in dictionary."""

    read_datamap(densmap, type = 'density', **kwargs)

    return None

def read_flowmap(flowmap, **kwargs):
    """Reads a flow map and stores values in dictionary."""

    read_datamap(flowmap, type = 'flow', **kwargs)

    return None

def read_data_from_datamap(system, datamap, print_inp = True):
    """Reads system data into dictionary from datamap."""

    if print_inp:
        print("Reading data map data ...", end = ' ', flush = True)
    
    if not {'X', 'Y'}.issubset(datamap.keys()):
        print("Density map is not read yet.")

        return False

    numcells_total = len(datamap['X'])

    X_first = datamap['X'][0]
    for cell, X_value in enumerate(datamap['X']):
        if X_value != X_first:
            break

    numcells_y = cell
    numcells_x = numcells_total // numcells_y

    cell_dimensions_x = datamap['X'][numcells_y] - datamap['X'][0]
    cell_dimensions_y = datamap['Y'][1] - datamap['Y'][0]

    system['numcellstotal'] = numcells_total
    system['numcells'] = [numcells_x, numcells_y]
    system['celldimensions'] = [cell_dimensions_x, cell_dimensions_y]
    system['initdisplacement'] = [datamap['X'][0], datamap['Y'][0]]

    if print_inp:
        print("Done.")

    return True

def read_data_from_file(system):
    """Reads a data file system['datafile'] for information. Returns a 
    success flag."""

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
            if len(values) == 1:
                system[data] = float(values[0])
            else:
                system[data] = []
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
