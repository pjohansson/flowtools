from modify_maps import cut_map
from pylab import axis, clf, colorbar, figure, hist2d
from read_data import read_densmap
from save_data import save_figure
from util import construct_filename, parse_kwargs, reset_fields

BOLTZ = 8.6173E-5 # eV / K 

def plot_energy_maps(system, frames, save_to = None, **kwargs):
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
        calc_energy(densmap)
        draw_energy(densmap, system, **kwargs)

        if save_to != None:
            save_figure(save_to_base, frame)
        else:
            figure()

    return None

def draw_energy(densmap, system, Emin = 1, **kwargs):
    """Draws the energy array E corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum energy as Emin 
    (default is 1)."""

    opts = {'colorbar' : True}
    parse_kwargs(opts, kwargs)

    hist2d(densmap['X'], densmap['Y'], weights = densmap['E'], 
            bins = system['numcells'], cmin = Emin, **kwargs)
    axis('equal')
    
    if opts['colorbar']:
        colorbar()

    return None

def calc_energy(densmap):
    """Calculates the kinetic energy in cells from the temperature, stores
    in dict with keyword 'E'."""

    reset_fields(densmap, {'E'})

    for temp, numatoms in zip(densmap['T'], densmap['N']):
        energy = 2 * BOLTZ * numatoms * temp
        densmap['E'].append(energy)

    return None
