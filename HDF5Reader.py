import os
import h5py
import xml.etree.ElementTree as ET
import numpy as np


class HDF5Reader:
    """
    Class for reading data from HDF5 and XDMF files. Will automatically find both HDF5 and XDMF files.

    Methods:
        __init__(self, path_to_file)
        check_paths(self, path_to_file)
        load_field_xdmf(self)
        load_particle_xdmf(self)
        load_hdf5(self)
        load_particle_hdf5(self, file)
        load_field_hdf5(self, file)

    Parameters:
        path_to_file: String containing relative or absolute path to hdf5/xdmf file
    """
    def __init__(self, path_to_file):
        # Common Data
        self.xdmf_path = None
        self.hdf5_path = None
        self.file_type = None
        self.check_paths(path_to_file)

        self.times = []
        self.frames = []
        self.nFrames = 0

        # Particle XDMF Data
        self.nParticles = None

        # Field XDMF Data
        self.dims = None
        self.origin = None
        self.dxdydz = None

        self.load_hdf5()

    def __iter__(self):
        return iter(self.frames)

    def check_paths(self, path_to_file):
        prefix, ext = os.path.splitext(path_to_file)

        if ext == '.hdf5':
            # If passed hdf5 path, build xdmf path
            path_to_hdf5 = path_to_file
            path_to_xdmf = prefix + '.xdmf'
        elif ext == '.xdmf':
            # If passed xdmf path, build hdf5 path
            path_to_hdf5 = prefix + '.hdf5'
            path_to_xdmf = path_to_file
        else:
            # Not xdmf or hdf5
            raise Exception(f'HDF5Reader.check_path(): Invalid file extension "{ext}".')

        # Check hdf5 path exists
        if not os.path.isfile(path_to_hdf5):
            raise Exception(f'HDF5Reader.check_path(): Invalid HDF5 file path. "{path_to_hdf5}"')
        # Check xdmf path exists
        if not os.path.isfile(path_to_xdmf):
            raise Exception(f'HDF5Reader.check_path(): Invalid XDMF file path. "{path_to_xdmf}"')

        if prefix[-1] == 'f' or prefix[-1] == 'p' or prefix[-1] == 'c':
            self.file_type = prefix[-1]
        else:
            raise Exception(f'HDF5Reader.check_path(): Invalid File Type suffix {prefix[-1]}. Should be "f/p/c".')

        self.xdmf_path = path_to_xdmf
        self.hdf5_path = path_to_hdf5

    def load_field_xdmf(self):
        tree = ET.parse(self.xdmf_path)
        root = tree.getroot()
        domain = list(root)[0]
        grids = list(domain)[0]
        ref_grid = grids[0]
        topo = list(ref_grid)[0]
        # Get dimensions for grids
        self.dims = tuple(int(dim) for dim in topo.attrib['Dimensions'].split())[::-1]
        geom = list(ref_grid)[1]
        origin = list(geom)[0]
        # Get origin as tuple (x, y, z)
        self.origin = tuple(float(orig) for orig in origin.text.split()[::-1])
        steps = list(geom)[1]
        # Get step sizes as tuple (dx, dy, dz)
        self.dxdydz = tuple(float(dl) for dl in steps.text.split()[::-1])
        # Get frame times
        for g in grids:
            self.times.append(float(list(g)[2].attrib['Value']))

    def load_particle_xdmf(self):
        tree = ET.parse(self.xdmf_path)
        root = tree.getroot()
        domain = list(root)[0]
        grids = list(domain)[0]

        ref_grid = list(grids)[0]

        topo = list(ref_grid)[1]
        self.nParticles = int(topo.attrib['NumberOfElements'])

        for g in grids:
            self.times.append(float(list(g)[0].attrib['Value']))

    def load_hdf5(self):
        file = h5py.File(self.hdf5_path, 'r')

        if self.file_type == 'f':
            print('Loading HDF5 Field files.')
            self.load_field_hdf5(file)
            print('Done.')
        elif self.file_type == 'p':
            print('Loading HDF5 Field files...')
            self.load_particle_hdf5(file)
            print('Done.')
        elif self.file_type == 'c':
            print('Loading HDF5 Chaining files...')
            self.load_chain_hdf5(file)
            print('Done.')
        else:
            raise Exception('HDF5Reader.load_hdf5(): File does not contain "H5pio" or "H5fio" tags at top level.')

    def load_field_hdf5(self, file):
        self.load_field_xdmf()

        data = file['H5fio_3DRectMesh']
        frame_keys = list(data.keys())

        self.nFrames = len(frame_keys)

        for i, frame in enumerate(frame_keys):
            self.frames.append(FieldFrame(frame=data[frame],
                                          dims=self.dims,
                                          time=self.times[i],
                                          frame_num=i))

    def load_particle_hdf5(self, file):
        self.load_particle_xdmf()

        data = file['H5pio']
        frame_keys = list(data.keys())

        self.nFrames = len(frame_keys)

        for i, frame in enumerate(frame_keys):
            self.frames.append(ParticleFrame(frame=data[frame],
                                             num_active=data[frame].attrs['nParticles_active'][0],
                                             time=self.times[i],
                                             frame_num=i))

    def load_chain_hdf5(self, file):
        self.load_field_xdmf()

        data = file['H5fio_3DRectMesh']
        frame_keys = list(data.keys())

        self.nFrames = len(frame_keys)
        self.dims = (self.dims[0] - 1, self.dims[1] - 1, self.dims[2] - 1)

        for i, frame in enumerate(frame_keys):
            self.frames.append(ChainFrame(frame=data[frame],
                                          dims=self.dims,
                                          time=self.times[i],
                                          frame_num=i))


