"""Contains tools for main tasks on flow maps."""

from util import construct_filename, parse_kwargs
from modify_maps import cut_map
from read_data import read_flowmap
from draw import draw_flowmap
from pylab import figure, hold, savefig, clf
from rows import keep_droplet_cells_in_system

def plot_flowmaps(system, frames, save_to = None, **kwargs):
    """Draws quiver plots of flow maps for specified frames. If no system
    supplied as input, or information lacking, asks user for file to 
    read from. By supplying options as for cut_maps in **kwargs the system
    can be cut before outputting. If so a density map has to be supplied for
    reconfiguration to succeed.
    
    To output frame images to .png, enter a base name string for save_to."""

    flowmap = {}

    opts = {'cutw' : None, 'cuth' : None}
    parse_kwargs(opts, kwargs)

    for frame in frames:
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_flowmap(flowmap)
        
        if (opts['cutw'] or opts['cuth']) != None:
            cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, **kwargs)

        keep_droplet_cells_in_system(flowmap, system)

        if save_to == None:
            figure()
        else:
            hold(False)
            save_to_frame = construct_filename(save_to, frame, ext = '.png')
            clf()

        draw_flowmap(flowmap, system, **kwargs)

        if save_to != None:
            savefig(save_to_frame)

    return None

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

    opts = {'line' : {}, 'relative' : True}
    parse_kwargs(opts, kwargs)

    contact_line = opts['line']

    find_contact_line_spread(contact_line, system, frames, **kwargs)

    if opts['relative']:
        trim_empty_head(contact_line, frames)

    if 'delta_t' in system.keys():
        draw_spread_time(contact_line, system)

    return None
