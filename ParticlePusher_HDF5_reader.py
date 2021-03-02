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
        self.num_particles = None
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
        # init_grid retrieves "NumberOfElements" from the first grid
        # and stores the values into self.dims
        grids = list(domain)[0]
        init_grid = grids[0][1].attrib
        self.num_particles = int(init_grid.get('NumberOfElements'))

        # iterates through grid elements and collects time stamps
        self.times = []
        for g in grids:
            elements = list(g)[0].attrib
            self.times.append(float(elements.get('Value')))


class Frame:
    """
    Stores individual HDF5 frames
    Frame number and Particle numbers
    List of Charges, Locations, masses, and velocities
    """
    def __init__(self, frame_num,  q, loc, mass, vel, num_particles, time):
        self.frame_num = frame_num
        self.n_particles = num_particles
        self.time = time

        self.charges = q
        self.masses = mass
        self.locations = loc
        self.velocities = vel


class HDF5_Particle:
    """
    Reads and stores frames and xdmf files for TFLink ParticlePusher HDF5 outputs.
    """
    def __init__(self, path):
        self.frames = []
        self.xdmf = None
        self.paths = [path + 'ParticlePusher.hdf5', path + 'ParticlePusher.xdmf']

    def read_hdf5(self):
        # Read the xdmf file to get the number of particles and time stamps
        self.xdmf = XdmfReader(self.paths[1])
        self.xdmf.read_xdmf()

        # Open HDF5 file in read only
        f = h5py.File(self.paths[0], 'r')
        # Unwrap dataset
        dset = f['H5pio']
        # Get list of frame keys (eg. 'frame_1', 'frame_2', ...) in ascending order
        # without "natsorted" the frames are ordered 'frame_1', 'frame_11', 'frame_2', 'frame_21'... so forth
        frame_keys = natsorted(list(dset.keys()))

        # Loop over every frame, create/save Frame object
        # Collect arrays and store them as a Frame object
        for i, frame in enumerate(frame_keys):
            q = np.array(dset[frame]['charge'])
            loc = np.array(dset[frame]['location'])
            mass = np.array(dset[frame]['mass'])
            vel = np.array(dset[frame]['velocity'])
            self.frames.append(Frame(i, q, loc, mass, vel, self.xdmf.num_particles, self.xdmf.times[i]))


def easy_read(path='data/'):
    """
    Creates object, reads files, returns object

    So you don't have to write it all yourself
    """
    particle_push = HDF5_Particle(path)
    particle_push.read_hdf5()
    return particle_push
