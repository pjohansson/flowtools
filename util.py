"""Various utilities for density and flow map work."""

import os
import numpy as np

def advance_frame(system, densmap, flowmap, frame_stride = 1, **kwargs):
    """Advances the frame number by frame_stride (default is one frame)
    and updates filenames to read. Does not read new maps. Does warn if
    no files found for new frame. Returns success flag."""

    current_frame = system['frame']
    system['frame'] += frame_stride
    new_densmap, new_flowmap = construct_filename(system, **kwargs)

    if os.path.isfile(new_densmap) and os.path.isfile(new_flowmap):
        densmap['filename'] = new_densmap
        flowmap['filename'] = new_flowmap
        success = True

    else:
        print("Density and / or flow map does not exist for frame %d." 
                % system['frame'])
        system['frame'] = current_frame
        success = False

    return success

def construct_filename(base, frame, **kwargs): 
    """Constructs filenames of data maps from given base and frame number. 
    In **kwargs a separator can be set using 'sep', extension using 'ext' 
    and number of zeros 'numd'. These default to '_', '.dat' and '5' 
    respectively."""

    opts = {'ext' : '.dat', 'sep' : '_', 'numd' : 5}
    parse_kwargs(opts, kwargs)

    frame_name = ('%0' + ('%d' % opts['numd']) + 'd') % frame
    tail = opts['sep'] + frame_name + opts['ext']

    filename = base + tail

    return filename

def parse_kwargs(opts, kwargs):
    """Parses a kwargs array and sets any already in opts to 
    specified values."""

    for arg in opts.keys():
        if arg in kwargs.keys():
            opts[arg] = kwargs[arg]
            del(kwargs[arg])

    return None

def reset_fields(data, fields_reset):
    """Resets specified fields in dictionary data."""
    
    for field in fields_reset:
        data[field] = []

    return None

def remove_empty_cells(datamap, **kwargs):
    """Removes cells which have no flow from a data map. Specify fields
    to remove as a set in the second argument. A minimum mass can be set
    as Mmin = minimum."""

    opts = {'fields' : set(), 'Mmin' : -np.inf}
    parse_kwargs(opts, kwargs)

    i = 0
    while i < len(datamap['U']):
        if not ((datamap['U'][i] != 0.0 or datamap['V'][i] != 0.0) and \
                datamap['M'][i] >= opts['Mmin']):
            for field in opts['fields']:
                del(datamap[field][i])
        else:
            i += 1

    return None
