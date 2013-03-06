import pylab as plt

def draw(func):
    """Decorator for giving common plot options."""

    def wrapper(**kwargs):
        # Read options
        axis = kwargs.pop('axis', 'scaled')
        colorbar = kwargs.pop('colorbar', False)
        dpi = kwargs.pop('dpi', 150)
        fig = kwargs.pop('figure', False)
        legend = kwargs.pop('legend', False)
        save = kwargs.pop('save', '')
        show = kwargs.pop('show', False)
        xlim = kwargs.pop('xlim', None)
        ylim = kwargs.pop('ylim', None)

        # If new figure demanded
        if fig:
            plt.figure()

        # Labels
        plt.xlabel(kwargs.pop('xlabel', 'Position (nm)'))
        plt.ylabel(kwargs.pop('ylabel', 'Height (nm)'))
        plt.title(kwargs.pop('title', ''))

        # Drawing function called with remaining keywords
        func(**kwargs)

        # View
        plt.axis(axis)
        plt.xlim(xlim)
        plt.ylim(ylim)

        # Decorating options
        if legend:
            plt.legend()
        if colorbar:
            plt.colorbar()

        # Show
        if show:
            plt.show()

        # Save
        if save:
            plt.savefig(save, dpi = dpi)

    return wrapper
