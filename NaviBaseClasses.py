import numpy as np


class SubplotInfo:
    """
    Parent class that holds common info for subplots
    """
    def __init__(self, ind, title, xlabel, ylabel):
        self.ind = ind
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def set_index(self, new_index):
        self.ind = new_index


class HistPlot(SubplotInfo):
    """
    Histogram Plot class used for storing plotting data.

    Methods:
        __init__(self, ydata, labels, ind=1, title='', xlabel='', ylabel='')

    Parameters:
        ydata:   Data to be plotted. Must be shape (n, 3).
        labels:  Labels for legend. Must be length 3.
        ind:     Positional index in subplot. 1 <= ind <= number of subplots.
        title:   Subplot title. Default is none.
        xlabel:  Subplot x-axis label. Default is none.
        ylabel:  Subplot y-axis label. Default is none.
    """
    def __init__(self, ydata=None, labels=(), ind=1, title='', xlabel='', ylabel=''):
        super().__init__(ind=ind, title=title, xlabel=xlabel, ylabel=ylabel)

        self.ydata = ydata if isinstance(ydata, (list, tuple)) else [ydata]
        self.labels = labels if labels else [f'Hist {i}' for i in range(len(ydata))]


class LinePlot(SubplotInfo):
    """
    Histogram Plot class used for storing plotting data.

    Methods:
        __init__(self, ydata, labels, ind=1, title='', xlabel='', ylabel='')

    Parameters:
        ydata:   List of data to be plotted.
        labels:  Labels for legend.
        ind:     Positional index in subplot. 1 <= ind <= number of subplots.
        title:   Subplot title. Default is none.
        xlabel:  Subplot x-axis label. Default is none.
        ylabel:  Subplot y-axis label. Default is none.
    """
    def __init__(self, xdata=None, ydata=None, labels=(), ind=1, title='', xlabel='', ylabel='', hold_yscale=False, ylims=None):
        if ydata is None:
            raise Exception('No ydata supplied to LinePlot.')

        super().__init__(ind, title, xlabel, ylabel)

        if isinstance(ydata, (list, tuple)):
            self.ydata = ydata
        else:
            self.ydata = [ydata]

        if xdata is None:
            m = self.ydata[0].shape[0]
            self.xdata = [i for i in range(m)]
        else:
            self.xdata = xdata

        self.labels = labels if labels else [f'Line {i}' for i in range(len(ydata))]
        self.hold_yscale = hold_yscale
        self.init_ylims = ylims


class ContourPlot(SubplotInfo):
    """
    Contour Plot class used for storing plotting data.

    Methods:
        __init__(self, xdata, ydata, zdata, labels, ind=1, title='', xlabel='', ylabel='')

    Parameters:
        xdata:   Optional. Sets x-axis range
        ydata:   Optional. Sets y-axis range
        zdata:   List of data to be plotted.
        ind:     Positional index in subplot. 1 <= index <= number of subplots.
        title:   Subplot title. Default is none.
        xlabel:  Subplot x-axis label. Default is none.
        ylabel:  Subplot y-axis label. Default is none.
        cmap:    String defining colormap. Default is 'viridis'.
        vmin:    Set minimum color value.
        vmax:    Set maximum color value.
        levels:  Set number of color levels. Default is 100.
    """
    def __init__(self, xdata=None, ydata=None, zdata=None,
                 ind=1, title='', xlabel='', ylabel='',
                 cmap='viridis', vmin=None, vmax=None, levels=100):

        if zdata is None:
            raise Exception('No zdata supplied to ContourPlot.')

        super().__init__(ind, title, xlabel, ylabel)

        self.zdata = zdata
        if xdata is None:
            m = zdata.shape[1]
            self.xdata = [i for i in range(m)]
        else:
            self.xdata = xdata

        if ydata is None:
            n = zdata.shape[0]
            self.ydata = [j for j in range(n)]
        else:
            self.ydata = ydata

        self.cmap = cmap
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
