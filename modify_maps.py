"""Tools for modifying data and flow maps."""

from util import parse_kwargs
from read_data import read_system

BOLTZ = 8.6173E-5 # eV / K 

def cut_map(map_to_cut, fields_to_cut, system, **kwargs):
    """Cuts given fields for positions inside, specified by giving arrays
    using keywords 'cutw' and 'cuth' for width and height respectively. 
    Fields are given as a set."""

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf], 'print' = True}
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

def calc_energy(densmap):
    """Calculates the kinetic energy in cells from the temperature, stores
    in dict with keyword 'E'."""

    for temp, numatoms in zip(densmap['T'], densmap['N']):
        energy = 2 * BOLTZ * numatoms * temp
        densmap['E'].append(energy)

    return None
