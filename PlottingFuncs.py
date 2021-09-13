import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, LinearSegmentedColormap

import os.path

from NaviBaseClasses import *


def rgb_to_dec(value):
    """ value size 3, return list of size 3 """
    return [v / 256 for v in value]


def get_continuous_cmap(rgb_file):
    rgb_data = np.loadtxt(rgb_file, skiprows=2)
    rgb_list = [rgb_to_dec(i) for i in rgb_data]

    float_list = list(np.linspace(0, 1, len(rgb_list)))
    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list

    cmp = LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)
    return cmp


cmp_fname = os.path.dirname(os.path.realpath(__file__)) + '/hot_desaturated.gp'
cm_hot_desaturated = get_continuous_cmap(cmp_fname)


def plot_lines(line_obj, fig, pos=(1, 1, 1)):
    """
    Plotting method for histograms.

    Parameters:
        line_obj: LinePlot object containing data to plot.
        fig: matplotlib figure object to put subplots into.
        pos: positional arguments for subplot. Default is (1, 1, 1)

    Return:
        fig: returns updated figure object
    """
    ax = fig.add_subplot(*pos)

    # set subplot params
    # ax.set_title(line_obj.title)
    ax.set_xlabel(line_obj.xlabel)
    ax.set_ylabel(line_obj.ylabel)

    # Plot all hist_objects
    for i in range(len(line_obj.ydata)):
        if line_obj.xdata is None:
            ax.plot(line_obj.ydata[i], label=line_obj.labels[i])
        else:
            ax.plot(line_obj.xdata, line_obj.ydata[i], label=line_obj.labels[i])

    if line_obj.xdata is not None:
        ax.set_xlim(line_obj.xdata[0], line_obj.xdata[-1])

    ax.legend()
    return fig


def plot_histogram(hist_obj, fig, pos=(1, 1, 1)):
    """
    Plotting method for histograms.

    Parameters:
        hist_obj: HistPlot object containing data to plot.
        fig: matplotlib figure object to put subplots into.
        pos: positional arguments for subplot. Default is (1, 1, 1)

    Return:
        fig: returns updated figure object
    """
    ax = fig.add_subplot(*pos)

    # set subplot params
    ax.set_title(hist_obj.title)
    ax.set_xlabel(hist_obj.xlabel)
    ax.set_ylabel(hist_obj.ylabel)

    # Plot all hist_objects
    for i in range(len(hist_obj.ydata)):
        for j in range(hist_obj.ydata[i].shape[1]):
            ax.hist(hist_obj.ydata[i][:, j], label=hist_obj.labels[i])

    ax.legend()
    return fig


def plot_contour(cont_obj, fig, pos=(1, 1, 1)):
    ax = fig.add_subplot(*pos)

    # set subplot params
    ax.set_title(cont_obj.title, fontsize=24)
    ax.set_xlabel(cont_obj.xlabel, fontsize=24)
    ax.set_ylabel(cont_obj.ylabel, fontsize=24)
    ax.tick_params(labelsize=20)

    im = ax.contourf(cont_obj.xdata, cont_obj.ydata, cont_obj.zdata,
                     cmap=cont_obj.cmap, vmin=cont_obj.vmin, vmax=cont_obj.vmax, levels=cont_obj.levels)

    cb = fig.colorbar(im, ax=ax)
    cb.ax.tick_params(labelsize=12)

    return fig


