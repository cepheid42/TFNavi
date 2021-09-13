import argparse
import time
# import matplotlib
# matplotlib.use('qt5agg')

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from HDF5Reader import *
from PlottingFuncs import cm_hot_desaturated


def init_argparse():
    """
    Creates argument parsing object.
    For more information about the argparse library see
    https://realpython.com/command-line-interfaces-python-argparse/#setting-the-name-or-flags-of-the-arguments
    """
    parser = argparse.ArgumentParser(usage='./%(prog)s [OPTIONS] [INPUT FILE]', description='Read .hdf5 files and update plots.')
    parser.add_argument('Path',           metavar='path', type=str,                help="Path to file to plot")
    # parser.add_argument('-o', '--output', action='store', type=str,                help='Output file name, Defaults to input filename with .gif added')
    # parser.add_argument('-s', '--sleep',  action='store', type=int,                help='How often to check for new files in directory in seconds')
    # parser.add_argument('--xlims',        action='store', type=float, nargs=2,     help='Plot X limits {lower upper}')
    # parser.add_argument('--ylims',        action='store', type=float, nargs=2,     help='Plot Y limits {lower upper}')
    # parser.add_argument('--zlims',        action='store', type=float, nargs=2,     help='Plot Z limits {lower upper}')
    # parser.add_argument('--gif',          action='store_true',                     help='Save animation as GIF')
    # parser.add_argument('--mp4',          action='store_true',                     help='Save animation as MP4')

    return parser


def get_xdmf_data(hdf5_path):
    xdmf_path = hdf5_path.split('.')[0] + '.xdmf'
    tree = ET.parse(xdmf_path)
    root = tree.getroot()
    domain = list(root)[0]
    grids = list(domain)[0]
    ref_grid = grids[0]
    topo = list(ref_grid)[0]
    # Get dimensions for grids
    dims = tuple(int(dim) for dim in topo.attrib['Dimensions'].split())
    times = float(list(grids[0])[2].attrib['Value'])
    return dims, times


def load_field_hdf5(hdf5_path):
    file = h5py.File(hdf5_path, 'r')
    data = file['H5fio']
    frame_key = list(data.keys())[0]
    frame = data[frame_key]

    e_field = np.asarray(frame['E'])
    b_field = np.asarray(frame['B'])
    # j_field = np.asarray(frame['J'])
    j_field = None

    return e_field, b_field, j_field


def main():
    the_parser = init_argparse()
    args = the_parser.parse_args()
    # convert to dict
    params = vars(args)

    # sleep_time = 1.0 if params['sleep'] is None else params['sleep']

    file_prefix = ''
    file_number = 0

    os.chdir(params['Path'])
    for file in os.listdir('.'):
        if file.endswith('.hdf5'):
            name = file.split('.')[0]
            file_prefix = name[:-4]
            file_number = int(name[-4:])
            if file_number > 1:
                file_number = 1
            break

    if file_prefix == '':
        raise Exception('Invalid filename.')

    # plt.ion()
    fig, axes = plt.subplots(2, 3, figsize=(12, 10), tight_layout=True)
    caxes = [make_axes_locatable(ax).append_axes('right', '5%', '5%') for ax in axes.flat]

    for ax, field in zip(axes.flat, ['Ex', 'Ey', 'Ez', 'Bx', 'By', 'Bz']):
        ax.set_title(field)
        ax.set_xlabel('z')
        ax.set_ylabel('x')

    # plt.show()

    visited = {file_number: file_prefix}

    bmin = -0.02
    bmax = 0.02

    emin = -600000
    emax = 600000

    bnorm = Normalize(vmin=bmin, vmax=bmax)
    bmap = ScalarMappable(norm=bnorm, cmap=cm_hot_desaturated)

    enorm = Normalize(vmin=emin, vmax=emax)
    emap = ScalarMappable(norm=enorm, cmap=cm_hot_desaturated)

#    fig.colorbar(emap, cax=caxes[0])
#    fig.colorbar(emap, cax=caxes[1])
#    fig.colorbar(emap, cax=caxes[2])
#    fig.colorbar(bmap, cax=caxes[3])
#    fig.colorbar(bmap, cax=caxes[4])
#    fig.colorbar(bmap, cax=caxes[5])

    while True:
        if file_number not in visited:
            cur_file = file_prefix + f'{file_number:04}.hdf5'
            if os.path.isfile(cur_file):
                dims, cur_time = get_xdmf_data(cur_file)

                fig.suptitle(f'{1e9 * cur_time:7.3f} ns @ y=0.0')

                E, B, J = load_field_hdf5(cur_file)

                Ex = E[:, 0].reshape(dims)[:, dims[1] // 2, :].T
                Ey = E[:, 1].reshape(dims)[:, dims[1] // 2, :].T
                Ez = E[:, 2].reshape(dims)[:, dims[1] // 2, :].T

                Bx = B[:, 0].reshape(dims)[:, dims[1] // 2, :].T
                By = B[:, 1].reshape(dims)[:, dims[1] // 2, :].T
                Bz = B[:, 2].reshape(dims)[:, dims[1] // 2, :].T

                # Jx = J[:, 0].reshape(dims)[:, dims[1] // 2, :]
                # Jy = J[:, 1].reshape(dims)[:, dims[1] // 2, :]
                # Jz = J[:, 2].reshape(dims)[:, dims[1] // 2, :]

                # Plot Electric Fields
                imEx = axes[0][0].contourf(Ex, cmap=cm_hot_desaturated, levels=100, vmin=emin, vmax=emax)
                imEy = axes[0][1].contourf(Ey, cmap=cm_hot_desaturated, levels=100, vmin=emin, vmax=emax)
                imEz = axes[0][2].contourf(Ez, cmap=cm_hot_desaturated, levels=100, vmin=emin, vmax=emax)

                # Plot Magnetic Fields
                imBx = axes[1][0].contourf(Bx, cmap=cm_hot_desaturated, levels=100, vmin=bmin, vmax=bmax)
                imBy = axes[1][1].contourf(By, cmap=cm_hot_desaturated, levels=100, vmin=bmin, vmax=bmax)
                imBz = axes[1][2].contourf(Bz, cmap=cm_hot_desaturated, levels=100, vmin=bmin, vmax=bmax)

                # # Plot Current Densities
                # imJx = axes[2][0].contourf(Jx, cmap=cm_hot_desaturated, levels=100)
                # fig.colorbar(imJx, cax=caxes[6])
                #
                # imJy = axes[2][1].contourf(Jy, cmap=cm_hot_desaturated, levels=100)
                # fig.colorbar(imJy, cax=caxes[7])
                #
                # imJz = axes[2][2].contourf(Jz, cmap=cm_hot_desaturated, levels=100)
                # fig.colorbar(imJz, cax=caxes[8])

                plt.pause(0.1)
                plt.savefig(f'/home/cepheid/Documents/TFLink/data/images/img_{file_number}.png')
                visited[file_number] = file_prefix

            else:
                time.sleep(1)
                continue

        else:
            file_number += 1
            continue


if __name__ == '__main__':
    main()
