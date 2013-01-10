"""Tools for visualisation of density and flow maps data."""

from pylab import hist2d

def draw_temperature(densmap, system, Tmin = 1, **kwargs):
    """Draws the temperature array T corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum temperature as cmin 
    (default is 1)."""

    hist2d(densmap['X'], densmap['Y'], weights = densmap['T'], 
            bins = system['numcells'], cmin = Tmin, **kwargs)

    return None
