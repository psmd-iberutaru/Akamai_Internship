import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid


def zeroedColorMap(cmap,min_val,max_val,name='shiftedcmap'):
    """Adapts :py:func:`~.shiftedColorMap` such that it is centered at zero.
    
    This function is a thin wrapper around the previous function such that
    the midpoint is automatically set to zero.

    Parameters
    ----------
    cmap : The matplotlib colormap to be altered
    start : Offset from lowest point in the colormap's range.
        Defaults to 0.0 (no lower offset). Should be between
        0.0 and `midpoint`.
        should be set to  1 - 5/(5 + 15)) or 0.75
    stop : Offset from highest point in the colormap's range.
        Defaults to 1.0 (no upper offset). Should be between
        `midpoint` and 1.0.

    Returns
    -------
    newcmap : The new matplotlib colormap.
    """

    # Use the formula from the previous documentation.
    midpoint = 1 - np.divide(max_val, max_val + np.abs(min_val), 
                            out=np.full_like(max_val,0.5), 
                            where=((max_val + np.abs(min_val)) != 0))
    
    # This section finally assumes that it is only being used for the 
    # polarization functions, and should only be of last resort.
    if (not(0 <= midpoint <= 1)):
        if ((min_val <= 0) and (max_val <= 0)):
            midpoint = 1
        elif ((min_val >= 0) and (max_val >= 0)):
            midpoint = 0
        else:
            midpoint = 0.5

    newcmap = shiftedColorMap(cmap, midpoint=midpoint, name=name)

    return newcmap


def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    """Modifies the scaling and zero point of Colormap

    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero.

    Adapted from: https://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib


    Parameters
    ----------
    cmap : The matplotlib colormap to be altered
    start : Offset from lowest point in the colormap's range.
        Defaults to 0.0 (no lower offset). Should be between
        0.0 and `midpoint`.
    midpoint : The new center of the colormap. Defaults to 
        0.5 (no shift). Should be between 0.0 and 1.0. In
        general, this should be  1 - vmax / (vmax + abs(vmin))
        For example if your data range from -15.0 to +5.0 and
        you want the center of the colormap at 0.0, `midpoint`
        should be set to  1 - 5/(5 + 15)) or 0.75
    stop : Offset from highest point in the colormap's range.
        Defaults to 1.0 (no upper offset). Should be between
        `midpoint` and 1.0.

    Returns
    -------
    newcmap : The new matplotlib colormap.
    """
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])
    
    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = mpl.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap