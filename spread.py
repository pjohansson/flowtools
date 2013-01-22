"""Module containing tool to plot spreading as a function of time."""

from util import construct_filename, parse_kwargs, reset_fields
from pylab import figure, plot, xlabel, ylabel, title
from read_data import read_flowmap
from rows import find_cells_in_row, keep_droplet_cells_in_row, find_edges_in_row, find_row
import numpy as np

def plot_spread_vs_time(system, frames, **kwargs):
    """Finds the spread of the contact line of a droplet and plots it for a 
    list of frame numbers. If system['delta_t'] is specified for time between
    every frame that is used as the x axis.
    
    A specific flow map filename structure can be specified using **kwargs
    as for construct_filename. **kwargs can also be used to specify a row in
    which the spreading is counted as row = 'num', to cut the flow map at
    a height using cut = 'height' and to save the contact line information
    into an external dictionary as line = contact_line.
    
    By default the time is measured after the first spreading is observed.
    To draw the diagram for all input frames, input relative = False in
    **kwargs array."""

    opts = {'line' : {}, 'relative' : True, 'delta_t' : 0}
    if 'delta_t' in system.keys():
        opts['delta_t'] = system['delta_t']
    parse_kwargs(opts, kwargs)

    contact_line = opts['line']

    find_contact_line_spread(contact_line, system, frames, **kwargs)

    if opts['relative']:
        trim_empty_head(contact_line, frames)

    if opts['delta_t'] > 0.0:
        draw_spread_time(contact_line, opts['delta_t'])
    else:
        draw_spread_frames(contact_line)

    return None

def draw_spread_time(contact_line, delta_t, **kwargs):
    """Draws a plot of a spreading droplet on a surface as a function of
    time. Plotting commands can be set using **kwargs."""

    opts = {'legend' : False, 'hold' : None}
    parse_kwargs(opts, kwargs)

    contact_line['times'] = []
    frame_null = contact_line['frames'][0]
    for i, frame in enumerate(contact_line['frames']):
        contact_line['times'].append((frame - frame_null) * delta_t)

    plot(contact_line['times'], contact_line['spread'], **kwargs)
    xlabel('Time (ps)'); ylabel('Spread of contact line (nm)');
    title('Spread of contact line of droplet on a surface.')
    
    if opts['legend']:
        legend()
    if opts['hold'] == True:
        hold(True)
    elif opts['hold'] == False:
        hold(False)

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
    parse_kwargs(opts, kwargs)

    if opts['row'] == None:
        opts['row'] = find_row(system['floor'], system)
        print(opts['row'])

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
        contact_line['spread'].append(row['edges'])

    return None

def find_impact_position(contact_line, frames):
    """Finds the middle position of the first impact given a fully read 
    contact line array."""

    for edges, frame in zip(contact_line['spread'], frames):
        if spread != []:
            contact_line['impact_frame'] = frame
            contact_line['impact_pos'] = np.mean(edges)
            break

    return None

def trim_empty_head(contact_line, frames):
    """Removes empty entries in contact_line up until the first non-empty
    and trims frames to fit from back. The remainder is a contact_line with
    values starting from first impact and frames counting from that point."""

    while contact_line['spread'] != [] and contact_line['spread'][0] == 0:
        del(contact_line['spread'][0])
        del(contact_line['frames'][-1])

    return None
