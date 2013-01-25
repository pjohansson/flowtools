from cut_system import cut_map
from read_data import read_datamap, read_system
from save_data import save_figure
from rows import keep_droplet_cells_in_system
from util import construct_filename, parse_kwargs, remove_empty_cells

import numpy as np
import pylab as plt

def plot_flowmaps(frames, **kwargs):
    """Draws quiver plots of flow maps for specified frames. If no system
    supplied as input, or information lacking, asks user for file to 
    read from. By supplying options as for cut_maps in **kwargs the system
    can be cut before outputting. If so a density map has to be supplied for
    reconfiguration to succeed.
    
    To output frame images to .png, enter a base name string for save_to."""

    datamap = {}

    opts = {'cutw' : [-np.inf, np.inf], 'cuth' : [-np.inf, np.inf], 
            'save_to' : None, 'dpi' : 200, 'clear' : True,
            'base' : None, system = {}}
    parse_kwargs(opts, kwargs)

    # Allocate system
    system = opts['system']

    # Find input base filename
    if opts['base'] != None:
        base_filename = opts['base']
    else 'database' in system:
        base_filename = system['database']

    # If no good system information, fill in
    if {'numcells'}.issuperset(system.keys()):
        init_filename = construct_filename(base_filename, frames[0])
        read_system(system, from_datafile = init_filename, print = False)

    # Alert if cutting
    if opts['cutw'] != [-np.inf, np.inf] or \
            opts['cuth'] != [-np.inf, np.inf]:
        to_cut = True
        print("Cutting system outside x = %r and y = %r." 
                % (opts['cutw'], opts['cuth']))
    else:
        to_cut = False

    if opts['clear']:
        plt.clf()

    # For every frame, read data, normalise and draw or save
    for i, frame in enumerate(frames):
        data_filename = construct_filename(base_filename, frame)
        read_datamap(datamap, type = 'flow', filename = data_filename,
                print = False)
        
        # If desired, cut and update system data
        if to_cut:
            cut_map(datamap, {'X', 'Y', 'U', 'V'}, system, **opts)

        # Clean system of bad cells
        remove_empty_cells(datamap, fields = {'X', 'Y', 'U', 'V'})
        keep_droplet_cells_in_system(datamap, system)

        draw_flowmap(datamap, system, **kwargs)

        # Output to file or open new window for next plot
        if opts['save_to'] != None:
            print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ', flush = True)
            save_figure(opts['save_to'], frame, opts['dpi'])
        elif frame < frames[-1]:
            plt.figure()

    if opts['save_to']:
        print("Done.")

    return None

def draw_flowmap(flowmap, system, **kwargs):
    """Draws a flow map as a quiver plot. Plot options can be supplied 
    using **kwargs."""

    plt.quiver(flowmap['X'], flowmap['Y'], flowmap['U'], flowmap['V'], **kwargs)
    plt.axis('scaled')

    return None

def plot_flowmaps_double(system_one, system_two, **kwargs):
    """Draws quiver plots of flow for several systems, starting from impact
    frames and moving on. Systems can be cut using **kwargs as for cut_map.
    Input save_to as a **kwargs to output to .png using that base. Input 
    frames = number of frames to plot."""

    datamap_one = {}; datamap_two = {};
    fields = {'X', 'Y', 'U', 'V', 'M'}

    opts = {'cutw_one' : [-np.inf, np.inf], 'cuth_one' : [-np.inf, np.inf], 
            'cutw_two' : [-np.inf, np.inf], 'cuth_two' : [-np.inf, np.inf], 
            'save_to' : None, 'dpi' : 200, 'clear' : True,
            'base' : None, 'frames' : 0}
    parse_kwargs(opts, kwargs)

    # Alert if cutting
    if opts['cutw_one'] != [-np.inf, np.inf] or \
            opts['cuth_one'] != [-np.inf, np.inf] or \
            opts['cutw_two'] != [-np.inf, np.inf] or \
            opts['cuth_two'] != [-np.inf, np.inf]:
        to_cut = True
    else:
        to_cut = False

    if opts['clear']:
        plt.clf()

    # For all frames, read system, cut, plot
    frame = 0
    while frame < opts['frames']:
        frame_one = system_one['impact_frame'] + frame - 4
        frame_two = system_two['impact_frame'] + frame - 4
        filename_one = construct_filename(system_one['database'], frame_one)
        filename_two = construct_filename(system_two['database'], frame_two)

        read_datamap(datamap_one, fields = fields, filename = filename_one, 
                print = False)
        read_datamap(datamap_two, fields = fields, filename = filename_two, 
                print = False)

        if to_cut:
            cut_map(datamap_one, fields, system_one, print = False,
                    cuth = opts['cuth_one'], cutw = opts['cutw_one'])
            cut_map(datamap_two, fields, system_two, print = False,
                    cuth = opts['cuth_two'], cutw = opts['cutw_two'])
            read_system(datamap_one, from_datamap = datamap_one, print = False)
            read_system(datamap_two, from_datamap = datamap_two, print = False)

        remove_empty_cells(datamap_one, fields = fields)
        remove_empty_cells(datamap_two, fields = fields)
        keep_droplet_cells_in_system(datamap_one, system_one)
        keep_droplet_cells_in_system(datamap_two, system_two)

        draw_flowmap_sub(datamap_one, datamap_two, system_one, system_two, 
                **kwargs)

        if opts['save_to'] != None:
            print("\rFrame %d of %d ..." % (frame + 1, opts['frames']), 
                end = ' ', flush = True)
            save_figure(opts['save_to'], frame + 1, opts['dpi'])
        elif frame < opts['frames'] - 1:
            plt.figure()

        frame += 1

    return None

def draw_flowmap_sub(datamap_one, datamap_two, system_one, system_two, 
        **kwargs):
    """Draws two flow maps as quiver plots. Plot options can be supplied 
    using **kwargs."""

    plt.subplot(2,1,1)
    plt.quiver(datamap_one['X'], datamap_one['Y'], datamap_one['U'], 
            datamap_one['V'], **kwargs)
    plt.axis('scaled')

    plt.title('Flow on uncharged substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    plt.xlim([117.875, 177.875])
    plt.ylim([0, 20])

    plt.subplot(2,1,2)
    plt.quiver(datamap_two['X'], datamap_two['Y'], datamap_two['U'], 
            datamap_two['V'], **kwargs)
    plt.axis('scaled')

    plt.title('Flow on charged substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    plt.xlim([114.25, 174.25])
    plt.ylim([-2, 18])

    return None
