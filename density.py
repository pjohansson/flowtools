from cut_system import cut_map
from numpy import inf
from pylab import axis, clf, colorbar, figure, hist2d, title, xlabel, ylabel, xlim, ylim
from read_data import read_densmap
from save_data import save_figure
from util import construct_filename, parse_kwargs, reset_fields

def plot_density(system, frames, **kwargs):
    """Calls relevant functions to draw energy maps of supplied density maps.
    Options for cut_map and draw_density can be supplied as usual through 
    **kwargs.

    To output frame images to .png, **kwargs can be used to enter a base name 
    with save_to and dpi setting with dpi."""

    densmap = {}

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf], 
            'save_to' : None, 'dpi' : 200}
    parse_kwargs(opts, kwargs)

    find_normalising_factor(system, frames)

    clf()

    for frame in frames:
        densmap['filename'] = construct_filename(system['densbase'], frame)
        read_densmap(densmap)

        cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, **opts)
        normalise_density(densmap, system)
        draw_density(densmap, system, **kwargs)

        if opts['save_to'] != None:
            save_figure(opts['save_to'], frame, opts['dpi'])
        elif frame < frames[-1]:
            figure()

    return None

def find_normalising_factor(system, frames):
    """Find the maximum mass in a cell in all frames of the system,
    use this to later normalise the system. Saves to system['max_mass'].
    If value already present, ignore."""

    densmap = {}

    if 'max_mass' in system.keys() and system['max_mass'] > 0.0:
        return None

    system['max_mass'] = 0.0

    for frame in frames:
        densmap['filename'] = construct_filename(system['densbase'], frame)
        read_densmap(densmap, print = False)
        system['max_mass'] = max(system['max_mass'], max(densmap['M']))

    return None

def normalise_density(densmap, system):
    """Uses system['max_mass'] to normalise masses in cells, saving normalised
    mass values to densmap['dens_norm']."""
    
    reset_fields(densmap, {'dens_norm'})
    for mass in densmap['M']:
        densmap['dens_norm'].append(mass / system['max_mass'])

    return None

def draw_density(densmap, system, **kwargs):
    """Draws the energy array E corresponding to cell positions X and Y in 
    a figure using a weighted 2d histogram and data for number of bins. 
    Normally caps colormap for normalised density values between 0 and 1, this 
    can be modified by supplying different vmin and vmax as kwargs, disabling
    by using None. 
    
    Supplying minimum and maximum masses to show can be done similarly as 
    mmin and mmax, these are normalised by system['max_mass']. Other **kwargs
    as for hist2d."""

    opts = {'colormap' : True, 'mmin' : -inf, 'mmax' : inf, 
            'vmin' : 0.0, 'vmax' : 1.0}
    parse_kwargs(opts, kwargs)

    opts['mmin'] /= system['max_mass']
    opts['mmax'] /= system['max_mass']

    hist2d(densmap['X'], densmap['Y'], weights = densmap['dens_norm'], 
            bins = system['numcells'], vmin = opts['vmin'], vmax = opts['vmax'],
            cmin = opts['mmin'], cmax = opts['mmax'], **kwargs)
    axis('scaled');

    title('Density of droplet on substrate.')
    xlabel('Position (nm)')
    ylabel('Height (nm)')
    
    if opts['colormap']:
        colorbar()

    return None
