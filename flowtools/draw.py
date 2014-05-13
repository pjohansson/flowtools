# Flowtools - a suite of tools for handling and drawing flow data
# Copyright (C) 2013 Petter Johansson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Functions for drawing images.

Functions:
    draw - a decorator for figures

"""

import pylab as plt

def draw(func):
    """Decorator for giving common plot options."""

    def wrapper(**kwargs):
        # Read options
        axis = kwargs.pop('axis', 'scaled')
        colorbar = kwargs.pop('colorbar', False)
        dpi = kwargs.pop('dpi', 150)
        fig = kwargs.pop('figure', False)
        invert_x = kwargs.pop('invert_x', False)
        invert_y = kwargs.pop('invert_y', False)
        legend = kwargs.pop('legend', False)
        save = kwargs.pop('save', '')
        show = kwargs.pop('show', False)
        transparent = kwargs.pop('transparent', False)
        xlim = kwargs.pop('xlim', None)
        ylim = kwargs.pop('ylim', None)

        # If new figure demanded
        if fig:
            plt.figure()

        # Labels
        plt.xlabel(kwargs.pop('xlabel', 'Time (ps)'))
        plt.ylabel(kwargs.pop('ylabel', 'Height (nm)'))
        plt.title(kwargs.pop('title', ''))

        # Drawing function called with remaining keywords
        func(**kwargs)

        # View
        plt.axis(axis)
        plt.xlim(xlim)
        plt.ylim(ylim)

        # Invert axises
        if invert_x:
            plt.gca().invert_xaxis()
        if invert_y:
            plt.gca().invert_yaxis()

        # Decorating options
        if legend:
            plt.legend()
        if colorbar:
            plt.colorbar()

        # Save
        if save:
            plt.savefig(save, dpi = dpi, transparent = transparent)

        # Show
        if show:
            plt.show()

        if save:
            plt.clf()

    return wrapper

@draw
def plot_line(**kwargs):
    """
    Plot a line, decorated by draw.

    Keywords:
        domain - domain of plot
        line - line

        Others as for draw and plot

        """

    domain = kwargs.pop('domain')
    line = kwargs.pop('line')

    plt.plot(domain, line, **kwargs)

    return None
