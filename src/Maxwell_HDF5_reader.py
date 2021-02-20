import h5py
import xml.etree.ElementTree as ET
import numpy as np
from natsort import natsorted


class XdmfReader:
    """
    Reads in .xdmf file for TFLink Maxwell outputs.

    Uses XML Element Trees to navigate xdmf files.

    Stores dimensions and time steps.
    """
    def __init__(self, filename):
        self.filename = filename
        self.dims = None
        self.times = None

    def read_xdmf(self):
        # Create XML Parser object
        parser = ET.XMLParser()
        tree = ET.parse(self.filename, parser)

        # Root of XML object
        root = tree.getroot()

        # Unwrap one level
        domains = list(root)
        domain = domains[0]

        # Unwrap two levels
        # grids contains each "field" element
        # init_grid retrieves "Dimensions" from the first grid (FRCR Reference Grid)
        # and stores the values into self.dims
        grids = list(domain)[0]
        init_grid = grids[0][0].attrib
        self.dims = tuple(int(i) for i in init_grid.get('Dimensions').split())

        # iterates through grid elements and collects time stamps
        self.times = []
        for g in grids:
            elements = list(g)[2].attrib
            self.times.append(float(elements.get('Value')))


class Frame:
    """
    Stores individual HDF5 frames.
    Electric, Magnetic, Source arrays
    Dimensions, frame number, frame time from xdmf file
    """
    def __init__(self, frame_num, e, b, j, dims, time):
        self.E = Field(e, dims)
        self.B = Field(b, dims)
        self.J = Field(j, dims)
        self.dims = dims
        self.frame_num = frame_num
        self.time = time


class Field:
    """
    Field components reshaped into correct dimensions.
    """
    def __init__(self, array, dims):
        self.x_component = array[0, :].reshape(dims)
        self.y_component = array[1, :].reshape(dims)
        self.z_component = array[2, :].reshape(dims)


class HDF5_Maxwell:
    """
    Reads and stores frames and xdmf files for TFLink Maxwell HDF5 outputs.
    """
    def __init__(self, path):
        self.frames = []
        self.xdmf = None
        self.paths = [path + 'maxwell.hdf5', path + 'maxwell.xdmf']

    def read_hdf5(self):
        # First read in XDMF file to get Dimensions and Time stamps
        self.xdmf = XdmfReader(self.paths[1])
        self.xdmf.read_xdmf()

        # Open HDF5 file in read only
        f = h5py.File(self.paths[0], 'r')
        # Unwrap dataset
        dset = f['H5fio']

        # Get list of frame keys (eg. 'frame_1', 'frame_2', ...) in ascending order
        # without "natsorted" the frames are ordered 'frame_1', 'frame_11', 'frame_2', 'frame_21'... so forth
        frame_keys = natsorted(list(dset.keys()))

        # Loop over every frame, create/save Frame object
        # E, B, and J come in shape (n, 3) with (x, y, z) elements
        # transpose makes it easier to seperate components later.
        for i, frame in enumerate(frame_keys):
            e = np.array(dset[frame]['B']).T
            b = np.array(dset[frame]['E']).T
            j = np.array(dset[frame]['J']).T
            self.frames.append(Frame(i, e, b, j, self.xdmf.dims, self.xdmf.times[i]))


def easy_read(path='data/'):
    """
    Creates object, reads files, returns object

    So you don't have to write it all yourself
    """
    maxwell_fields = HDF5_Maxwell(path)
    maxwell_fields.read_hdf5()
    return maxwell_fields

