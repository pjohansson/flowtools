"""Various utilities for density and flow map work."""

from os import path

def advance_frame(system, densmap, flowmap, frame_stride = 1, **kwargs):
    """Advances the frame number by frame_stride (default is one frame)
    and updates filenames to read. Does not read new maps. Does warn if
    no files found for new frame. Returns success flag."""

    current_frame = system['frame']
    system['frame'] += frame_stride
    new_densmap, new_flowmap = construct_filename(system, **kwargs)

    if path.isfile(new_densmap) and path.isfile(new_flowmap):
        densmap['filename'] = new_densmap
        flowmap['filename'] = new_flowmap
        success = True

    else:
        print("Density and / or flow map does not exist for frame %d." 
                % system['frame'])
        system['frame'] = current_frame
        success = False

    return success

def construct_filename(system, **kwargs): 
    """Constructs filenames of density and flow maps from given bases and 
    frame number. In **kwargs a separator can be set using 'sep', extension
    using 'ext' and number of zeros 'numd'."""

    opts = {'ext' : '.dat', 'sep' : '_', 'numd' : 5}
    parse_kwars(opts, kwargs)

    frame_name = ('%0' + ('%d' % opts['numd']) + 'd') % system['frame']
    tail = opts['sep'] + frame_name + opts['ext']

    filename_densmap = system['densbase'] + tail
    filename_flowmap = system['flowbase'] + tail

    return (filename_densmap, filename_flowmap)

def parse_kwars(opts, kwargs):
    """Parses a kwargs array and sets any already in opts to 
    specified values."""

    for arg in kwargs.keys():
        if arg in opts.keys():
            opts[arg] = kwargs[arg]

    return None

def reset_fields(data, fields_reset):
    """Resets specified fields in dictionary data."""
    
    for field in fields_reset:
        data[field] = []

    return None
