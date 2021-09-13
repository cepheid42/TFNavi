import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from NaviBaseClasses import *
import os


def make_mp4():
    os.system("ffmpeg -framerate 24 -r 24 -i ./outputs/images/anim_%d.png -vf format=yuv420p output.mp4")


class AnimatedSubplot:
    """
    Animated Subplot class.

    Methods:
        __init__(self, *plots, nrows, ncols)
        __del__(self)
        _create_anim(self, nrows, ncols)
        update(self)

    Parameters:
        plots:     List of LinePlot/ContourPlot objects to be animated.
        nrows:     Number of subplot rows. Default is 1.
        ncols:     Number of subplot columns. Default is 1.
        fig_title: Title for whole plot figure.
    """
    def __init__(self, *plots, nrows=1, ncols=1, fig_title=None, save=False):
        self.plots = list(plots)
        self.nplots = len(plots)
        self.fig = None
        self.fig_title = fig_title
        self.frame_number = 0
        self.fig_text_ptr = None
        self.ylims = [(0.0, 0.0) for _ in range(self.nplots)]

        self.save_anim = save

        self._create_anim(nrows, ncols)

    def __del__(self):
        plt.show(block=True)

    def _create_anim(self, nrows, ncols):
        plt.ion()

        self.fig = plt.figure(tight_layout=True)

        # If subplot indices are not unique, ignores all given indices.
        indices = {self.plots[x].ind for x in range(self.nplots)}
        use_indices = True if len(indices) == self.nplots else False

        # Add title if given
        if self.fig_title is None:
            self.fig_text_ptr = self.fig.suptitle('Frame 0')
        else:
            self.fig_text_ptr = self.fig.suptitle(self.fig_title)

        for i in range(self.nplots):
            cur_plot = self.plots[i]
            # Checks if indices are usable, updates index if not
            if use_indices:
                pos_ind = cur_plot.ind
            else:
                pos_ind = i + 1
                cur_plot.set_index(pos_ind)

            # Add suplot to figure
            ax = self.fig.add_subplot(nrows, ncols, pos_ind)

            # Set labels on current subplot axes
            ax.set_xlabel(cur_plot.xlabel)
            ax.set_ylabel(cur_plot.ylabel)
            ax.set_title(cur_plot.title)

            # Initial plots for creating the figure
            # LinePlot
            if isinstance(cur_plot, LinePlot):
                # Plot each stacked line in the LinePlot
                for j in range(len(cur_plot.ydata)):
                    ax.plot(cur_plot.xdata, cur_plot.ydata[j], label=cur_plot.labels[j])

                if cur_plot.init_ylims is not None:
                    # Define manual ylimits at start
                    bot, top = cur_plot.init_ylims
                    ax.set_ylim(bottom=bot, top=top)
                else:
                    # set y-limits small enough for magnetic fields
                    ax.set_ylim(bottom=-1e-6, top=1e-6)

                self.ylims[i] = ax.get_ylim()
                ax.legend()

            # ContourPlot
            elif isinstance(cur_plot, ContourPlot):
                ax.set_aspect(aspect=1)
                ax.contourf(cur_plot.xdata, cur_plot.ydata, cur_plot.zdata, cmap=cur_plot.cmap, levels=cur_plot.levels)

            else:
                raise Exception('Invalid Plotting Class.')

        if self.save_anim:
            self.fig.savefig(f'./outputs/images/anim_{self.frame_number}.png')

    def update(self):
        """
        Updates subplots.
        """

        for i, ax in enumerate(self.fig.axes):
            cur_plot = self.plots[i]
            ymax = 0
            ymin = 0
            if isinstance(cur_plot, LinePlot):
                for line, ydata in zip(ax.get_lines(), cur_plot.ydata):
                    ymin = min(ymin, np.amin(ydata))
                    ymax = max(ymax, np.amax(ydata))

                    line.set_ydata(ydata)

                if cur_plot.hold_yscale:
                    ymin = self.ylims[i][0] # if ymin >= self.ylims[i][0] else 1.1 * ymin
                    ymax = self.ylims[i][1] # if ymax <= self.ylims[i][1] else 1.1 * ymax

                    self.ylims[i] = ax.set_ylim([ymin, ymax])
                else:
                    ax.relim()
                    ax.autoscale()

            elif isinstance(cur_plot, ContourPlot):
                ax.set_title(cur_plot.title)
                # clear current axes
                ax.cla()
                # replot contour
                ax.contourf(cur_plot.xdata, cur_plot.ydata, cur_plot.zdata, cmap=cur_plot.cmap, levels=cur_plot.levels)

        self.frame_number += 1
        self.fig_text_ptr.set_text(f'Frame {self.frame_number}')

        plt.pause(0.08)

        if self.save_anim:
            self.fig.savefig(f'./outputs/images/anim_{self.frame_number}.png')


