import matplotlib
# matplotlib.use('Qt5Agg')

from NaviAnimationClass import *


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
    # ax.set_title(temp_obj.title)
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
    ax.set_title(cont_obj.title)
    ax.set_xlabel(cont_obj.xlabel)
    ax.set_ylabel(cont_obj.ylabel)

    im = ax.contourf(cont_obj.xdata, cont_obj.ydata, cont_obj.zdata,
                     cmap=cont_obj.cmap, vmin=cont_obj.vmin, vmax=cont_obj.vmax, levels=cont_obj.levels)

    fig.colorbar(im, ax=ax)
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


def main():
    # xx = np.linspace(0, 4, 100)
    #
    # line1 = np.zeros(100)
    # line2 = np.zeros(100)
    #
    # line4 = np.zeros(100)
    # line5 = np.zeros(100)
    #
    # line7 = np.zeros(100)
    # line8 = np.zeros(100)
    #
    # labels1 = ['Line 1', 'Line 2']
    # labels2 = ['Line 4', 'Line 5']
    # labels3 = ['Line 7', 'Line 8']
    #
    # l1 = LinePlot(ydata=[line1, line2], labels=labels1, xlabel='X', ylabel='Y')
    # l2 = LinePlot(ydata=[line4, line5], labels=labels2, xlabel='X', ylabel='Y')
    # l3 = LinePlot(ydata=[line7, line8], labels=labels3, xlabel='X', ylabel='Y')
    #
    # cont1 = np.zeros((100, 100))
    # cont2 = np.zeros((100, 100))
    # cont3 = np.zeros((100, 100))
    # X, Y = np.meshgrid(xx, xx)
    #
    # c1 = ContourPlot(zdata=cont1)
    # c2 = ContourPlot(zdata=cont2)
    # c3 = ContourPlot(zdata=cont3)
    #
    # # make_subplots(l1, l2, c1, c2, l3, c3, nrows=3, ncols=2)
    # anim1 = AnimatedSubplot(l1, l2, l3, nrows=3, ncols=1)
    # anim2 = AnimatedSubplot(c1, c2, c3, nrows=1, ncols=3)
    #
    # for n in range(300):
    #     line1[:] = np.sin(2 * np.pi * (xx - 0.01 * n))
    #     line2[:] = np.cos(2 * np.pi * (xx - 0.01 * n))
    #
    #     line4[:] = np.sin(-2 * np.pi * (xx - 0.01 * n))
    #     line5[:] = np.cos(2 * np.pi * (xx - 0.01 * n))
    #
    #     line7[:] = np.exp(-4 * (xx - 0.01 * n)**2)
    #     line8[:] = np.exp(-4 * (2 * xx - 0.01 * n)**2)
    #
    #     for i in range(X.shape[1]):
    #         cont1[:, i] = np.sin(2 * np.pi * (X[:, i] - 0.01 * n))
    #         cont2[i, :] = np.cos(2 * np.pi * (X[:, i] - 0.01 * n))
    #         cont3[:, i] = -np.sin(2 * np.pi * (X[:, i] - 0.01 * n))
    #
    #     if n % 5 == 0:
    #         anim1.update()
    #         anim2.update()

    """ Create some random temperature and velocity data """
    nsteps = 100

    etemp = np.zeros(nsteps)
    Htemp = np.zeros(nsteps)
    Ctemp = np.full(nsteps, 3500)
    Otemp = np.full(nsteps, 8000)

    Ven = np.zeros(nsteps)
    VHn = np.zeros(nsteps)
    VCn = np.zeros(nsteps)
    VOn = np.zeros(nsteps)

    ve3 = np.zeros((nsteps, 3))
    vh3 = np.zeros((nsteps, 3))
    vo3 = np.zeros((nsteps, 3))
    vc3 = np.zeros((nsteps, 3))

    Tps = np.zeros(nsteps)

    # create some arbitrary data for plotting
    for n in range(nsteps):
        Tps[n] = n

        # random temperatures
        etemp[n] = (n + np.random.randint(-5, 5)) ** 2

        # random velocity magnitudes
        Ven[n] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        VHn[n] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        VCn[n] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        VOn[n] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2

        # random velocity components for histograms
        ve3[n, 0] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vh3[n, 0] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vc3[n, 0] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vo3[n, 0] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2

        ve3[n, 1] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vh3[n, 1] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vc3[n, 1] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vo3[n, 1] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2

        ve3[n, 2] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vh3[n, 2] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vc3[n, 2] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2
        vo3[n, 2] = (n + np.random.randint(-5, 5)) ** 2 / nsteps ** 2


    ''' create line objects containing temp and |v| data '''
    temp1_labels = ['$T_e$', '$T_H$', '$T_C$', '$T_O$']
    temp1 = LinePlot(xdata=Tps, ydata=[etemp / 11601, Htemp / 11601, Ctemp / 11601, Otemp / 11601], labels=temp1_labels,
                     ind=1, xlabel='time [ps]', ylabel='temperature [eV]')

    temp2 = LinePlot(ydata=etemp)

    vel_labels = ['$v_e$', '$v_H$', '$v_C$', '$v_O$']
    vels = LinePlot(xdata=Tps, ydata=[Ven, VHn, VCn, VOn], labels=vel_labels, ind=2, xlabel='time [ps]',
                    ylabel='|v| [m/s]')

    # Creates a single subplot
    make_subplots(temp2)
    # Creates multiple subplots
    make_subplots(temp1, vels, fig_title='Temps and Velocities', nrows=1, ncols=2)


    ''' create histogram objects with velocity components '''
    hist1_labels = ['$v_{x,e}$', '$v_{y,e}$', '$v_{z,e}$']
    hist1 = HistPlot(ve3, hist1_labels, ind=1, title='Electrons', xlabel='veloctiy [m/s]', ylabel='particle count')

    hist2_labels = ['$v_{x,H}$', '$v_{y,H}$', '$v_{z,H}$']
    hist2 = HistPlot(vh3, hist2_labels, ind=2, title='Hydrogen', xlabel='veloctiy [m/s]', ylabel='particle count')

    hist3_labels = ['$v_{x,C}$', '$v_{y,C}$', '$v_{z,C}$']
    hist3 = HistPlot(vc3, hist3_labels, ind=3, title='Carbon', xlabel='veloctiy [m/s]', ylabel='particle count')

    hist4_labels = ['$v_{x,O}$', '$v_{y,O}$', '$v_{z,O}$']
    hist4 = HistPlot(vo3, hist4_labels, ind=4, title='Oxygen', xlabel='veloctiy [m/s]', ylabel='particle count')

    # Create a single subplot
    make_subplots(hist1)
    # Create multiple subplots
    make_subplots(hist1, hist2, hist3, hist4, fig_title="Histograms", nrows=2, ncols=2)


    ''' Create generic 2D data for contour plots'''
    ex_field = np.zeros((100, 100))
    ey_field = np.zeros((100, 100))
    ez_field = np.zeros((100, 100))

    xx = np.linspace(0, 1, 100)
    yy = np.linspace(0, 1, 100)

    X, Y = np.meshgrid(xx, yy)

    for row in range(100):
        ex_field[row, :] = (row / 100) ** 2
        ey_field[:, row] = (row / 100) ** 2
        ez_field[:, row] = (row / 100) ** 2

    ''' Create ContourPlot Objects'''
    # Creat ContourPlot objects
    ex_cont = ContourPlot(zdata=ex_field)
    ey_cont = ContourPlot(zdata=ey_field)
    ez_cont = ContourPlot(zdata=ez_field)

    # More complex ContourPlot objects
    ex_cont1 = ContourPlot(xdata=X, ydata=Y, zdata=ex_field,
                           ind=1, title='Ex Field', xlabel='Y', ylabel='Z')

    ey_cont1 = ContourPlot(zdata=ey_field,
                           ind=3, title='Ey Field', xlabel='X', ylabel='Z',
                           cmap='copper', vmin=0.5, vmax=1.0)

    ez_cont1 = ContourPlot(xdata=X, ydata=Y, zdata=ez_field,
                           ind=2, title='Ez Field', xlabel='X', ylabel='Y',
                           cmap='hsv', vmin=-1.0, vmax=1.0, levels=10)

    # Single contour plot
    make_subplots(ex_cont)
    # Make multiple plots
    make_subplots(ex_cont, ey_cont, ez_cont, nrows=1, ncols=3)

    # Single contour plot
    make_subplots(ex_cont1)
    # Multiple contour plots
    make_subplots(ex_cont1, ey_cont1, ez_cont1, fig_title='The whole shebang!', nrows=2, ncols=2)

    # Mix and Match
    make_subplots(ex_cont1, hist1, hist2, temp1, vels, ez_cont, nrows=2, ncols=3, save_fig=True)


if __name__ == '__main__':
    main()
