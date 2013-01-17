"""Tools for visualisation of density and flow maps data."""

from pylab import colorbar, hist2d, axis, quiver
from util import parse_kwargs

def draw_temperature(densmap, system, Tmin = 1, **kwargs):
    """Draws the temperature array T corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum temperature as cmin 
    (default is 1)."""

    opts = {'colormap' : True}
    parse_kwargs(opts, kwargs)

    hist2d(densmap['X'], densmap['Y'], weights = densmap['T'], 
            bins = system['numcells'], cmin = Tmin, **kwargs)
    axis('equal')

    if opts['colormap']:
        colorbar()

    return None
