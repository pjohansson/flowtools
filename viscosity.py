"""Modules that work with viscosity and flow fields."""

def unmod_visc_flow(X, Y, U, V, data, filename_viscdata, 
        cut_height = [-1.0, -1.0]):
    """Uses data of viscosity increase close to a substrate to reverse the
    effect of it on a flowmap. Returns a one-dimensional array of the 
    viscosity-reversed flow divided by unmodified in every cell of the
    lowest layer of a spreading droplet.

    An optional vector of cut_height = [cut_min, cut_max] can be supplied
    to control the minimum layers and maximum layers to be included in the 
    calculation. If no maximum is given the function tries to find the 
    thinnest area and cut the calculation at that height. Setting these
    to -1.0 disables them."""

    # Find lowest (well-connected) row of droplet
    # Find how many rows to include in calculation
    # Calculate viscosity modification for every road from data file
    # Apply to every row, add, average
    # Divide by unmodified flow
    # Output

    return None
