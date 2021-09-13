import numpy as np

import shutil
import os


def reset_output_dirs(path):
    shutil.rmtree(path)
    os.makedirs(path)


def load_field_npy(path):
    store = []

    if os.path.isdir(path):
        n_files = sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path))
    else:
        raise Exception('load_npy(): Not a valid path.')

    for n in range(n_files):
        filename = path + f'/{path[-2:]}_{n}.npy'

        try:
            temp = np.load(filename)
            store.append(temp)
        except IOError:
            print(f'Cannot read file "{filename}", continuing.')
            continue

    return store


def load_field_csv(path, shape=None):
    store = []

    if os.path.isdir(path):
        n_files = sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path))
    else:
        raise Exception('load_csv(): Not a valid path.')

    for n in range(n_files):
        filename = path + f'/{path[-2:]}_{n}.csv'

        temp = np.genfromtxt(filename, delimiter=',')
        store.append(temp.reshape(shape))

    return store
