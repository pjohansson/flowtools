"""Module containing tool to plot spreading as a function of time."""

from util import construct_filename, parse_kwargs, reset_fields
from numpy import floor
from pylab import plot, xlabel, ylabel, title
from read_data import read_flowmap
from rows import find_cells_in_row, keep_droplet_cells_in_row, find_edges_in_row

def draw_spread_time(contact_line, system, **kwargs):
    """Draws a plot of a spreading droplet on a surface as a function of
    time. Plotting commands can be set using **kwargs."""

    contact_line['times'] = []
    frame_null = contact_line['frames'][0]
    for i, frame in enumerate(contact_line['frames']):
        contact_line['times'].append((frame - frame_null) * system['delta_t'])

    plot(contact_line['times'], contact_line['spread'])
    xlabel('Time (ps)'); ylabel('Spread of contact line (nm)');
    title('Spread of contact line of droplet on a quadrupole surface.')

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
    parse_kwargs(opts, kwargs)

    if opts['row'] == None:
        row = int(floor((system['floor'] - system['initdisplacement'][1])
                / system['celldimensions'][1]))
        opts['row'] = row

    row = {'num' : opts['row']}

    reset_fields(contact_line, {'spread', 'frames'})

    for frame in frames:
        flowmap['filename'] = construct_filename(system['flowbase'], 
                frame, **kwargs)
        
        read_flowmap(flowmap)
        find_cells_in_row(row, flowmap, system)
        keep_droplet_cells_in_row(row, flowmap, system)
        find_edges_in_row(row, system)

        contact_line['frames'].append(frame)
        if row['edges'] != []:
            contact_line['spread'].append(row['edges'][1] - row['edges'][0])
        else:
            contact_line['spread'].append(0)

    return None

def trim_empty_head(contact_line, frames):
    """Removes empty entries in contact_line up until the first non-empty
    and trims frames to fit from back. The remainder is a contact_line with
    values starting from first impact and frames counting from that point."""

    while contact_line['spread'] != [] and contact_line['spread'][0] == 0:
        del(contact_line['spread'][0])
        del(contact_line['frames'][-1])

    return None
