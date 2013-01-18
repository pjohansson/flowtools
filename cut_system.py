from numpy import inf
from read_data import read_densmap, read_flowmap
from save_data import save_densmap, save_flowmap
from util import construct_filename, parse_kwargs, reset_fields

"""Tool for cutting a system for many frames at once and output the cut data
to a new folder."""

def cut_system_for_frames(system, frames, save_to_folder, **kwargs):
    """Cuts density and flow maps of a system for specified frames and outputs 
    to specified bases. An optional suffix can be supplied in **kwargs as
    suffix = 'suffix'. Cut arguments are given in **kwargs as for cut_map."""

    opts = {'suffix' : ''}
    parse_kwargs(opts, kwargs)

    densmap = {}; flowmap = {};

    densbase_strip = system['densbase'].rsplit('/', maxsplit = 1)[-1]
    flowbase_strip = system['flowbase'].rsplit('/', maxsplit = 1)[-1]
    save_to_densbase = save_to_folder + densbase_strip + opts['suffix']
    save_to_flowbase = save_to_folder + flowbase_strip + opts['suffix']

    print("Cutting system outside x = %r and y = %r." 
            % (opts['cutw'], opts['cuth']))
    print("%s -> %s", (system['densbase'], save_to_densbase))
    print("%s -> %s", (system['flowbase'], save_to_flowbase))

    for frame in frames:
        print("\rFrame %d of %d ..." % (frame, frames[-1]), end = ' ')
        densmap['filename'] = construct_filename(system['densbase'], frame)
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_densmap(densmap, print = False)
        read_flowmap(flowmap, print = False)

        cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, 
                print = False, **kwargs)
        cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, 
                print = False, **kwargs)

        save_to_dens = construct_filename(save_to_densbase, frame)
        save_to_flow = construct_filename(save_to_flowbase, frame)
        save_densmap(densmap, save_to_dens)
        save_flowmap(flowmap, save_to_flow)

    return None

def cut_map(map_to_cut, fields_to_cut, system, **kwargs):
    """Cuts given fields for positions inside, specified by giving arrays
    using keywords 'cutw' and 'cuth' for width and height respectively. 
    Fields are given as a set."""

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf], 'print' : True}
    parse_kwargs(opts, kwargs)

    if opts['print']:
        print("Trying to cut fields ...", 
                end = ' ', flush = True)

    for field in {'X', 'Y'}:
        fields_to_cut.add(field)

    if opts['cutw'][0] > opts['cutw'][1] \
            or opts['cuth'][0] > opts['cuth'][1]:
        if opts['print']:
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
