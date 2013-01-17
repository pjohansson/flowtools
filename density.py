from cut_system import cut_map
from pylab import axis, clf, colorbar, figure, hist2d
from read_data import read_densmap
from save_data import save_figure
from util import construct_filename, parse_kwargs

def plot_density(system, frames, save_to = None, **kwargs):
    """Calls relevant functions to draw energy maps of supplied density maps.
    Options for cut_map and hist2d can be supplied as usual through **kwargs.

    To output frame images to .png, enter a base name for save_to."""

    densmap = {}

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf]}
    parse_kwargs(opts, kwargs)

    clf()

    for frame in frames:
        densmap['filename'] = construct_filename(system['densbase'], frame)
        read_densmap(densmap)

        cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, **opts)
        normalise_density(densmap)
        draw_energy(densmap, system, **kwargs)

        if save_to != None:
            save_figure(save_to_base, frame)
        else:
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
    """Draws the energy array E corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum energy as Emin 
    (default is 1)."""

    opts = {'colormap' : True}
    parse_kwargs(opts, kwargs)

    hist2d(densmap['X'], densmap['Y'], weights = densmap['dens_norm'], 
            bins = system['numcells'], **kwargs)
    axis('equal')
    
    if opts['colormap']:
        colorbar()

    return None
