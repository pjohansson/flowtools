"""Tools for saving data and maps."""

from modify_maps import cut_map
from util import construct_filename
from read_data import read_densmap, read_flowmap

def save_data_to_file(system, saveto_filename):
    """Prints system data information to a text file."""

    try:
        saveto = open(saveto_filename, 'w')
    except IOError:
        print("Could not open '%s' for writing data to." % saveto_filename)
        return None

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

def save_densmap(densmap, save_to_filename):
    """Saves a density map to a file."""

    fields = ['X', 'Y', 'N', 'T', 'M']
    save_map_to_file(densmap, fields, save_to_filename)

    return None

def save_flowmap(flowmap, save_to_filename):
    """Saves a flow map to a file."""

    fields = ['X', 'Y', 'U', 'V']
    save_map_to_file(flowmap, fields, save_to_filename)

    return None

def save_map_to_file(data_map, fields, save_to_filename):
    """Saves chosen fields from a map to a file."""

    try:
        save_to = open(save_to_filename, 'w')
    except IOError:
        print("Could not open '%s' for writing data to." % save_to_filename)
        return None

    header = create_header(fields)
    save_to.write(header)

    for i in range(len(data_map[fields[0]])):
        line = create_line(i, data_map, fields)
        save_to.write(line)

    save_to.close()

    return None

def create_line(i, data_map, fields):
    """Returns a line created in order from fields."""

    line = ''

    for field in fields:
        if i < len(data_map[field]):
            line += '%f' % data_map[field][i]
        else:
            line += '%f' % 0.0

        if field != fields[-1]:
            line += ' '

    line += '\n'

    return line

def create_header(fields):
    """Returns a header created in order from fields."""

    header = ''

    for field in fields:
        header += field

        if field != fields[-1]:
            header += ' '

    header += '\n'

    return header

def cut_system_for_frames(system, frames, save_to_densbase, save_to_flowbase, 
        **kwargs):
    """Cuts density and flow maps of a system for specified frames and outputs 
    to specified bases. Cut arguments are given in **kwargs as for cut_map."""

    densmap = {}; flowmap = {};

    for frame in frames:
        densmap['filename'] = construct_filename(system['densbase'], frame)
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_densmap(densmap)
        read_flowmap(flowmap)

        cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, **kwargs)
        cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, **kwargs)

        save_to_dens = construct_filename(save_to_densbase, frame)
        save_to_flow = construct_filename(save_to_flowbase, frame)
        save_densmap(densmap, save_to_dens)
        save_flowmap(flowmap, save_to_flow)
