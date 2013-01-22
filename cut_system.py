from read_data import read_datamap
from save_data import save_datamap
from util import construct_filename, parse_kwargs, reset_fields
import numpy as np

"""Tool for cutting a system for many frames at once and output the cut data
to a new folder."""

def cut_system_for_frames(system, frames, save_to_folder, **kwargs):
    """Cuts density and flow maps of a system for specified frames and outputs 
    to specified bases. An optional suffix can be supplied in **kwargs as
    suffix = 'suffix'. Cut arguments are given in **kwargs as for cut_map."""

    opts = {'suffix' : ''}
    parse_kwargs(opts, kwargs)

    datamap = {}

    base_strip = system['database'].rsplit('/', maxsplit = 1)[-1]
    save_to_base = save_to_folder + base_strip + opts['suffix']

    print("'%s' -> '%s'" % (system['database'], save_to_base))

    for i, frame in enumerate(frames):
        print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ', flush = True)

        data_filename = construct_filename(system['database'], frame)
        read_datamap(datamap, filename = data_filename, print = False)

        cut_map(datamap, {'X', 'Y', 'N', 'T', 'M', 'U', 'V'}, system, 
                print = False, **kwargs)

        save_to = construct_filename(save_to_base, frame)
        save_datamap(datamap, save_to)

    print("Done.")

    return None

def cut_map(map_to_cut, fields_to_cut, system, **kwargs):
    """Cuts given fields for positions inside, specified by giving arrays
    using keywords 'cutw' and 'cuth' for width and height respectively. 
    Fields are given as a set."""

    opts = {'cutw' : [-np.inf, np.inf], 'cuth' : [-np.inf, np.inf], 'print' : True}
    parse_kwargs(opts, kwargs)

    if opts['print']:
        print("Trying to cut fields ...", end = ' ', flush = True)

    for field in {'X', 'Y'}:
        fields_to_cut.add(field)

    if opts['cutw'][0] > opts['cutw'][1] \
            or opts['cuth'][0] > opts['cuth'][1]:
        print("Cannot cut negative space!")

        return None

    keep = {field : [] for field in fields_to_cut}

    for i, (pos_x, pos_y) in enumerate( zip(map_to_cut['X'], map_to_cut['Y']) ):
        if opts['cutw'][0] < pos_x < opts['cutw'][1] \
                and opts['cuth'][0] < pos_y < opts['cuth'][1]:
            for field in fields_to_cut:
                keep[field].append(map_to_cut[field][i])

    for field in (fields_to_cut):
        map_to_cut[field] = keep[field]

    if opts['print']:
        print("Done.")
    
    return None