def make_subplots(*args, nrows=1, ncols=1, fig_title=None, figsize=None, save_fig=False, save_name=None):
    """
    Creates and displays subplot containing histograms.

    Parameters:
        *args:     Arbitrary number of HistPlot/LinePlot/ContourPlot objects.
        nrows:     Number of subplot rows.
        ncols:     Number of subplot columns.
        fig_title: Title for whole plot figure.
        figsize:   Tuple for size of figure.
        save_fig:  Boolean. Save figure. Default is False
        save_name: Filename to save figure as. Default is 'Figure1.png'
    Usage:
        Single Plot:
            make_subplots(plot1)

        Multiple Subplots:
            make_subplots(plot1, plot2, ..., plotN, nrows=nrows, ncols=ncols, figsize=(9, 5))

    """

    num_plots = len(args)

    # If subplot indices are not unique, ignores all given indices.
    indices = {args[x].ind for x in range(num_plots)}
    use_indices = True if len(indices) == num_plots else False

    # Checks figsize argument for correctness
    if figsize is not None and isinstance(figsize, tuple):
        fig = plt.figure(figsize=figsize, tight_layout=True)
    else:
        fig = plt.figure(tight_layout=True)

    # Add title if given
    if fig_title is not None:
        fig.suptitle(fig_title)

    # Iterate over plots and call appropriate functions
    for i in range(num_plots):
        # Checks if indices are usable, updates index if not
        if use_indices:
            pos_ind = args[i].ind
        else:
            pos_ind = i + 1
            args[i].set_index(pos_ind)

        position = (nrows, ncols, pos_ind)

        if isinstance(args[i], LinePlot):
            # Line Plots
            fig = plot_lines(args[i], fig, pos=position)
        elif isinstance(args[i], HistPlot):
            # Histograms
            fig = plot_histogram(args[i], fig, pos=position)
        elif isinstance(args[i], ContourPlot):
            # Contour Plots
            fig = plot_contour(args[i], fig, pos=position)
        else:
            raise Exception('Invalid Plotting Class.')

    # Save figure to current directory
    if save_fig:
        filename = save_name if save_name is not None else 'Figure1.png'
        plt.savefig(filename)

    plt.show()


def animate_contour(xdata=None, ydata=None, zdata=None, times=None, timescale='s', title='', xlabel='', ylabel='',
                    cmap=cm_hot_desaturated, zlims=None, levels=100, save=False, filename=None):
    nt = len(zdata)

    if xdata is None:
        m = zdata[0].shape[1]
        xdata = [i for i in range(m)]
    if ydata is None:
        n = zdata[0].shape[0]
        ydata = [j for j in range(n)]

    vmin = zlims[0] if zlims is not None else np.min(zdata)
    vmax = zlims[1] if zlims is not None else np.max(zdata)

    norm = Normalize(vmin=vmin, vmax=vmax)

    if times is None:
        title_str = title + f'\n0/{nt}'
    else:
        title_str = title + f'\n{times[0]:4.3f}{timescale}'

    fig, ax = plt.subplots(1, 1)

    fig_title = ax.set_title(title_str)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    cax = make_axes_locatable(ax).append_axes('right', '5%', '5%')

    im = ax.contourf(xdata, ydata, zdata[0], cmap=cmap, levels=levels, norm=norm)

    if zlims is not None:
        fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax)

    def animate(i):
        if zlims is None:
            im = ax.contourf(xdata, ydata, zdata[i], cmap=cmap, levels=levels)
            cax.clear()
            fig.colorbar(im, cax=cax)
        else:
            im = ax.contourf(xdata, ydata, zdata[i], cmap=cmap, levels=levels, norm=norm)

        if times is None:
            title_str = title + f'\n{i}/{nt}'
        else:
            title_str = title + f'\n{times[i]:4.3f}{timescale}'

        fig_title.set_text(title_str)
        return im,

    anim = FuncAnimation(fig, animate, frames=len(zdata), interval=100, blit=False)

    if save:
        anim.save(filename, writer='ffmpeg')
        print(f'Animation saved as {filename}.')
    else:
        plt.show()


def animate_line(arrs, title='', xlabel='', ylabel='', ylims=None, save=False, filename=None):
    nt = len(arrs)

    fig, ax = plt.subplots(1, 1)

    title = ax.set_title(f'Frame 0 / {nt}')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if ylims is not None:
        ax.set_ylim(ylims[0], ylims[1])

    line, = ax.plot(arrs[0])

    def animate(i):
        line.set_ydata(arrs[i])

        title.set_text(f'Frame {i} / {nt}')
        return line,

    anim = FuncAnimation(fig, animate, frames=len(arrs), interval=100, blit=False)

    if save:
        anim.save(filename, writer='ffmpeg')
        print(f'Animation saved as {filename}.')
    else:
        plt.show()
