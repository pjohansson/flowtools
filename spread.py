"""Module containing tool to plot spreading as a function of time."""

from util import construct_filename, parse_kwargs, reset_fields, remove_empty_cells
from pylab import figure, plot, xlabel, ylabel, title, hold
from read_data import read_flowmap, read_datamap
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

    opts = {'line' : {}, 'relative' : True, 'delta_t' : 0,
            'Mmin' : -np.inf}
    if 'delta_t' in system.keys():
        opts['delta_t'] = system['delta_t']
    parse_kwargs(opts, kwargs)

    find_contact_line_spread(system, frames, contact_line = opts['line'],
            Mmin = opts['Mmin'], **kwargs)

    if opts['relative']:
        trim_empty_head(opts['line'])

    if opts['delta_t'] > 0.0:
        draw_spread_time(opts['line'], opts['delta_t'], **kwargs)
    else:
        pass
        #draw_spread_frames(opts['line'])

    return None

def draw_spread_time(contact_line, delta_t, **kwargs):
    """Draws a plot of a spreading droplet on a surface as a function of
    time. Plotting commands can be set using **kwargs."""

    opts = {'label' : '_nolegend_', 'legend' : False, 'hold' : None,
            'color' : 'blue'}
    parse_kwargs(opts, kwargs)

    contact_line['times'] = []
    frame_null = contact_line['frames'][0]
    for i, frame in enumerate(contact_line['frames']):
        contact_line['times'].append((frame - frame_null) * delta_t)

    hold(True)
    plot(contact_line['times'], contact_line['spread']['left'], opts['color'],
            label=opts['label'], **kwargs)
    plot(contact_line['times'], contact_line['spread']['right'], opts['color'],
            label='_nolegend_', **kwargs)
    xlabel('Time (ps)'); ylabel('Spread of contact line (nm)');
    title('Spread of contact line of droplet on a surface.')

    return None

def find_contact_line_spread(system, frames, **kwargs):
    """Finds the spread of a droplet as a function of time by reading flowmaps
    for a list of frame number frames and finding the edges of the droplet in
    the row directly above the floor, specified in system['floor']. Saves the
    first frame in which the contact line is found in system['frame_impact'].

    If different options needed for construction of filenames they can be
    supplied in **kwargs as for construct_filename. A specific row in which
    the floor begins can be specified in **kwargs using row = 'num', otherwise
    it will be calculated using settings for system['initdisplacement'],
    system['celldimensions'] and system['floor'].

    The finished contact line can be input and thus save by using the **kwargs
    contact_line."""

    datamap = {}
    fields_flow = {'X', 'Y', 'U', 'V', 'M'}

    opts = {'row' : None, 'contact_line' : {}, 'base' : None,
            'Mmin' : -np.inf, 'impact_frame' : 0}
    parse_kwargs(opts, kwargs)

    if opts['row'] == None:
        opts['row'] = find_row(system['floor'], system)

    row = {'num' : opts['row']}
    impact_frame = False

    reset_fields(opts['contact_line'], {'frames'})
    opts['contact_line']['spread'] = {'left' : [], 'right' : []}

    for i, frame in enumerate(frames):
        print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)),
            end = ' ', flush = True)

        # Construct filename for frame and read data map
        data_filename = construct_filename(system['database'], frame, **kwargs)
        read_datamap(datamap, fields = fields_flow,
                filename = data_filename, print = False)

        # Clean map of non-good cells and extract cells in row
        remove_empty_cells(datamap, fields = fields_flow, Mmin = opts['Mmin'])
        find_cells_in_row(row, datamap, system)

        # Remove cells in row of the precursor film and then find the edges
        keep_droplet_cells_in_row(row, datamap, system)
        find_edges_in_row(row, system)


        # Check if impact or not, ie. if edges are found
        if row['edges'] == [] or frame < opts['impact_frame']:
            opts['contact_line']['spread']['left'].append(0.)
            opts['contact_line']['spread']['right'].append(0.)
        else:
            # Save impact information
            if not impact_frame:
                impact_frame = True
                opts['contact_line']['impact_frame'] = frame
                opts['contact_line']['impact_pos'] = np.mean(row['edges'])

            # Append spread
            opts['contact_line']['spread']['left'].append(
                    row['edges'][0] - opts['contact_line']['impact_pos'])
            opts['contact_line']['spread']['right'].append(
                    row['edges'][1] - opts['contact_line']['impact_pos'])

        # Append frame number to list
        opts['contact_line']['frames'].append(frame)

    return None

def trim_empty_head(contact_line):
    """Removes empty entries in contact_line up until the first non-empty
    and trims frames to fit from back. The remainder is a contact_line with
    values starting from first impact and frames counting from that point."""

    frame = contact_line['frames'][0]
    while frame < contact_line['impact_frame']:
        del(contact_line['spread']['left'][0])
        del(contact_line['spread']['right'][0])
        del(contact_line['frames'][-1])
        frame += 1

    return None
