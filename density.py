from cut_system import cut_map
from read_data import read_datamap, read_system
from save_data import save_figure
from util import construct_filename, parse_kwargs, reset_fields
import numpy as np
import pylab as plt

def plot_density(system, frames, **kwargs):
    """Calls relevant functions to draw energy maps of supplied density maps.
    Options for cut_map and draw_density can be supplied as usual through 
    **kwargs. A base name different from that in system through base.

    To output frame images to .png, **kwargs can be used to enter a base name 
    with save_to and dpi setting with dpi. To avoid clearing active figure
    at start, supply clear = False."""

    datamap = {}

    opts = {'cutw' : [-np.inf, np.inf], 'cuth' : [-np.inf, np.inf], 
            'save_to' : None, 'dpi' : 200, 'clear' : True,
            'base' : None}
    parse_kwargs(opts, kwargs)

    # Find input base filename
    if opts['base'] != None:
        base_filename = opts['base']
    elif 'database' in system:
        base_filename = system['database']
    else:
        base_filename = system['densbase']

    # Alert if cutting
    if opts['cutw'] != [-np.inf, np.inf] or \
            opts['cuth'] != [-np.inf, np.inf]:
        to_cut = True
        print("Cutting system outside x = %r and y = %r." 
                % (opts['cutw'], opts['cuth']))
    else:
        to_cut = False

    find_normalising_factor(system, base_filename, frames)

    if opts['clear']:
        plt.clf()

    # For every frame, read data, normalise and draw or save
    for frame in frames:
        data_filename = construct_filename(base_filename, frame)
        read_datamap(datamap, filename = data_filename, 
                fields = {'X', 'Y', 'M'}, print = False)

        # If desired, cut and update system data
        if to_cut:
            cut_map(datamap, {'X', 'Y', 'M'}, system, print = False, **opts)
            read_system(system, from_datamap = datamap, print = False)

        normalise_density(datamap, system)
        draw_density(datamap, system, **kwargs)

        if opts['save_to'] != None:
            print("\rFrame %d (%d of %d) ..." % (frame, i + 1, len(frames)), 
                end = ' ')
            save_figure(opts['save_to'], frame, opts['dpi'])
        elif frame < frames[-1]:
            plt.figure()

    print("Done.")

    return None

def find_normalising_factor(system, base_filename, frames):
    """Find the maximum mass in a cell in all frames of the system,
    use this to later normalise the system. Saves to system['max_mass'].
    If value already present, ignore."""

    datamap = {}

    if 'max_mass' in system.keys() and system['max_mass'] > 0.0:
        return None

    print("Finding normalising factor.")

    system['max_mass'] = 0.0

    for frame in frames:
        data_filename = construct_filename(base_filename, frame)
        read_datamap(datamap, filename = data_filename, fields = {'M'}, 
                print = False)
        system['max_mass'] = max(system['max_mass'], max(datamap['M']))

    return None

def normalise_density(datamap, system):
    """Uses system['max_mass'] to normalise masses in cells, saving normalised
    mass values to datamap['dens_norm']."""
    
    reset_fields(datamap, {'dens_norm'})
    for mass in datamap['M']:
        datamap['dens_norm'].append(mass / system['max_mass'])

    return None

def draw_density(datamap, system, **kwargs):
    """Draws the energy array E corresponding to cell positions X and Y in 
    a figure using a weighted 2d histogram and data for number of bins. 
    Normally caps colormap for normalised density values between 0 and 1, this 
    can be modified by supplying different vmin and vmax as kwargs, disabling
    by using None. 
    
    Supplying minimum and maximum masses to show can be done similarly as 
    mmin and mmax, these are normalised by system['max_mass']. Other **kwargs
    as for hist2d."""

    opts = {'colormap' : True, 'mmin' : -np.inf, 'mmax' : np.inf, 
            'vmin' : 0.0, 'vmax' : 1.0}
    parse_kwargs(opts, kwargs)

    opts['mmin'] /= system['max_mass']
    opts['mmax'] /= system['max_mass']

    plt.hist2d(datamap['X'], datamap['Y'], weights = datamap['dens_norm'], 
            bins = system['numcells'], vmin = opts['vmin'], vmax = opts['vmax'],
            cmin = opts['mmin'], cmax = opts['mmax'], **kwargs)
    plt.axis('scaled');

    plt.title('Density of droplet on substrate.')
    plt.xlabel('Position (nm)')
    plt.ylabel('Height (nm)')
    
    if opts['colormap']:
        plt.colorbar()

    return None
