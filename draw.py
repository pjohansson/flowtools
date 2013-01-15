"""Tools for visualisation of density and flow maps data."""

from pylab import hist2d, axis, quiver

def draw_temperature(densmap, system, Tmin = 1, **kwargs):
    """Draws the temperature array T corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum temperature as cmin 
    (default is 1)."""

    hist2d(densmap['X'], densmap['Y'], weights = densmap['T'], 
            bins = system['numcells'], cmin = Tmin, **kwargs)
    axis('equal')

    return None

def draw_energy(densmap, system, Emin = 1, **kwargs):
    """Draws the energy array E corresponding to cell positions
    X and Y in a figure using a weighted 2d histogram and data for number
    of bins. Can additionally be called with minimum energy as Emin 
    (default is 1)."""

    hist2d(densmap['X'], densmap['Y'], weights = densmap['E'], 
            bins = system['numcells'], cmin = Emin, **kwargs)
    axis('equal')

    return None

def draw_flowmap(flowmap, system, **kwargs):
    """Draws a flow map as a quiver plot. Plot options can be supplied 
    using **kwargs."""

    quiver(flowmap['X'], flowmap['Y'], flowmap['U'], flowmap['V'])
    axis('equal')

    return None
