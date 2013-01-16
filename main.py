"""Contains tools for main tasks on flow maps."""

from util import construct_filename, parse_kwargs
from modify_maps import cut_map, calc_energy
from read_data import read_densmap, read_flowmap
from draw import draw_flowmap, draw_energy
from pylab import figure, hold, savefig, clf
from rows import keep_droplet_cells_in_system
from numpy import inf

def plot_flowmaps(system, frames, save_to = None, **kwargs):
    """Draws quiver plots of flow maps for specified frames. If no system
    supplied as input, or information lacking, asks user for file to 
    read from. By supplying options as for cut_maps in **kwargs the system
    can be cut before outputting. If so a density map has to be supplied for
    reconfiguration to succeed.
    
    To output frame images to .png, enter a base name string for save_to."""

    flowmap = {}

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf]}
    parse_kwargs(opts, kwargs)

    for frame in frames:
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_flowmap(flowmap)
        
        cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, **opts)

        keep_droplet_cells_in_system(flowmap, system)

        if save_to == None:
            figure()
        else:
            clf()
            hold(False)
            save_to_frame = construct_filename(save_to, frame, ext = '.png')

        draw_flowmap(flowmap, system, **kwargs)

        if save_to != None:
            savefig(save_to_frame)

    return None

def plot_energy_maps(system, frames, save_to = None, **kwargs):
    """Calls relevant functions to draw energy maps of supplied density maps.
    Options for cut_map and hist2d can be supplied as usual through **kwargs.

    To output frame images to .png, enter a base name for save_to."""

    densmap = {}

    opts = {'cutw' : [-inf, inf], 'cuth' : [-inf, inf]}
    parse_kwargs(opts, kwargs)

    for frame in frames:
        densmap['filename'] = construct_filename(system['densbase'], frame)
        read_densmap(densmap)

        cut_map(densmap, {'X', 'Y', 'N', 'T', 'M'}, system, **opts)

        calc_energy(densmap)

        if save_to == None:
            figure()
        else:
            clf()
            hold(False)
            save_to_frame = construct_filename(save_to, frame, ext = '.png')

        draw_energy(densmap, system, **kwargs)

        if save_to != None:
            savefig(save_to_frame)

    return None
