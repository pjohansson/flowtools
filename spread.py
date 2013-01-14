"""Module containing tool to plot spreading as a function of time."""

from util import construct_filename, parse_kwargs
from pyplot import plot

def plot_spread_vs_time(system, frames, **kwargs):
    """Finds the spread of the contact line of a droplet and plots it for a 
    list of frame numbers. If system['delta_t'] is specified for time between
    every frame that is used as the x axis.
    
    A specific flow map filename structure can be specified using **kwargs
    as for construct_filename. **kwargs can also be used to specify a row in
    which the spreading is counted as row = 'num."""

    contact_line = {}
    find_contact_line_spread(contact_line, system, frames, **kwargs)
    trim_empty_head(contact_line, frames)

    if 'delta_t' in system.keys():
        for i, value in enumerate(frames):
            frames[i] = i * system['delta_t']

    plot(contact_line['edges'][0], frames, contact_line['edges'][1], frames)

    return None

def find_contact_line_spread(contact_line, system, frames, **kwargs):
    """Finds the spread of a droplet as a function of time by reading flowmaps
    for a list of frame number frames and finding the edges of the droplet in 
    the row directly above the floor, specified in system['floor']. Saves the 
    first frame in which the contact line is found in system['frame_impact'].

    If different options needed for construction of filenames they can be 
    supplied in **kwargs as for construct_filename. A specific row in which
    the floor begins can be specified in **kwargs using row = 'num', otherwise
    it will be calculated using settings for system['initdisplacement'],
    system['celldimensions'] and system['floor']."""

    densmap = {}; flowmap = {};

    opts = {'row' : None}
    parse_kwargs(opts, {'row'})

    if opts['row'] == None:
        row = floor((system['floor'] - system['initdisplacement'][1])
                % system['celldimensions'][1]) - 1
        opts['row'] = row

    row = {'num' : opts['row']}

    for system['frame'] in frames:
        densmap['filename'], flowmap['filename'] = \
                construct_filename(system, **kwargs)
        
        read_flowmap(flowmap)
        find_cells_in_row(row, flowmap, system)
        keep_droplet_cells_in_row(row, flowmap, system)
        find_edges_in_row(row, system)

        contact_line['frame'].append(system['frame'])
        contact_line['edges'].append(row['edges'])

    return None

def trim_empty_head(contact_line, frames):
    """Removes empty entries in contact_line up until the first non-empty
    and trims frames to fit from back. The remainder is a contact_line with
    values starting from first impact and frames counting from that point."""

    while contact_line['edges'][0] == []:
        for field in contact_line.keys():
            del(contact_line[field][0])
        del(frames[-1])

    return None
