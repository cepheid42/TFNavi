import numpy as np

import matplotlib
matplotlib.use('qt5agg')

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from TFNavi import HDF5Reader, cm_hot_desaturated


# Read in data
data = HDF5Reader('/home/cepheid/Documents/TFLink/tflink/data/pFRC_f.hdf5')

nx, ny, nz = data.dims
nt = data.nFrames

r = 0.045
xx = np.linspace(-0.125, 0.125, nx)
yy = np.linspace(-0.125, 0.125, ny)

# Slice data along z-axis
E_x = [data.frames[i].Ex[:, :, nz // 2] for i in range(data.nFrames)]
E_y = [data.frames[i].Ey[:, :, nz // 2] for i in range(data.nFrames)]

# B_x = [1e4 * data.frames[i].Bx[:, :, nz // 2] for i in range(20, data.nFrames)]
# B_y = [1e4 * data.frames[i].By[:, :, nz // 2] for i in range(20, data.nFrames)]

# get times
times = [1e9 * data.frames[i].time for i in range(data.nFrames)]

# zero out values outside of circle r=0.045
for n in range(nt):
    for ix in range(nx):
        for iy in range(ny):
            if xx[ix]**2 + yy[iy]**2 >= r**2:
                E_x[n][ix, iy] = 0.0
                E_y[n][ix, iy] = 0.0
#                 # B_x[n][ix, iy] = 0.0
#                 # B_y[n][ix, iy] = 0.0

# trim off excess data
E_x = [E_x[n][16:-16, 16:-16] for n in range(len(E_x))]
E_y = [E_y[n][16:-16, 16:-16] for n in range(len(E_y))]
# B_x = [B_x[n][16:-16, 16:-16] for n in range(len(B_x))]
# B_y = [B_y[n][16:-16, 16:-16] for n in range(len(B_y))]

xx = xx[16:-16]
yy = yy[16:-16]


def animate_quiver(Ex, Ey, nframes):
    # Plot circle over everything
    circle = plt.Circle((0, 0), r, fill=False, ls='--', lw=2, color='w', zorder=1)

    # calculate vector magnitudes for coloring
    M = [np.hypot(Ex[i], Ey[i]) for i in range(len(Ex))]

    # colorbar min/max values
    r_max = np.min(M)
    r_min = np.max(M)

    norm = Normalize(vmin=r_min, vmax=r_max)

    fig, ax = plt.subplots(1, 1)
    fig.colorbar(ScalarMappable(norm=norm, cmap=cm_hot_desaturated), label='V/m')

    ax.set_aspect('equal')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'$\\bf{{E}}_{{xy}}$ @ z=0.0m r=0.045m\n{times[0]:6.3f}ns')
    # make background dark blue color
    ax.set_facecolor('xkcd:midnight')
    # add circle to current plot/axes
    ax.add_artist(circle)

    # initial plot
    q = ax.quiver(xx, yy, Ex[0], Ey[0], M[0], scale=100, scale_units='dots', width=0.005, pivot='mid', minlength=2, cmap=cm_hot_desaturated, norm=norm, zorder=2)

    def animate(i):
        # clear previous plot data
        ax.cla()
        # plot current frame
        q = ax.quiver(xx, yy, Ex[i], Ey[i], M[i], scale=100, scale_units='dots', width=0.005, pivot='mid', minlength=2, cmap=cm_hot_desaturated, norm=norm, zorder=2)
        # re-add the circle
        ax.add_artist(circle)

        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title(f'$\\bf{{E}}_{{xy}}$ @ z=0.0m r=0.045m\n{times[i]:6.3f}ns')
        ax.set_facecolor('xkcd:midnight')
        return q,

    anim = FuncAnimation(fig, animate, frames=nframes, interval=100, blit=False)
    anim.save('e_vector_z0_new.mp4', writer='ffmpeg', fps=15)
    plt.show()

# Call function
animate_quiver(E_x, E_y, nt)
