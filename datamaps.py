"""Contains functions that operate on density and flow field maps."""

from numpy import inf
from draw import *
from util import *
from viscosity import *

BOLTZ = 8.6173E-5 # eV / K 

def read_system(system, densmap = {}, saveto_filename = ''):
    """If a precalculated data file is supplied in the system dictionary as
    system['datafile'], reads and stores total number of cells, as well as 
    for each direction the number of cells, cell dimensions, and system 
    displacement, in the same dictionary.

    The function can also read this data from a density map, given as an
    optional second argument. This data can be further saved by supplying
    a location of a file to store it in as a third argument."""

    if densmap == {}:
        print("Reading data file '%s' ..." % system['datafile'] , end = ' ') 
        success = read_data_from_file(system)
        if success:
            print("Done.")
        else:
            print("Could not read file.")

    else:
        success = read_data_from_densmap(system, densmap)
        if success and saveto_filename != '':
            save_data_to_file(system, saveto_filename)

    return None

def read_densmap(densmap_data):
    """Reads a density map and stores values in dictionary."""

    densmap = open(densmap_data['filename'])

    fields = ['X', 'Y', 'N', 'T', 'M']
    reset_fields(densmap_data, fields)

    # Assert that first line is good header and read rest of file
    header = densmap.readline().strip().upper().split()

    if header == fields:
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

        print("Done.")
        densmap_data['read'] = 1

    else:
        print("No good density map: '%s'" % densmap_data['filename'])
        densmap_data['read'] = 0
    
    densmap.close()

    return None

def read_flowmap(flowmap_data):
    """Reads a flow map and stores values in dictionary."""

    flowmap = open(flowmap_data['filename'])

    fields = ['X', 'Y', 'U', 'V']
    reset_fields(flowmap_data, fields)

    # Assert that first line is good header and read rest of file
    header = flowmap.readline().strip().upper().split()

    if header == fields:
        print("Reading flow map '%s' ..." 
                % flowmap_data['filename'], end = ' ', flush = True)

        line = flowmap.readline().strip()
        while (line != ''):
            values = line.split()

            if len(values) == 4:
                for i, value in enumerate(values):
                    flowmap_data[fields[i]].append(float(value))

            line = flowmap.readline().strip()

        print("Done.")
        flowmap_data['read'] = 1

    else:
        print("No good flow map: '%s'" % flowmap_data['filename'])
        flowmap_data['read'] = 0
    
    flowmap.close()

    return None

def read_data_from_densmap(system, densmap):
    """Reads system data into dictionary from density map."""

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

    print("Done.")

    return True

def read_data_from_file(system):
    """Reads a data file and stores it in system. Returns a success flag."""

    datafile = open(system['datafile'], 'r')

    data_list = {
            'numcellstotal', 'numcells', 'celldimensions', 'initdisplacement'
            }

    line = datafile.readline().strip()
    while (line != ''):
        data, sign, *values = line.split()

        if data in data_list:
            system[data] = []
            for var in values:
                system[data].append(float(var))

        line = datafile.readline().strip()

    datafile.close()

    # Check if fully read
    if data_list <= system.keys():
        system['numcellstotal'][0] = int(system['numcellstotal'][0])
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

def save_data_to_file(system, saveto_filename):
    """Prints system data information to a text file."""

    saveto = open(saveto_filename, 'w')
    fields = {
            'numcellstotal', 'numcells', 'celldimensions', 'initdisplacement'
            }

    for field in fields:
        line = field + ' ='

        if type(system[field]) == list:
            for value in system[field]:
                line += ' %s' % value
        else:
            line += ' %s' % system[field]

        line.strip()
        line += '\n'

        saveto.write(line)
    saveto.close()

    return None

def cut_map(map_to_cut, fields_to_cut, system, **kwargs):
    """Cuts given fields for positions inside, specified by giving arrays
    using keywords 'cutw' and 'cuth' for width and height respectively. 
    Fields are given as a set."""

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf]}

    print("Trying to cut fields ...", end = ' ', flush = True)

    parse_kwars(opts, kwargs)

    # Assert that cut area is positive
    if opts['cutw'][0] > opts['cutw'][1] or opts['cuth'][0] > opts['cuth'][1]:
        print("Cannot cut negative space!")
        return 

    # 'X' and 'Y' implicit to cut
    for field in ('X', 'Y'):
        fields_to_cut.add(field)

    # Create new fields to keep
    keep = {field : [] for field in fields_to_cut}

    for i in range(len(map_to_cut['X'])):
        # Check if inside
        if opts['cutw'][0] < map_to_cut['X'][i] < opts['cutw'][1] \
                and opts['cuth'][0] < map_to_cut['Y'][i] < opts['cuth'][1]:
            for field in fields_to_cut:
                keep[field].append(map_to_cut[field][i])

    for field in (fields_to_cut):
        map_to_cut[field] = keep[field]

    print("Done.")

    read_system(system, map_to_cut)
    print("System cell data updated.")

    return None

def construct_filename(system, frame, **kwargs): 
    """Constructs filenames of density and flow maps from given bases and 
    frame number. In **kwargs a separator can be set using 'sep', extension
    using 'ext' and number of zeros 'numd'."""

    opts = {'ext' : '.dat', 'sep' : '_', 'numd' : 5}

    parse_kwars(opts, kwargs)

    frame_filename = ('%0' + ('%d' % opts['numd']) + 'd') % frame
    filename_densmap = '%s%s%s%s' % (
            system['densbase'], opts['sep'], frame_filename, opts['ext'])
    filename_flowmap = '%s%s%s%s' % (
            system['flowbase'], opts['sep'], frame_filename, opts['ext'])

    return (filename_densmap, filename_flowmap)

def calc_energy(densmap):
    """Calculates the kinetic energy in cells from the temperature, stores
    in dict with keyword 'E'."""

    reset_fields(densmap, {'E'})

    for temp, numatoms in zip(densmap['T'], densmap['N']):
        energy = 2 * BOLTZ * numatoms * temp
        densmap['E'].append(energy)
