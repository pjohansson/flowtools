"""Contains tools for main tasks on flow maps."""

from util import construct_filename

def plot_flowmaps(system, frames, **kwargs):
    """Draws quiver plots of flow maps for specified frames. If no system
    supplied as input, or information lacking, asks user for file to 
    read from. By supplying options as for cut_maps in **kwargs the system
    can be cut before outputting. If so a density map has to be supplied for
    reconfiguration to succeed."""
    flowmap = {}

    for frame in frames:
        construct_filename(flowmap, system['flowbase'], frame)
