from vispy_canvas import XYZAxis
from vispy_canvas import Colorbar
from vispy_canvas import SeismicCanvas
from vispy_canvas import volume_slices
import numpy as np
from vispy.scene import SceneCanvas

CANVAS_SIZE = (900, 900)  

data = np.load('train_seismic.npy')

nodes = volume_slices(data,x_pos=100, y_pos=128, z_pos=30,
    seismic_coord_system=False)

axis_scales = (1, 1, -1)

xyz_axis = XYZAxis(seismic_coord_system=False)

colorbar = Colorbar(cmap='grays', clim=(data.min(), data.max()),
                    label_str='Amplitude', label_size=8, tick_size=6)

# Run the canvas.
canvas = SeismicCanvas(title='Sísmica 3D',
                        visual_nodes=nodes,
                        axis_scales=axis_scales,
                        xyz_axis=xyz_axis,
                        colorbar=colorbar,
                        # Set the option below=0 will hide the colorbar region
                        # colorbar_region_ratio=0,
                        # Manual camera setting below.
                        # auto_range=False,
                        # scale_factor=972.794,
                        # center=(434.46, 545.63, 10.26),
                        fov=30,
                        elevation=36,
                        azimuth=45,
                        zoom_factor=1.2 # >1: zoom in; <1: zoom out
                        )
canvas.measure_fps()
canvas.app.run()






