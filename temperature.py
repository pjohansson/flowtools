from cut_system import cut_map
from read_data import read_datamap, read_system
from save_data import save_figure
from util import construct_filename, parse_kwargs
import pylab as plt
import numpy as np

def subplot_temperature(system_one, system_two, **kwargs):
    """Draws plots of flow for several systems, starting from impact
    frames and moving on. Systems can be cut using **kwargs as for cut_map.
    Input save_to as a **kwargs to output to .png using that base."""

    datamap_one = {}; datamap_two = {};
    fields = {'X', 'Y', 'T'}

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
            read_system(system_one, from_datamap = datamap_one, print = False)
            read_system(system_two, from_datamap = datamap_two, print = False)

        draw_temperature_sub(datamap_one, datamap_two, system_one, system_two, 
                **kwargs)

        if opts['save_to'] != None:
            print("\rFrame %d of %d ..." % (frame + 1, opts['frames']), 
                end = ' ', flush = True)
            save_figure(opts['save_to'], frame + 1, opts['dpi'])
        elif frame < opts['frames'] - 1:
            plt.figure()

        frame += 1

    return None

def draw_temperature_sub(datamap_one, datamap_two, system_one, system_two, 
        **kwargs):
    """Draws two temperature maps as hist2d plots. Plot options can be supplied 
    using **kwargs."""

    plt.subplot(2,1,1)
    plt.hist2d(datamap_one['X'], datamap_one['Y'], weights = datamap_one['T'], 
            bins = system_one['numcells'], **kwargs)
    plt.axis('scaled')
    plt.title('Temperature on uncharged substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    plt.xlim([117.875, 177.875])
    plt.ylim([2.75, 20])
    plt.subplot(2,1,2)
    plt.hist2d(datamap_two['X'], datamap_two['Y'], weights = datamap_two['T'], 
            bins = system_two['numcells'], **kwargs)
    plt.axis('scaled')
    plt.title('Temperature on charged substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    plt.xlim([114.25, 174.25])
    plt.ylim([0.75, 18])

    plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
    cax = plt.axes([0.85, 0.1, 0.075, 0.8])
    plt.colorbar(cax=cax)

    return None
