from cut_system import cut_map
from numpy import inf
from read_data import read_densmap, read_system
from save_data import save_figure
from util import construct_filename, parse_kwargs, reset_fields
import pylab as plt

def plot_temperature(system, frames, **kwargs):
    """Calls relevant functions to draw the temperature of supplied density 
    maps. Options for cut_map and draw_density can be supplied as usual through 
    **kwargs.

    To output frame images to .png, **kwargs can be used to enter a base name 
    with save_to and dpi setting with dpi. To avoid clearing active figure
    at start, supply clear = False."""

    densmap = {}

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf], 
            'save_to' : None, 'dpi' : 200, 'clear' : True}
    parse_kwargs(opts, kwargs)

    if opts['cutw'] != [-inf, inf] or opts['cuth'] != [-inf, inf]:
        print("Cutting system outside x = %r and y = %r." 
                % (opts['cutw'], opts['cuth']))

    if opts['clear']:
        plt.clf()

    for i, frame in enumerate(frames):
        densmap['filename'] = construct_filename(system['densbase'], frame)
        read_densmap(densmap, print = False)

        if opts['cutw'] != [-inf, inf] or opts['cuth'] != [-inf, inf]:
            cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, 
                    print = False, **opts)
            read_system(system, densmap, print = False)

        draw_temperature(densmap, system, **kwargs)

        if opts['save_to'] != None:
            print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ')
            save_figure(opts['save_to'], frame, opts['dpi'])
        elif frame < frames[-1]:
            plt.figure()

    print("Done.")

    return None

def draw_temperature(densmap, system, **kwargs):
    """Draws the energy array E corresponding to cell positions X and Y in 
    a figure using a weighted 2d histogram and data for number of bins. 
    Supplying minimum and maximum temperatures to show can be done as **kwargs
    tmin and tmax. Other **kwargs as for hist2d."""

    opts = {'colormap' : True, 'tmin' : -inf, 'tmax' : inf}
    parse_kwargs(opts, kwargs)

    plt.hist2d(densmap['X'], densmap['Y'], weights = densmap['T'], 
            bins = system['numcells'], 
            cmin = opts['tmin'], cmax = opts['tmax'], **kwargs)
    plt.axis('scaled');

    plt.title('Temperature of droplet on substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    
    if opts['colormap']:
        plt.colorbar()

    return None
