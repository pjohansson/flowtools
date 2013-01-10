"""Contains functions that operate on density and flow field maps."""
from pylab import hist2d

def readDensmap(filename_densmap):
    """Reads a density map from input filename and returns positions X, Y, 
    number of atoms N, temperature T and mass M for individual cells 
    as arrays."""

    densmap = open(filename_densmap)

    X, Y, N, T, M = ([], [], [], [], [])

    # Assert that first line is good header and read rest of file
    line = densmap.readline().strip()

    if line.upper().split() == ['X', 'Y', 'N', 'T', 'M']:
        print("Reading density map '%s' ... " % filename_densmap, end = '')
        line = densmap.readline().strip()

        while (line != ''):
            elements = line.split(' ')

            if len(elements) == 5:
                X.append(float(elements[0]))
                Y.append(float(elements[1]))
                N.append(int(float(elements[2])))
                T.append(float(elements[3]))
                M.append(float(elements[4]))

            line = densmap.readline().strip()

        print("Done.")

    else:
        print("No good density map: '%s'" % filename_densmap)
    
    densmap.close()

    return (X, Y, N, T, M)

def readFlowmap(filename_flowmap):
    """Reads a flow map from input filename and returns positions X, Y, 
    and mass flow velocity U, V for individual cells as arrays."""

    flowmap = open(filename_flowmap)

    X, Y, U, V = ([], [], [], [])

    # Assert that first line is good header and read rest of file
    line = flowmap.readline().strip()

    if line.upper().split() == ['X', 'Y', 'U', 'V']:
        print("Reading flow map '%s' ... " % filename_flowmap, end = '')
        line = flowmap.readline().strip()

        while (line != ''):
            elements = line.split(' ')

            if len(elements) == 4:
                X.append(float(elements[0]))
                Y.append(float(elements[1]))
                U.append(float(elements[2]))
                V.append(float(elements[3]))

            line = flowmap.readline().strip()

        print("Done.")

    else:
        print("No good flow map: '%s'" % filename_flowmap)
    
    flowmap.close()

    return (X, Y, U, V)

def readSystemData(input_filename, output_filename = ''):
    """If a precalculated data file is supplied, reads and returns total 
    number of cells N, as well as number of cells [Nx, Ny], cell dimensions
    [size_x, size_y] and system displacement [disp_x, disp_y] in each 
    direction as a tuple.
    
    The function can also read and save this data to a file by instead 
    supplying a density map as the first argument, and a file to save this 
    data to in the second. The data will still be returned."""

    if output_filename == '':
        print("Reading data file '%s' ... " % input_filename , end = '') 
        data, success = readDatafile(input_filename)
        if success == 1:
            print("Done.")
        else:
            print("Could not read file.")

    else:
        print("NOT IMPLEMENTED YET.")
        data = (0, [], [], [])
        print("Reading density map '%s' for data ... " % input_filename, 
                end = '')
        # data, error = readDataFromDensmap(input_filename)
        print("Done.")
        print("Saving data to file '%s' ... " % output_filename, end = '')
        # error = saveDataFile(data, output_filename)
        print("Done.")

    return data

def readDatafile(data_filename):
    """Reads a data file and returns data and a success flag."""

    datafile = open(data_filename, 'r')

    line = datafile.readline().strip()
    success = 0
    while (line != ''):
        field, sign, *values = line.split()

        if field == 'numcellstotal':
            N_total = int(values[0])
            success += 1

        elif field == 'numcells':
            N_x, N_y = map(int, values)
            success += 1

        elif field == 'celldimensions':
            size_x, size_y = map(float, values)
            success += 1

        elif field == 'initdisplacement':
            disp_x, disp_y = map(float, values)
            success += 1

        line = datafile.readline().strip()
    datafile.close()

    if success == 4:
        flag = 1
    else:
        flag = 0

    return ((N_total, [N_x, N_y], [size_x, size_y], [disp_x, disp_y]), flag)

def drawTemperature(X, Y, T, data, Tmin = 1, Tmax = None):
    """Draws the temperature array T corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum and maximum temperature
    to be shown."""

    hist2d(X, Y, weights = T, bins = data[1], cmin = Tmin, cmax = Tmax)

def drawDensity(X, Y, M, data):
    """Draws the mass density array M corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of binds."""

    hist2d(X, Y, weights = M, bins = data[1])

def cutMap(width_cut, height_cut, X, Y, *fields):
    """Cuts given fields for positions inside specified width and height.
    The input is two vectors with boundaries in height and width respectively.
    If min and max is equal no cut is made."""

    X_keep, Y_keep= ([], []) 
    fields_keep = []
    for i in fields:
        fields_keep.append([])
    
    print("Trying to cut fields ... ", end = '')

    # Check which dimensions to cut
    boolHeight = 0
    if height_cut[0] < height_cut[1]:
        boolHeight = 1
    elif height_cut[0] > height_cut[1]:
        boolHeight = -1

    boolWidth = 0
    if width_cut[0] < width_cut[1]:
        boolWidth = 1
    elif width_cut[0] > width_cut[1]:
        boolWidth = -1

    if boolHeight == -1 or boolWidth == -1:
        print("Cannot cut negative space!")
        return (X_keep, Y_keep, fields_keep)

    for i in range(len(X)):
        # Check if inside height
        if not boolHeight:
            boolKeep = 1
        elif boolHeight and height_cut[0] < Y[i] < height_cut[1]:
            boolKeep = 1
        else:
            boolKeep = 0

        # Check if inside width
        if boolKeep == 1 and not boolWidth:
            boolKeep = 1
        elif boolKeep == 1 and boolWidth and width_cut[0] < X[i] < width_cut[1]:
            boolKeep = 1
        else:
            boolKeep = 0

        # If both good, append to keep
        if boolKeep == 1:
            X_keep.append(X[i])
            Y_keep.append(Y[i])
            for j in range(len(fields)):
                fields_keep[j].append(fields[j][i])

    print("Done.")

    return (X_keep, Y_keep, fields_keep)

def unmodViscFlow(X, Y, U, V, data, filename_viscdata, 
        cut_height = [-1.0, -1.0]):
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

def constructName(filename_densbase, filename_flowbase, frame, 
        extension = '.dat', separator = '_', num_digits = 5):
    """Constructs filenames of density and flow maps from given bases and 
    frame number. Optionally an extension, a separator between base and 
    frame number and a specific number of zeros for the number can 
    be supplied."""

    frame_filename = ('%0' + ('%d' % num_digits) + 'd') % frame
    filename_densmap = '%s%c%s%s' % (
            filename_densbase, separator, frame_filename, extension)
    filename_flowmap = '%s%c%s%s' % (
            filename_flowbase, separator, frame_filename, extension)

    return (filename_densmap, filename_flowmap)

def resetFields(data, fields_reset):
    """Resets specified fields in dictionary data."""
    
    for field, values in data.items():
        if field in fields_reset:
            data[field] = []

def newReadDensmap(densmap_data):
    """Reads a density map and stores values in dictionary."""

    densmap = open(densmap_data['filename'])

    fields = ['X', 'Y', 'N', 'T', 'M']
    resetFields(densmap_data, fields)

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
