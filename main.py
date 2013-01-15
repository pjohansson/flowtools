"""Contains tools for main tasks on flow maps."""

from util import construct_filename, parse_kwargs
from modify_maps import cut_map
from read_data import read_flowmap
from draw import draw_flowmap
from pylab import figure
from rows import keep_droplet_cells_in_system

def plot_flowmaps(system, frames, **kwargs):
    """Draws quiver plots of flow maps for specified frames. If no system
    supplied as input, or information lacking, asks user for file to 
    read from. By supplying options as for cut_maps in **kwargs the system
    can be cut before outputting. If so a density map has to be supplied for
    reconfiguration to succeed."""

    flowmap = {}

    opts = {'cutw' : None, 'cuth' : None}
    parse_kwargs(opts, kwargs)

    for frame in frames:
        construct_filename(flowmap, system['flowbase'], frame)
        read_flowmap(flowmap)
        
        if (opts['cutw'] or opts['cuth']) != None:
            cut_map(flowmap, {'X', 'Y', 'U', 'V'}, system, **kwargs)

        keep_droplet_cells_in_system(flowmap, system)

        figure()
        draw_flowmap(flowmap, system, **kwargs)
