import numpy as np
import h5py
from vispy import scene
from .axis_aligned_image import AxisAlignedImage

def volume_slices_hdf5(hdf5_file, dataset_name, x_pos=None, y_pos=None, z_pos=None,
                       preproc_funcs=None,
                       cmaps='grays', clims=None,
                       interpolation='spline36', method='auto'):
    """ Acquire a list of slices from an HDF5 file in the form of AxisAlignedImage.
    The list can be attached to a SeismicCanvas to visualize the volume
    in 3D interactively.
    
    Parameters:
    - hdf5_file: path to the HDF5 file
    - dataset_name: the name of the dataset within the HDF5 file
    """
    
    # Open the HDF5 file
    with h5py.File(hdf5_file, 'r') as f:
        dataset = f[dataset_name]
        shape = dataset.shape
        
        # Configure cache for chunks if necessary (optional)
        f.id.get_access_plist().set_chunk_cache(1024*1024*64, 521, 0.75)
        
        # Check whether single volume or multiple volumes are provided
        if isinstance(dataset, (tuple, list)):
            n_vol = len(dataset)
            if preproc_funcs is None:
                preproc_funcs = [None] * n_vol # repeat n times ...
            else:
                assert isinstance(preproc_funcs, (tuple, list)) \
                    and len(preproc_funcs) >= n_vol
            assert isinstance(cmaps, (tuple, list)) \
                and len(cmaps) >= n_vol
            assert isinstance(clims, (tuple, list)) \
                and len(clims >= n_vol) \
                and len(clims[0]) == 2 or clims[0] is None
        else:
            dataset = [dataset]
            preproc_funcs = [preproc_funcs]
            cmaps = [cmaps]
            clims = [clims]
            n_vol = 1

        slices_list = []
        
        # Automatically set clim (cmap range) if not specified
        for i_vol in range(n_vol):
            clim = clims[i_vol]
            vol = dataset
            if clim is None or clim == 'auto':
                clims[i_vol] = (vol[:].min(), vol[:].max())  # Access entire dataset min/max

        # Function that returns the limitation of slice movement
        def limit(axis):
            if axis == 'x': return (0, shape[0]-1)
            elif axis == 'y': return (0, shape[1]-1)
            elif axis == 'z': return (0, shape[2]-1)

        # Function that returns a function to provide the slice image at specified position
        def get_image_func(axis, i_vol):
            def slicing_at_axis(pos, get_shape=False):
                pos = int(np.round(pos))
                if get_shape:  # return the shape information
                    if axis == 'x': return shape[1], shape[2]
                    elif axis == 'y': return shape[0], shape[2]
                    elif axis == 'z': return shape[0], shape[1]
                else:
                    # Apply flip to x and y axes only, leave z as it is
                    if axis == 'x': 
                        return dataset[pos, :, :][::-1, ::-1]  # Flip both x and y
                    elif axis == 'y': 
                        return dataset[:, pos, :][::-1, ::-1]  # Flip both x and y
                    elif axis == 'z': 
                        return dataset[:, :, pos]  # No flip for z-axis slices
            return slicing_at_axis

        # Organize the slice positions
        for xyz_pos in (x_pos, y_pos, z_pos):
            if not (isinstance(xyz_pos, (list, tuple, int, float)) or xyz_pos is None):
                raise ValueError(f'Wrong type of x_pos/y_pos/z_pos={xyz_pos}')
        axis_slices = {'x': x_pos, 'y': y_pos, 'z': z_pos}

        # Create AxisAlignedImage nodes and append to slices_list
        for axis, pos_list in axis_slices.items():
            if pos_list is not None:
                if isinstance(pos_list, (int, float)):
                    pos_list = [pos_list]  # make it iterable
                for pos in pos_list:
                    pos = int(np.round(pos))
                    if axis in ('y', 'z'):  # Adjust position for y and z axes
                        pos = limit(axis)[1] - pos
                    image_funcs = []
                    for i_vol in range(n_vol):
                        image_funcs.append(get_image_func(axis, i_vol))
                    image_node = AxisAlignedImage(image_funcs,
                        axis=axis, pos=pos, limit=limit(axis),
                        cmaps=cmaps, clims=clims,
                        interpolation=interpolation, method=method)
                    slices_list.append(image_node)

    return slices_list