class ParticleFrame:
    def __init__(self, frame, num_active, time, frame_num):
        self.charge = np.asarray(frame['charge'])
        self.mass = np.asarray(frame['mass'])

        self.location = np.asarray(frame['location'])
        self.velocity = np.asarray(frame['velocity'])

        self.spid = np.asarray(frame['spid'])

        self.particles_active = num_active
        self.time = time
        self.frame_num = frame_num


class FieldFrame:
    def __init__(self, frame, dims, time, frame_num):
        e_field = np.asarray(frame['E'])
        b_field = np.asarray(frame['B'])
        j_field = np.asarray(frame['J'])
        reshape_dims = dims[::-1]

        # Assuming X and Z are swapped
        self.Ex = e_field[:, 0].reshape(reshape_dims).T
        self.Ey = e_field[:, 1].reshape(reshape_dims).T
        self.Ez = e_field[:, 2].reshape(reshape_dims).T

        self.Bx = b_field[:, 0].reshape(reshape_dims).T
        self.By = b_field[:, 1].reshape(reshape_dims).T
        self.Bz = b_field[:, 2].reshape(reshape_dims).T

        self.Jx = j_field[:, 0].reshape(reshape_dims).T
        self.Jy = j_field[:, 1].reshape(reshape_dims).T
        self.Jz = j_field[:, 2].reshape(reshape_dims).T

        self.time = time
        self.dims = dims
        self.frame_num = frame_num


class ChainFrame:
    def __init__(self, frame, dims, time, frame_num):
        reshape_dims = dims[::-1]
        self.Cu_nDensity    = np.asarray(frame['Cu.nDensity']).reshape(reshape_dims).T
        self.Cu_temperature = np.asarray(frame['Cu.temperature']).reshape(reshape_dims).T
        self.e_nDensity    = np.asarray(frame['e.nDensity']).reshape(reshape_dims).T
        self.e_temperature = np.asarray(frame['e.temperature']).reshape(reshape_dims).T

        self.dims = dims
        self.time = time
        self.frame_num = frame_num
