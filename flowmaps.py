from modify_maps import cut_map
from pylab import axis, clf, figure, quiver
from read_data import read_flowmap
from save_data import save_figure
from rows import keep_droplet_cells_in_system
from util import construct_filename, parse_kwargs

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

    clf()

    for frame in frames:
        flowmap['filename'] = construct_filename(system['flowbase'], frame)
        read_flowmap(flowmap)
        
        cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, **opts)
        keep_droplet_cells_in_system(flowmap, system)
        draw_flowmap(flowmap, system, **kwargs)

        if save_to != None:
            save_figure(save_to_base, frame)
        else:
            figure()

    return None

def draw_flowmap(flowmap, system, **kwargs):
    """Draws a flow map as a quiver plot. Plot options can be supplied 
    using **kwargs."""

    quiver(flowmap['X'], flowmap['Y'], flowmap['U'], flowmap['V'], **kwargs)
    axis('equal')

    return None
