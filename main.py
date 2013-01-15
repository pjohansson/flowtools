"""Contains tools for main tasks on flow maps."""

from util import construct_filename, parse_kwargs
from datamaps import read_flowmap, cut_map
from draw import draw_flowmap
from pylab import figure

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

        figure()
        draw_flowmap(flowmap, system, **kwargs)



def cut_non_droplet_cells(flowmap, system):
    """Remove all cells not part of droplet from flowmap."""

    for all rows:
        find_cells_in_row(row, flowmap, system):
        keep_droplet_cells_in_row(row, flowmap, system):
